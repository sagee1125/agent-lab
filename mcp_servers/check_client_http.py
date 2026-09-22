import asyncio

from fastmcp import Client

URL = "http://127.0.0.1:8000/mcp"


async def main() -> None:
    async with Client(URL) as c:
        tools = await c.list_tools()
        print("tools:", [t.name for t in tools])
        result = await c.call_tool("list_dir", {"path": "mcp_servers"})
        print(result.data)


asyncio.run(main())
