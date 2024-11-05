from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.core.config import settings


def init_routers(application: FastAPI):
    from app.api import api_router
    application.include_router(api_router, prefix=settings.API_STR)


@asynccontextmanager
async def lifespan(application: FastAPI):
    init_routers(application)
    yield

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
