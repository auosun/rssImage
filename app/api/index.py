import copy
import os
import os.path
from urllib.parse import quote, urlparse

from aiohttp import ClientSession
from diskcache import Cache
from fastapi import APIRouter
from starlette.exceptions import HTTPException
from starlette.responses import FileResponse

from app.core.config import settings

cache = Cache(settings.IMAGE_CACHE_PATH, cull_limit=500, eviction_policy='least-recently-used')

client_settings = {
    "default": {
        "headers": {
            "Referer": "",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        }
    },
    "img.m-team.cc": {
        "headers": {
            "Referer": "https://kp.m-team.cc/",
        }
    },
    "www.javbus.com": {
        "headers": {
            "Referer": "https://www.javbus.com/",
        }
    }

}


async def download_image(url: str, cache_key: str):
    url = urlparse(url)

    client_setting = client_settings["default"]
    if url.hostname in client_settings:
        client_setting = copy.deepcopy(client_setting)

        for k, v in client_setting.items():
            if k in client_settings[url.hostname]:
                client_setting[k].update(client_settings[url.hostname][k])

    client = ClientSession(**client_setting)

    async with client as session:
        async with session.get(url.geturl()) as response:
            if response.status == 200:
                # 创建缓存目录并存储图片
                file_path = os.path.join(settings.IMAGE_CACHE_PATH, cache_key)
                with open(file_path, "wb") as f:
                    f.write(await response.read())
                return file_path
            else:
                raise HTTPException(status_code=404, detail="Image not found")


router = APIRouter()

@router.get("/{url:path}")
async def get_image(url: str):
    if not url.startswith("http"):
        return HTTPException(status_code=400, detail="Invalid URL")

    cache_key = quote(url, safe="")
    cached_file = cache.get(cache_key)

    if cached_file and os.path.exists(cached_file):
        return FileResponse(cached_file)

    file_path = await download_image(url, cache_key)
    cache.set(cache_key, file_path)

    return FileResponse(file_path)
