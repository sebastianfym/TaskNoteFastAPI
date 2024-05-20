from logging import getLogger

from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_200_OK

from auth.utils import get_current_active_user
from tasks.models import Task as TaskPydantic
from db.service import get_tasks_all, get_session, add_task, get_tasks_by_owner, update_task_data, delete_task, \
    get_task_by_id, is_task_owner
from users.models import User
from .models import *

log = getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/all", status_code=HTTP_200_OK, summary="Get all tasks", )
async def get_tasks(session: AsyncSession = Depends(get_session)) -> list[TaskPydantic]:
    tasks = await (get_tasks_all(session))
    if len(list(tasks)) == 0:
        return []
    return [TaskPydantic(**task.dict()) for task in tasks]


@router.post("/add", status_code=HTTP_201_CREATED, summary="Create task")
async def create_task(task: TaskData, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_active_user)):
    task.owner_id = user.id
    task.created_at = datetime.datetime.utcnow()
    new_task = await add_task(session, TaskData(**task.dict()))
    return new_task


@router.get("/my_tasks", status_code=HTTP_200_OK, summary="Get all user tasks")
async def get_task_by_owner(session: AsyncSession = Depends(get_session), user: User = Depends(get_current_active_user)):
    tasks = await (get_tasks_by_owner(session, user.id))
    if len(list(tasks)) == 0:
        return []
    return [TaskPydantic(**task.dict()) for task in tasks]


@router.patch("/{task_id}", status_code=HTTP_200_OK, summary="Update task", responses={
                404: {"model": ErrorException, "detail": "Task not found",
                      "message": "Task not found"},
                403: {"model": ErrorException, "detail": "Permission denied",
                      "message": "You are not the owner of the task"}
            })
async def update_task(task_id: int, task: TaskData, session: AsyncSession = Depends(get_session),
                      user: User = Depends(get_current_active_user)):
    if await (is_task_owner(session, task_id,  user.id)):
        data = {k: v for k, v in task.dict().items() if v is not None}
        updated_task = await update_task_data(session, task_id, data)
        return updated_task
    else:
        raise HTTPException(status_code=403, detail="You are not the owner of the task")


@router.delete("/task/{task_id}", response_model=None, summary="Delete task", responses={
                404: {"model": ErrorException, "detail": "Task not found",
                      "message": "Task not found"},
                403: {"model": ErrorException, "detail": "Permission denied",
                      "message": "You are not the owner of the task"}
            })
async def delete_task_by_id(task_id: int, session: AsyncSession = Depends(get_session),
                            user: User = Depends(get_current_active_user)):
    if await (is_task_owner(session, task_id, user.id)):
        task = await get_task_by_id(session, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        await delete_task(session, task_id)
        return {"detail": "Task deleted successfully"}
    else:
        raise HTTPException(status_code=403, detail="You are not the owner of the task")


@router.get("/task/{task_id}", response_model=TaskPydantic, summary="Get a specific task", responses={
                404: {"model": ErrorException, "detail": "Task not found",
                      "message": "Task not found"}
            })
async def get_task(task_id: int, session: AsyncSession = Depends(get_session)):
    task = await get_task_by_id(session, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task