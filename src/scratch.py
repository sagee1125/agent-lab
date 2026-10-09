# import asyncio

# from agent_lab.agent import SYSTEM_PROMPT
# from agent_lab.graph import app

# CFG = {"configurable": {"thread_id": "demo-1"}, "recursion_limit": 25}


# def show(m) -> str:
#     if isinstance(m, dict):
#         calls = [c["function"]["name"] for c in (m.get("tool_calls") or [])]
#         return f"{m['role']:>9} | {str(m.get('content'))[:70]} | calls={calls}"
#     return f"{getattr(m, 'role', '?'):>9} | {str(getattr(m, 'content', None))[:70]}"


# async def main() -> None:
#     print("=== 第 1 輪：東京天氣 ===")
#     r1 = await app.ainvoke(
#         {"messages": [
#             {"role": "system", "content": SYSTEM_PROMPT},
#             {"role": "user", "content": "東京現在天氣如何？"},
#         ]},
#         CFG,
#     )
#     for m in r1["messages"]:
#         print(show(m))

#     print("=== 第 2 輪：只送新訊息，同一 thread ===")
#     r2 = await app.ainvoke({"messages": [{"role": "user", "content": "那濕度呢？"}]}, CFG)
#     for m in r2["messages"]:
#         print(show(m))
#     print("累積訊息數：", len(r2["messages"]), "| 型別：", {type(m).__name__ for m in r2["messages"]})

#     print("=== 第 3 輪：換一個 thread_id，應該沒有記憶 ===")
#     r3 = await app.ainvoke(
#         {"messages": [{"role": "user", "content": "那濕度呢？"}]},
#         {"configurable": {"thread_id": "demo-2"}, "recursion_limit": 25},
#     )
#     print("新 thread 的回答：", r3["messages"][-1]["content"])


# if __name__ == "__main__":        # ← 手打，別複製
#     asyncio.run(main())


from langgraph.checkpoint.memory import InMemorySaver
from agent_lab.graph import build_app

app = build_app(InMemorySaver())
