import asyncio
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from fastmcp import Client
from fastmcp.exceptions import ToolError

from fs_server import mcp


async def main() -> None:
    async with Client(mcp) as c:
        print("tools:", [t.name for t in await c.list_tools()])

        print("\n--- list_dir ---")
        print((await c.call_tool("list_dir", {})).data)

        print("\n--- write_file（會自動建上層目錄）---")
        print((await c.call_tool("write_file", {
            "path": "notes/deep/mcp-test.txt",
            "content": "hello from MCP\n第二行\n",
        })).data)

        print("\n--- read_file ---")
        print((await c.call_tool("read_file", {"path": "notes/deep/mcp-test.txt"})).data)

        print("\n--- search_content 'mcp' ---")
        print((await c.call_tool("search_content", {"keyword": "mcp"})).data)

        print("\n--- 檔案不存在（可回復 → 一般字串）---")
        r = await c.call_tool("read_file", {"path": "nope.txt"})
        print("is_error:", r.is_error, "|", r.data)

        print("\n--- 安全性：路徑穿越 ---")
        for bad in ["../pyproject.toml", "notes/../../pyproject.toml", ".."]:
            try:
                await c.call_tool("read_file", {"path": bad})
                print(f"  {bad!r:34} -> 沒有擋住！")
            except ToolError as e:
                print(f"  {bad!r:34} -> 已擋住")

        print("\n--- 安全性：敏感檔案 ---")
        try:
            await c.call_tool("read_file", {"path": ".env"})
            print("  .env -> 沒有擋住！")
        except ToolError:
            print("  .env -> 已擋住")


asyncio.run(main())
