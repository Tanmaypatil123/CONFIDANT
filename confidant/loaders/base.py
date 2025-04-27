from abc import ABC, abstractmethod
from typing import Dict

class BaseLoader(ABC):
    """
    Abstract base class for all settings loaders.
    """

    @abstractmethod
    def load(self) -> Dict[str, str]:
        """
        Load settings from source.
        Must be implemented by all loaders.
        """
        pass

    def info(self) -> str:
        """
        Optional: Return source info (file path, URL, etc.)
        """
        return self.__class__.__name__
