from agent_lab.errors import NotFoundError
from agent_lab.models import Todo


class TodoStore:
    """記憶體版的 Todo 儲存（≈ Nest 的 TodoService）。"""

    def __init__(self) -> None:
        self._items: dict[int, Todo] = {}

    def add(self, todo: Todo) -> Todo:
        self._items[todo.id] = todo
        return todo

    def list(self) -> list[Todo]:
        return list(self._items.values())

    def get(self, todo_id: int) -> Todo:
        todo = self._items.get(todo_id)
        if todo is None:
            raise NotFoundError(f"todo {todo_id} 不存在")
        return todo


_store = TodoStore()


def get_todo_store() -> TodoStore:
    return _store
