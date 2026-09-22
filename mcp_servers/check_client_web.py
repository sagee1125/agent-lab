import asyncio

from fastmcp import Client

URL = "http://127.0.0.1:8001/mcp"


async def main() -> None:
    async with Client(URL) as c:
        tools = await c.list_tools()
        print("tools:", [t.name for t in tools])
        print("--------------------------------")
        calls: dict[str, dict] = {
            "get_weather": {"city": "Tokyo"},
            "get_exchange_rate": {"base": "USD", "quote": "JPY"},
            "web_search": {"query": "MCP protocol"},
        }
        for tool in tools:
            if tool.name in calls:
                print(f"{tool.name}: {tool.description}")
                result = await c.call_tool(tool.name, calls[tool.name])
                print(f"{tool.name}: {result.data}")


asyncio.run(main())
