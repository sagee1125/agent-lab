from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel


@dataclass(frozen=True)
class Tool:
    """一個工具 = 名字 + 說明 + 輸入模型 + 執行函式。

    input_model 為 None 時，代表「輸入驗證交給工具自己負責」，此時要提供
    raw_schema —— 直接沿用對方給的 JSON Schema，原樣餵給 LLM。
    遠端工具（MCP）就是這種：server 自己會驗證，並用 tool error 回報。
    """

    name: str
    description: str
    input_model: type[BaseModel] | None
    fn: Callable[[Any], Awaitable[str]]
    raw_schema: dict[str, Any] | None = None

    def openai_schema(self) -> dict[str, Any]:
        if self.raw_schema is not None:
            parameters = self.raw_schema
        else:
            parameters = self.input_model.model_json_schema()  # type: ignore[union-attr]
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": parameters,
            },
        }
