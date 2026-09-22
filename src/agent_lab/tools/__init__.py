from agent_lab.tools.base import Tool
from agent_lab.tools.local import LOCAL_TOOLS
from agent_lab.tools.web import WEB_TOOLS

# 內建工具，只是 REGISTRY 的「起始內容」。
# 執行期可以再掛上遠端的 MCP 工具（見 agent_lab.mcp_tools）。
BUILTIN_TOOLS: list[Tool] = [*LOCAL_TOOLS, *WEB_TOOLS]

# 唯一的真相來源：工具存不存在看這裡，餵給 LLM 的清單也看這裡。
# 兩者若各自維護一份，動態註冊的工具就會「執行得到、但 LLM 看不到」。
REGISTRY: dict[str, Tool] = {t.name: t for t in BUILTIN_TOOLS}


def get_schemas() -> list[dict]:
    return [t.openai_schema() for t in REGISTRY.values()]
