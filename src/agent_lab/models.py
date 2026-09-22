from datetime import date

from pydantic import BaseModel, Field, field_validator


class Todo(BaseModel):
    id: int
    title: str = Field(min_length=1, max_length=100)
    done: bool = False
    due: date | None = None
    tags: list[str] = Field(default_factory=list)

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title cannot be blank")
        return v.strip()
