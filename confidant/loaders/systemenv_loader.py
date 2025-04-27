import os
from .base import BaseLoader

class SystemEnvLoader(BaseLoader):
    def load(self) -> dict:
        return dict(os.environ)

    def info(self) -> str:
        return "System Environment Variables"
