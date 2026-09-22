import asyncio
import json
from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from agent_lab.tools import REGISTRY

DEFAULT_TIMEOUT = 15.0
MAX_ATTEMPTS = 3


@dataclass
class ToolResult:
    ok: bool
    content: str
    error_type: str | None = None


async def execute_tool(name: str, raw_args: str | None) -> ToolResult:
    # 防線 1：工具存在嗎？
    tool = REGISTRY.get(name)
    if tool is None:
        return ToolResult(
            ok=False,
            error_type="unknown_tool",
            content=f"錯誤：沒有名為「{name}」的工具。可用工具：{', '.join(REGISTRY)}。",
        )

    # 防線 2：參數是合法 JSON 嗎？
    try:
        args = json.loads(raw_args or "{}")
    except json.JSONDecodeError as e:
        return ToolResult(
            ok=False,
            error_type="bad_arguments_json",
            content=f"錯誤：參數不是合法 JSON（{e.msg}）。請重新產生正確的 JSON。",
        )

    # 防線 3：參數符合 schema 嗎？
    # input_model 為 None 代表驗證由工具自己負責（例如 MCP server），跳過這道。
    if tool.input_model is None:
        validated: Any = args
    else:
        try:
            validated = tool.input_model(**args)
        except ValidationError as e:
            return ToolResult(
                ok=False,
                error_type="invalid_arguments",
                content=f"錯誤：參數不合法，請依下列訊息修正後重試。\n{e}",
            )

    # 防線 4：執行（超時 + 重試 + 例外）
    last_error = ""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            result = await asyncio.wait_for(tool.fn(validated), timeout=DEFAULT_TIMEOUT)
            return ToolResult(ok=True, content=str(result))
        except TimeoutError:
            last_error = f"工具「{name}」執行超時（超過 {DEFAULT_TIMEOUT:.0f} 秒）。"
        # 這裡的 noqa 是刻意的：工具的例外型別無法預期 —— 本地工具、遠端 MCP 工具都可能拋
        # 任何東西。這個防線的職責就是「把任何失敗轉成給模型看的回饋」，所以必須
        # 攔 Exception。縮小範圍反而會讓未預期的例外直接炸穿 agent 迴圈。
        except Exception as e:  # noqa: BLE001
            last_error = f"工具「{name}」執行失敗：{type(e).__name__}: {e}"
        if attempt < MAX_ATTEMPTS:
            await asyncio.sleep(0.5 * attempt)  # 簡單退避

    return ToolResult(
        ok=False,
        error_type="execution_failed",
        content=f"{last_error}（已重試 {MAX_ATTEMPTS} 次）",
    )
