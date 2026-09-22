from agent_lab.tools.base import Tool
from agent_lab.tools.local import LOCAL_TOOLS
from agent_lab.tools.web import WEB_TOOLS

ALL_TOOLS: list[Tool] = [*LOCAL_TOOLS, *WEB_TOOLS]

REGISTRY: dict[str, Tool] = {t.name: t for t in ALL_TOOLS}


def get_schemas() -> list[dict]:
    return [t.openai_schema() for t in ALL_TOOLS]
