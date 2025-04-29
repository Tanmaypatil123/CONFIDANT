import json
import os
from .base import BaseLoader

class JsonLoader(BaseLoader):
    def __init__(self, filepath: str):
        """
        Initializes the JsonLoader with the specified JSON file path.
        
        Args:
        	filepath: Path to the JSON file to be loaded.
        """
        self.filepath = filepath

    def load(self) -> dict:
        """
        Loads and returns the contents of the JSON file as a dictionary.
        
        If the file does not exist at the specified path, returns an empty dictionary.
        """
        if not os.path.exists(self.filepath):
            return {}
        with open(self.filepath, "r") as f:
            return json.load(f)

    def info(self) -> str:
        """
        Returns a description of the loader, including the associated JSON file path.
        """
        return f"JSON file: {self.filepath}"
