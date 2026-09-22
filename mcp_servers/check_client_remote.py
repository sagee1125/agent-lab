"""連到部署在 Prefect Horizon 上的 web_server，列出工具並各打一次。

    uv run python mcp_servers/check_client_remote.py

第一次跑會開瀏覽器要你授權；token 由 agent_lab.mcp_auth 加密存到磁碟，
之後就靜默通過。

（曾經用 KeyringStore 走 Windows 認證管理員，但單筆憑證上限 2560 bytes、
 keyring 又用 UTF-16 存 —— 等於只能放 1280 個字元，OAuth token 一定爆，
 會回 WinError 1783 CredWrite。詳見 src/agent_lab/mcp_auth.py。）
"""

import asyncio

from fastmcp import Client

from agent_lab.mcp_auth import make_oauth

URL = "https://agent-lab-web.fastmcp.app/mcp"


async def main() -> None:
    async with Client(URL, auth=make_oauth()) as c:
        tools = await c.list_tools()
        print("tools:", [t.name for t in tools])

        for name, args in [
            ("get_weather", {"city": "Tokyo"}),
            ("get_exchange_rate", {"base": "USD", "quote": "JPY"}),
            ("web_search", {"query": "Model Context Protocol"}),
        ]:
            r = await c.call_tool(name, args)
            print(f"[{name}] is_error={r.is_error}")
            print("   ", str(r.data).splitlines()[0][:100])


asyncio.run(main())
