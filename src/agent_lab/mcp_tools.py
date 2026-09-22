"""把 MCP server 上的工具掛進 agent 的 REGISTRY。

MCP 的 tool 和 agent_lab 的 Tool 其實是同一個抽象：
    名字 + 說明 + 輸入 schema + 可呼叫物件

所以適配器本身很短 —— 真正要處理的只有兩件事：
  1. MCP 給的是 JSON Schema，不是 pydantic model
     → Tool(input_model=None, raw_schema=...)，驗證交給 server
  2. 同名工具誰優先
     → MCP 版本取代內建版本（工具搬到遠端之後，本地那份就該退場）
"""

from dataclasses import dataclass, field

from fastmcp import Client

from agent_lab.tools import REGISTRY
from agent_lab.tools.base import Tool


@dataclass
class MountReport:
    """掛載結果。新增和取代分開列，讓「覆蓋」這件事是看得見的。"""

    added: list[str] = field(default_factory=list)
    replaced: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        return f"新增 {len(self.added)} 個、取代 {len(self.replaced)} 個"


def _wrap(
    client: Client,
    mcp_name: str,
    registry_name: str,
    description: str,
    schema: dict,
) -> Tool:
    """把一個 MCP 工具包成 agent 的 Tool。

    fn 收到的是原始 dict（不是 pydantic model），因為 input_model=None 時
    executor 會跳過驗證 —— 驗證由擁有工具的 server 負責。
    """

    async def call(args: dict) -> str:
        result = await client.call_tool(mcp_name, args)
        return str(result.data)

    return Tool(registry_name, description, None, call, raw_schema=schema)


async def mount(client: Client, *, prefix: str = "") -> MountReport:
    """把 client 這個 MCP server 的工具全部掛進 REGISTRY，回傳掛載報告。

    prefix 用來避免不同 server 之間的命名衝突；同一份工具鏈不需要前綴。
    """
    report = MountReport()
    for t in await client.list_tools():
        registry_name = f"{prefix}{t.name}"
        if registry_name in REGISTRY:
            report.replaced.append(registry_name)
        else:
            report.added.append(registry_name)
        REGISTRY[registry_name] = _wrap(
            client,
            t.name,
            registry_name,
            t.description or "",
            t.input_schema,
        )
    return report
