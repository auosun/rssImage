from pathlib import Path
from typing import Optional

from pydantic.v1 import BaseSettings


class Settings(BaseSettings):

    PROJECT_NAME = "proxy_image"

    API_STR: str = "/api"

    CONFIG_DIR: Optional[str] = None

    ALLOWED_HOSTS = ["*"]

    @property
    def CONFIG_PATH(self):
        if self.CONFIG_DIR:
            return Path(self.CONFIG_DIR)

        return self.ROOT_PATH / "config"

    @property
    def ROOT_PATH(self):
        return Path(__file__).parents[2]

    @property
    def LOG_PATH(self):
        return self.CONFIG_PATH / "logs"

    @property
    def IMAGE_CACHE_PATH(self):
        return self.CONFIG_PATH / "image_cache"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for path in [self.CONFIG_PATH, self.LOG_PATH, self.IMAGE_CACHE_PATH]:
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)

    class Config:
        # 环境变量名称必须与字段名称匹配
        case_sensitive = True


settings = Settings(
    _env_file=Settings().CONFIG_PATH / ".env",
    _env_file_encoding="utf-8",
)
