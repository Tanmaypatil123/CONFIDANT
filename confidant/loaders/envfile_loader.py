from dotenv import dotenv_values
import os
from .base import BaseLoader

class EnvFileLoader(BaseLoader):
    def __init__(self, filepath: str):
        self.filepath = filepath

    def load(self) -> dict:
        if not os.path.exists(self.filepath):
            return {}
        return dotenv_values(self.filepath)

    def info(self) -> str:
        return f".env file: {self.filepath}"
