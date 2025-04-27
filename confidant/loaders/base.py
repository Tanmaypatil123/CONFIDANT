from abc import ABC, abstractmethod
from typing import Dict

class BaseLoader(ABC):
    """
    Abstract base class for all settings loaders.
    """

    @abstractmethod
    def load(self) -> Dict[str, str]:
        """
        Loads settings from a source.
        
        Returns:
            A dictionary mapping setting names to their string values.
        
        This method must be implemented by all subclasses to retrieve settings from
        their respective sources.
        """
        pass

    def info(self) -> str:
        """
        Returns a string identifying the source of the loader.
        
        By default, this returns the class name, but subclasses may override it to provide more specific source information such as a file path or URL.
        """
        return self.__class__.__name__
