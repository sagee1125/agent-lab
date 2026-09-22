from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel


@dataclass(frozen=True)
class Tool:
    """一個工具 = 名字 + 說明 + 輸入模型 + 執行函式。"""

    name: str
    description: str
    input_model: type[BaseModel]
    fn: Callable[[Any], Awaitable[str]]

    def openai_schema(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_model.model_json_schema(),
            },
        }
