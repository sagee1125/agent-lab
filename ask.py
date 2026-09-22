import asyncio

from agent_lab.llm import chat


async def main() -> None:
    reply = await chat("用一句話說明什麼是 event loop")
    print(reply)


if __name__ == "__main__":
    asyncio.run(main())
