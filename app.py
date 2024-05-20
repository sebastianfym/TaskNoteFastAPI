import logging
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from tasks.api import router as tasks_router
from users.router import router as users_router
from auth.login import router as auth_router
from auth.register import router as register_router

logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(users_router)
api_router.include_router(auth_router)
api_router.include_router(register_router)
api_router.include_router(tasks_router)

app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
