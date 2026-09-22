"""把雲端的 MCP server 掛進 agent，然後跑一輪。

    uv run python mcp_agent_demo.py

第一次會開瀏覽器要你授權（OAuth），之後 token 加密存在 ~/.agent-lab/oauth-tokens/，
第二次起就靜默通過。金鑰來自 .env 的 OAUTH_STORAGE_KEY（見 agent_lab.mcp_auth）。

注意：get_weather / get_exchange_rate / web_search 這三個工具原本是本地函式，
現在改由雲端的 MCP server 提供 —— 掛載時會取代掉內建版本。
"""

import asyncio

from fastmcp import Client

from agent_lab.agent import run_agent
from agent_lab.mcp_auth import make_oauth
from agent_lab.mcp_tools import mount
from agent_lab.tools import REGISTRY

REMOTE = "https://agent-lab-web.fastmcp.app/mcp"

QUESTION = "東京現在天氣如何？順便查一下 USD 對 CNY 的匯率，再告訴我 MCP 是什麼。"


async def main() -> None:
    async with Client(REMOTE, auth=make_oauth()) as remote:
        report = await mount(remote)
        print(f"掛載結果：{report}")
        print(f"  新增      ：{report.added}")
        print(f"  被取代    ：{report.replaced}")
        print(f"  REGISTRY 現在共 {len(REGISTRY)} 個工具")

        print()
        print(await run_agent(QUESTION))


asyncio.run(main())
