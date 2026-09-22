import asyncio
from pathlib import Path

from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport

HERE = Path(__file__).resolve().parent
SERVER = HERE / "fs_server.py"
CHILD_LOG = HERE / "fs_server.log"


async def main() -> None:
    transport = PythonStdioTransport(str(SERVER), log_file=CHILD_LOG)
    async with Client(transport) as c:
        tools = await c.list_tools()
        print("這個 server 提供：")
        for t in tools:
            print(f"  - {t.name}: {t.description}")

        result = await c.call_tool("read_file", {"path": "pyproject.toml"})
        print("\n呼叫結果：")
        print(result.data[:200])


asyncio.run(main())

# import asyncio
# from pathlib import Path

# from fastmcp import Client

# HERE = Path(__file__).resolve().parent
# SERVER = HERE / "fs_server.py"
# ROOT = HERE.parent


# async def main() -> None:
#     client = Client(SERVER)
#     async with client:
#         tools = await client.list_tools()
#         print("這個 server 提供：")
#         for t in tools:
#             print(f"  - {t.name}: {t.description}")

#         result = await client.call_tool(
#             "read_file", {"path": str(ROOT / "pyproject.toml")}
#         )
#         print("\n呼叫結果：")
#         print(result)


# asyncio.run(main())


# import asyncio, sys
# sys.path.insert(0, "mcp_servers")
# from fs_server import mcp          # ← 直接 import server 物件
# from fastmcp import Client

# async def main():
#     async with Client(mcp) as c:   # ← 不傳 Path，傳物件 = 記憶體內
#         print(await c.list_tools())
#         print((await c.call_tool("read_file", {"path": "pyproject.toml"})).data[:60])

# asyncio.run(main())
