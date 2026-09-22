import truststore
from fastapi import FastAPI

from agent_lab.errors import register_exception_handlers
from agent_lab.routers import health, rates, todos

truststore.inject_into_ssl()

app = FastAPI(title="agent-lab", version="0.1.0")

register_exception_handlers(app)

app.include_router(health.router)
app.include_router(todos.router)
app.include_router(rates.router)
