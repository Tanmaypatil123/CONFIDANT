import os
from .base import BaseLoader

class SystemEnvLoader(BaseLoader):
    def load(self) -> dict:
        """
        Returns a dictionary of the current system environment variables.
        
        Returns:
            A dictionary mapping environment variable names to their values.
        """
        return dict(os.environ)

    def info(self) -> str:
        """
        Returns a description of the loader as "System Environment Variables".
        """
        return "System Environment Variables"
