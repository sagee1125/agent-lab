from contextlib import asynccontextmanager
from pathlib import Path

import truststore
from fastapi import FastAPI
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from agent_lab.errors import register_exception_handlers
from agent_lab.graph import build_app
from agent_lab.routers import chat, health, rates, todos

truststore.inject_into_ssl()

DB_PATH = Path(__file__).resolve().parents[2] / "checkpoints.db"


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncSqliteSaver.from_conn_string(str(DB_PATH)) as saver:
        app.state.agent_graph = build_app(saver)
        yield


app = FastAPI(title="agent-lab", version="0.1.0", lifespan=lifespan)

register_exception_handlers(app)
app.include_router(health.router)
app.include_router(todos.router)
app.include_router(rates.router)
app.include_router(chat.router)
