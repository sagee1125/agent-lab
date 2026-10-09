from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

# from agent_lab.graph import app as agent_graph

router = APIRouter(prefix="/chat", tags=["chat"])

RECURSION_LIMIT = 25


class ChatRequest(BaseModel):
    thread_id: str = Field(min_length=1, description="對話 ID；同一個 ID 共用同一段記憶")
    message: str = Field(min_length=1)


class ChatReply(BaseModel):
    thread_id: str
    reply: str
    message_count: int


@router.post("")
async def chat(req: ChatRequest, request: Request) -> ChatReply:
    agent_graph = request.app.state.agent_graph
    cfg = {"configurable": {"thread_id": req.thread_id}, "recursion_limit": RECURSION_LIMIT}
    result = await agent_graph.ainvoke(
        {"messages": [{"role": "user", "content": req.message}]}, cfg
    )
    return ChatReply(
        thread_id=req.thread_id,
        reply=result["messages"][-1]["content"] or "",
        message_count=len(result["messages"]),
    )
