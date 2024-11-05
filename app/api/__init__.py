from fastapi import APIRouter

from app.api import index

api_router = APIRouter()

api_router.include_router(index.router, prefix='', tags=['index'])