import asyncio

from agent_lab.agent import run_agent


async def main() -> None:
    for q in [
        "東京現在天氣如何？",
        "100 美元換成港幣是多少？",
        "幫我查一下 LangGraph 是什麼",
        # "現在東京幾點？",
        # "幫我新增一筆待辦：複習 pydantic，到期 2026-09-20",
        # "幫我在 2026-10-01 加一個行程：團隊 review",
        # "列出我的待辦",
        # "2026-10-01 有什麼行程？",
    ]:
        print(f"\n[user]  {q}")
        print(f"[agent] {await run_agent(q)}")


if __name__ == "__main__":
    asyncio.run(main())
