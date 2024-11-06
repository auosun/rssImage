import importlib
import inspect
import os
import os.path
from urllib.parse import quote, urlparse

from diskcache import Cache
from fastapi import APIRouter
from starlette.exceptions import HTTPException
from starlette.responses import FileResponse

from app.core.config import settings
from app.downloader.basic import Downloader
from app.downloader.domain import MTeam

cache = Cache(settings.IMAGE_CACHE_PATH, cull_limit=500, eviction_policy='least-recently-used')

router = APIRouter()


module = importlib.import_module('app.downloader')
downloader_subclasses = [
    cls for _, cls in inspect.getmembers(module, inspect.isclass)
    if issubclass(cls, Downloader) and cls is not Downloader and cls.domain
]

downloaders = {d.domain: d for d in downloader_subclasses}

@router.get("/{url:path}")
async def get_image(url: str):
    if not url.startswith("http"):
        return HTTPException(status_code=400, detail="Invalid URL")

    cache_key = quote(url, safe="")
    cached_file = cache.get(cache_key)

    if cached_file and os.path.exists(cached_file):
        return FileResponse(cached_file)

    url = urlparse(url)
    dcls = downloaders.get(url.hostname, downloaders["default"])
    file_path = await dcls(url, cache_key).download()

    cache.set(cache_key, file_path)
    return FileResponse(file_path)
