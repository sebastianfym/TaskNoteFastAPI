import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic.dataclasses import dataclass as pydantic_dataclass

from db.models import Task


@pydantic_dataclass
class ErrorException(Exception):
    status_code: int
    detail: str
    message: str


class Task(BaseModel):
    id: int
    title: str | None = None
    description: Optional[str] = None
    created_at: datetime.datetime | None = None
    owner_id: int

    @staticmethod
    def from_orm(task: Task):
        return Task(
            id=task.id,
            title=task.title,
            description=task.description,
            created_at=task.created_at,
            owner_id=task.owner_id
        )


class TaskData(BaseModel):
    title: str | None = None
    description: Optional[str] = None
    owner_id: int | None = None
    created_at: datetime.datetime | None = None