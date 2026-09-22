import asyncio

from fastmcp import Client
from fastmcp.client.auth import OAuth
from key_value.aio.stores.keyring import KeyringStore

URL = "https://agent-lab-web.fastmcp.app/mcp"

# auth="oauth" 預設只把 token 存在記憶體，進程一結束就沒了 —— 每次跑都要重開瀏覽器授權。
# 傳一個 token_storage 才會持久化；KeyringStore 走 Windows 認證管理員（WinVaultKeyring），
# 由作業系統加密保存，不需要自己管金鑰。
oauth = OAuth(token_storage=KeyringStore(service_name="agent-lab"))


async def main() -> None:
    async with Client(URL, auth=oauth) as c:
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
