from dotenv import dotenv_values
import os
from .base import BaseLoader

class EnvFileLoader(BaseLoader):
    def __init__(self, filepath: str):
        """
        Initializes the EnvFileLoader with the path to an environment file.
        
        Args:
        	filepath: Path to the .env file to be loaded.
        """
        self.filepath = filepath

    def load(self) -> dict:
        """
        Loads environment variables from the specified file.
        
        Returns:
            A dictionary containing environment variables from the file, or an empty
            dictionary if the file does not exist.
        """
        if not os.path.exists(self.filepath):
            return {}
        return dotenv_values(self.filepath)

    def info(self) -> str:
        """
        Returns a string describing the path of the environment file in use.
        """
        return f".env file: {self.filepath}"
