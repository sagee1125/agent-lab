"""executor.execute_tool 的四道防線測試。

執行：uv run pytest -q
"""

import asyncio

import pytest
from pydantic import BaseModel

import agent_lab.tools.executor as executor
from agent_lab.tools import REGISTRY
from agent_lab.tools.base import Tool
from agent_lab.tools.executor import execute_tool


class NoInput(BaseModel):
    pass


async def _slow(_: NoInput) -> str:
    await asyncio.sleep(5)
    return "終於完成了"


async def _boom(_: NoInput) -> str:
    raise RuntimeError("模擬工具內部錯誤")


@pytest.fixture
def fast_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """把超時縮短成 0.2 秒，讓超時測試跑得快。"""
    monkeypatch.setattr(executor, "DEFAULT_TIMEOUT", 0.2)


@pytest.fixture
def demo_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    """暫時註冊兩個測試用工具；monkeypatch 會在測試結束後自動移除。"""
    monkeypatch.setitem(
        REGISTRY, "_slow_demo", Tool("_slow_demo", "測試用慢工具", NoInput, _slow)
    )
    monkeypatch.setitem(
        REGISTRY, "_boom_demo", Tool("_boom_demo", "測試用會拋錯的工具", NoInput, _boom)
    )


def test_unknown_tool() -> None:
    """防線 1：模型瞎編工具名。"""
    res = asyncio.run(execute_tool("get_wether", '{"city": "Tokyo"}'))
    assert res.ok is False
    assert res.error_type == "unknown_tool"
    assert "get_weather" in res.content  # 要告訴模型有哪些可用工具


def test_bad_arguments_json() -> None:
    """防線 2：參數不是合法 JSON。"""
    res = asyncio.run(execute_tool("get_weather", "{city: Tokyo}"))
    assert res.ok is False
    assert res.error_type == "bad_arguments_json"


def test_invalid_arguments() -> None:
    """防線 3：參數不符合 pydantic schema（缺 title）。"""
    res = asyncio.run(execute_tool("todo_add", '{"due": "2026-10-01"}'))
    assert res.ok is False
    assert res.error_type == "invalid_arguments"
    assert "title" in res.content  # 錯誤原文要能讓模型看懂並修正


def test_timeout(fast_timeout: None, demo_tools: None) -> None:
    """防線 4a：工具執行超時。"""
    res = asyncio.run(execute_tool("_slow_demo", "{}"))
    assert res.ok is False
    assert res.error_type == "execution_failed"
    assert "超時" in res.content


def test_internal_error(demo_tools: None) -> None:
    """防線 4b：工具內部拋出例外。"""
    res = asyncio.run(execute_tool("_boom_demo", "{}"))
    assert res.ok is False
    assert res.error_type == "execution_failed"
    assert "RuntimeError" in res.content


def test_success_control() -> None:
    """對照組：正常呼叫要成功。"""
    res = asyncio.run(
        execute_tool("get_exchange_rate", '{"base": "USD", "quote": "HKD"}')
    )
    assert res.ok is True
    assert res.error_type is None
