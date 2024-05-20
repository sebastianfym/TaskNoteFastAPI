from typing import List

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import UserAuth
from tasks.models import TaskData
from .models import *
from sqlalchemy.ext.asyncio import AsyncSession

from db.config import engine, Base, async_session_maker
from db.models import Task as TaskModel
from tasks.models import Task as TaskPydantic


async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


async def get_task(session: AsyncSession, task_id: int) -> Task | None:
    task = await session.execute(select(Task).where(Task.id == task_id))
    return task.scalars().first()


async def is_task_owner(session: AsyncSession, task_id: int, user_id: int) -> bool:
    result = await session.execute(
        select(TaskModel)
        .where(TaskModel.id == task_id)
        .where(TaskModel.owner_id == user_id)
    )
    task = result.scalar_one_or_none()
    if task is None:
        return False
    return True


async def get_tasks_all(session: AsyncSession) -> List[TaskPydantic] | None:
    tasks = await session.execute(select(TaskModel))
    task_list = tasks.scalars().all()
    # task_list = [TaskPydantic.from_orm(task) for task in task_list]
    return [TaskPydantic.from_orm(task) for task in task_list]


async def get_tasks_by_owner(session: AsyncSession, user_id: int) -> List[TaskPydantic]:
    result = await session.execute(select(TaskModel).filter(TaskModel.owner_id == user_id))
    task_list = result.scalars().all()
    return [TaskPydantic.from_orm(task) for task in task_list]


async def update_task_data(session: AsyncSession, task_id: int, data: dict):
    await session.execute(
        update(TaskModel)
        .where(TaskModel.id == task_id)
        .values(**data)
    )
    await session.commit()
    result = await session.execute(select(TaskModel).where(TaskModel.id == task_id))
    updated_task = result.scalar_one_or_none()
    return updated_task


async def delete_task(session: AsyncSession, task_id: int) -> None:
    await session.execute(
        delete(TaskModel)
        .where(TaskModel.id == task_id)
    )
    await session.commit()


async def get_task_by_id(session: AsyncSession, task_id: int) -> TaskModel | None:
    result = await session.execute(select(TaskModel).where(TaskModel.id == task_id))
    task = result.scalar_one_or_none()
    return task


async def add_task(session: AsyncSession, task: TaskData):
    task = TaskModel(**task.dict())
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def create_user(session: AsyncSession, user_data: UserAuth):
    user = User(username=user_data.username, password_hash=user_data.password_hash)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    user = await session.execute(select(User).where(User.username == username))
    return user.scalars().first()
