import aiohttp

from app.core.config import settings
from app.downloader.basic import RefererMixin, Downloader, ProxyMixin, CookieMixin


class MTeam(RefererMixin, ProxyMixin, Downloader):
    domain = 'img.m-team.cc'
    referer = "https://kp.m-team.cc/"
    proxy = 'socks5://127.0.0.1:8889'


class JavBus(RefererMixin, Downloader):
    domain = 'www.javbus.com'
    referer = "https://www.javbus.com/"
