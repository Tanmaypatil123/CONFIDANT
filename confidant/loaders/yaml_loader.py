import json
import os
from .base import BaseLoader

class JsonLoader(BaseLoader):
    def __init__(self, filepath: str):
        self.filepath = filepath

    def load(self) -> dict:
        if not os.path.exists(self.filepath):
            return {}
        with open(self.filepath, "r") as f:
            return json.load(f)

    def info(self) -> str:
        return f"JSON file: {self.filepath}"
