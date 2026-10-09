"""人工審批（human-in-the-loop）示範：在工具執行「之前」停下來，等人批准。

為什麼這件事重要？
  1. 高風險工具（轉帳、刪檔、寄信）不能讓模型自己決定就執行，要人點頭。
  2. 那個「暫停」必須跨行程存活 —— 伺服器重啟、你隔天再回來批准，都要接得上。
     這就是 checkpoint 的第二個用途：斷點續跑。

用法（每一行都是獨立的行程，暫停狀態存在 checkpoints.db）：
    uv run python src/hitl_demo.py ask "東京現在天氣如何？"   # 送出問題，停在工具前
    uv run python src/hitl_demo.py status                     # 看停在哪、要批准什麼
    uv run python src/hitl_demo.py approve                    # 批准 → 執行工具 → 產出答案
    uv run python src/hitl_demo.py reject                     # 拒絕 → 把拒絕訊息餵回模型
    uv run python src/hitl_demo.py history                    # 看 checkpoint 歷史

註：這裡直接拿 graph.py 裡的圖定義 g 自己編譯，因為 interrupt_before 是「編譯選項」——
    同一張圖，換一個執行模式而已。
"""

import argparse
import asyncio
from pathlib import Path
from typing import Any

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from agent_lab.graph import g

DB_PATH = Path(__file__).resolve().parents[1] / "checkpoints.db"
DEFAULT_THREAD = "hitl-1"


def tool_calls_of(m: Any) -> list:
    if isinstance(m, dict):
        return m.get("tool_calls") or []
    return getattr(m, "tool_calls", None) or []


def cfg_of(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}, "recursion_limit": 25}


async def show_status(graph: Any, cfg: dict) -> bool:
    """印出暫停狀態。回傳 True 表示有東西在等批准。"""
    snap = await graph.aget_state(cfg)
    if not snap.next:
        print("沒有暫停中的任務。")
        return False
    print(f"暫停在節點：{snap.next}")
    print(f"目前累積 {len(snap.values['messages'])} 則訊息，等待批准的工具呼叫：")
    for c in tool_calls_of(snap.values["messages"][-1]):
        fn = c["function"]
        print(f"  - {fn['name']}({fn['arguments']})")
    return True


async def resume_and_report(graph: Any, cfg: dict) -> None:
    result = await graph.ainvoke(None, cfg)
    snap = await graph.aget_state(cfg)
    if snap.next:
        print("\n又停在工具前了（模型還想呼叫別的工具），再 approve 一次即可。")
        await show_status(graph, cfg)
    else:
        print("\n" + (result["messages"][-1]["content"] or ""))
        print(f"\n[完成，累積 {len(result['messages'])} 則訊息]")


async def main() -> None:
    parser = argparse.ArgumentParser(description="人工審批示範")
    parser.add_argument("action", choices=["ask", "status", "approve", "reject", "history"])
    parser.add_argument("message", nargs="?", default="東京現在天氣如何？")
    parser.add_argument("--thread", default=DEFAULT_THREAD, help="thread_id（預設 hitl-1）")
    args = parser.parse_args()

    cfg = cfg_of(args.thread)

    async with AsyncSqliteSaver.from_conn_string(str(DB_PATH)) as saver:
        graph = g.compile(checkpointer=saver, interrupt_before=["tools"])

        if args.action == "ask":
            result = await graph.ainvoke(
                {"messages": [{"role": "user", "content": args.message}]}, cfg
            )
            print(f"送出：{args.message}")
            print(f"（模型已回應，訊息數 {len(result['messages'])}）")
            await show_status(graph, cfg)

        elif args.action == "status":
            await show_status(graph, cfg)

        elif args.action == "approve":
            snap = await graph.aget_state(cfg)
            if not snap.next:
                print("沒有暫停中的任務，不需要批准。")
                return
            print("批准 → 續跑")
            await resume_and_report(graph, cfg)

        elif args.action == "reject":
            snap = await graph.aget_state(cfg)
            if not snap.next:
                print("沒有暫停中的任務，沒東西可拒絕。")
                return
            rejects = [
                {
                    "role": "tool",
                    "tool_call_id": c["id"],
                    "content": "使用者拒絕了這次工具呼叫。請直接說明你沒有取得授權，不要重試。",
                }
                for c in tool_calls_of(snap.values["messages"][-1])
            ]
            await graph.aupdate_state(cfg, {"messages": rejects}, as_node="tools")
            print(f"已拒絕 {len(rejects)} 個工具呼叫（把拒絕訊息當成工具結果寫回 state）")
            await resume_and_report(graph, cfg)

        elif args.action == "history":
            async for s in graph.aget_state_history(cfg):
                print(f"  next={s.next or ('（完成）',)}  訊息數={len(s.values['messages'])}")


if __name__ == "__main__":
    asyncio.run(main())
