from typing import Annotated, Any, Literal

from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict

from agent_lab.llm import MODEL, client          # ← 不是 chat
from agent_lab.tools import get_schemas          # ← 不是 tools.base
from agent_lab.tools.executor import execute_tool

from agent_lab.agent import SYSTEM_PROMPT

def append(left: list[Any], right: list[Any]) -> list[Any]:
    return left + right

def tool_calls_of(m: Any) -> list:
    if isinstance(m, dict):
        return m.get("tool_calls") or []
    return getattr(m, "tool_calls", None) or []

class AgentState(TypedDict):
    messages: Annotated[list[Any], append]                      # 這裡塞的是 SDK 的 pydantic message，不是 dict


async def call_model(state: AgentState) -> dict:
    payload = with_system(state["messages"])      # 只補在送出的那份，不寫回 state
    resp = await client.chat.completions.create(
        model=MODEL, messages=payload, tools=get_schemas()
    )
    msg = resp.choices[0].message
    return {"messages": [msg.model_dump(exclude_none=True)]}


async def call_tools(state: AgentState) -> dict:
    last = state["messages"][-1]
    outputs = []
    for c in tool_calls_of(last):
        name = c["function"]["name"] if isinstance(c, dict) else c.function.name
        args = c["function"]["arguments"] if isinstance(c, dict) else c.function.arguments
        cid = c["id"] if isinstance(c, dict) else c.id
        result = await execute_tool(name, args)
        outputs.append({"role": "tool", "tool_call_id": cid, "content": result.content})
    return {"messages": outputs}


def with_system(messages: list[Any]) -> list[Any]:
    if messages and isinstance(messages[0], dict) and messages[0].get("role") == "system":
        return messages
    return [{"role": "system", "content": SYSTEM_PROMPT}, *messages]

def should_continue(state: AgentState) -> Literal["tools", END]:
    return "tools" if tool_calls_of(state["messages"][-1]) else END



g = StateGraph(AgentState)
g.add_node("model", call_model)
g.add_node("tools", call_tools)
g.set_entry_point("model")
g.add_conditional_edges("model", should_continue)
g.add_edge("tools", "model")

def build_app(checkpointer: Any = None):
    """編譯這張圖。checkpointer 由呼叫方提供 —— 它有生命週期，
    必須在 event loop 裡建立，不能在 import 時刻就寫死。"""
    return g.compile(checkpointer=checkpointer)

