# from fastapi import APIRouter

# from agent_lab.models import Todo

# router = APIRouter(prefix="/todos", tags=["todos"])

# _todos: list[Todo] = []


# @router.post("")
# async def create_todo(todo: Todo) -> Todo:
#     _todos.append(todo)
#     return todo


# @router.get("")
# async def list_todos() -> list[Todo]:
#     return _todos


from typing import Annotated

from fastapi import APIRouter, Depends

from agent_lab.deps import TodoStore, get_todo_store
from agent_lab.models import Todo

router = APIRouter(prefix="/todos", tags=["todos"])

Store = Annotated[TodoStore, Depends(get_todo_store)]


@router.post("")
async def create_todo(todo: Todo, store: Store) -> Todo:
    return store.add(todo)


@router.get("")
async def list_todos(store: Store) -> list[Todo]:
    return store.list()


@router.get("/{todo_id}")
async def get_todo(todo_id: int, store: Store) -> Todo:
    return store.get(todo_id)
