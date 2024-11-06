import os
import typing

from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector
from starlette.exceptions import HTTPException

from app.core.config import settings as app_settings, settings


class Downloader(object):
    domain: typing.Optional[str] = None

    def __init__(self, url, cache_key):
        self.url = url
        self.path = os.path.join(app_settings.IMAGE_CACHE_PATH, cache_key)

    def _client_default(self, **kwargs):
        headers = kwargs.pop('headers', {})
        if "User-Agent" not in headers:
            headers["User-Agent"] = settings.REQUEST_USER_AGENT

        kwargs['headers'] = headers
        return kwargs

    def get_client(self, **kwargs):
        client_methods = [attr for attr in self.__dir__() if attr.startswith('_client_')]
        for method in client_methods:
            kwargs = getattr(self, method)(**kwargs)

        return ClientSession(**kwargs)

    def get_session_kwargs(self):
        return dict()

    async def download(self):
        client = self.get_client()
        async with client as session:
            return await self.request(session)

    async def request(self, session: ClientSession):
        async with session.get(self.url.geturl(), **self.get_session_kwargs()) as response:
            if response.status == 200:
                # 创建缓存目录并存储图片

                with open(self.path, "wb") as f:
                    f.write(await response.read())
                return self.path
            else:
                raise HTTPException(status_code=response.status, detail=response.reason)


class RefererMixin(object):
    referer = ""

    # def
    def _client_referer(self, **kwargs):
        if not self.referer:
            return kwargs

        headers = kwargs.pop('headers', {})
        headers['referer'] = self.referer
        kwargs['headers'] = headers
        return kwargs


class ProxyMixin(object):
    proxy = ""

    def _client_connector(self, **kwargs):
        if not self.proxy:
            return kwargs

        connector = ProxyConnector.from_url(self.proxy, ssl=False)
        kwargs['connector'] = connector
        return kwargs


class CookieMixin(object):

    cookies = ""

    def _client_cookie(self, **kwargs):
        if not self.cookies:
            return kwargs

        kwargs['cookies'] = self.cookies
        return kwargs



class BasicDownloader(Downloader):
    domain = 'default'
