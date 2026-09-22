from datetime import datetime
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field

from agent_lab.tools.base import Tool


class GetTimeInput(BaseModel):
    timezone: str = Field(default="Asia/Hong_Kong", description="IANA 時區，例如 Asia/Tokyo")


async def get_time(inp: GetTimeInput) -> str:
    return datetime.now(ZoneInfo(inp.timezone)).strftime("%Y-%m-%d %H:%M:%S %Z")


class TodoAddInput(BaseModel):
    title: str = Field(min_length=1, description="待辦內容")
    due: str | None = Field(default=None, description="到期日 YYYY-MM-DD")


class TodoListInput(BaseModel):
    pass


_TODOS: list[dict] = []


async def todo_add(inp: TodoAddInput) -> str:
    _TODOS.append(inp.model_dump())
    return f"已新增：{inp.title}（目前共 {len(_TODOS)} 項）"


async def todo_list(_: TodoListInput) -> str:
    if not _TODOS:
        return "目前沒有待辦事項。"
    return "\n".join(
        f"{i}. {t['title']}" + (f"（到期 {t['due']}）" if t["due"] else "")
        for i, t in enumerate(_TODOS, 1)
    )


class CalendarAddInput(BaseModel):
    title: str = Field(min_length=1, description="行程名稱")
    date: str = Field(description="日期 YYYY-MM-DD")
    at: str | None = Field(default=None, description="時間 HH:MM")


class CalendarQueryInput(BaseModel):
    date: str = Field(description="要查詢的日期 YYYY-MM-DD")


_EVENTS: list[dict] = []


async def calendar_add(inp: CalendarAddInput) -> str:
    _EVENTS.append(inp.model_dump())
    return f"已加入行程：{inp.date} {inp.at or '(全天)'} {inp.title}"


async def calendar_query(inp: CalendarQueryInput) -> str:
    hits = [e for e in _EVENTS if e["date"] == inp.date]
    if not hits:
        return f"{inp.date} 沒有行程。"
    return "\n".join(f"- {e['at'] or '(全天)'} {e['title']}" for e in hits)


LOCAL_TOOLS = [
    Tool("get_current_time", "取得指定時區的目前日期與時間。", GetTimeInput, get_time),
    Tool("todo_add", "新增一筆待辦事項。", TodoAddInput, todo_add),
    Tool("todo_list", "列出所有待辦事項。", TodoListInput, todo_list),
    Tool("calendar_add", "在日曆新增一筆行程。", CalendarAddInput, calendar_add),
    Tool("calendar_query", "查詢某一天的行程。", CalendarQueryInput, calendar_query),
]
