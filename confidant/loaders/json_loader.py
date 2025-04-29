import json
import os
from .base import BaseLoader

class JsonLoader(BaseLoader):
    def __init__(self, filepath: str):
        """
        Initializes the JsonLoader with the path to a JSON file.
        
        Args:
        	filepath: Path to the JSON file to be loaded.
        """
        self.filepath = filepath

    def load(self) -> dict:
        """
        Loads and parses JSON data from the specified file path.
        
        Returns:
            A dictionary containing the parsed JSON data, or an empty dictionary if the file does not exist.
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
