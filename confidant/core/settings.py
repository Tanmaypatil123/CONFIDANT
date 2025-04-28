# confidant/settings.py

import threading
import datetime
from typing import Type, TypeVar, List, Optional, Dict, Any, Callable

from pydantic import BaseModel
from confidant.loaders import BaseLoader
from confidant.secrets import decrypt_secret_fields, resolve_secret_identifiers
from confidant.errors import SettingsLoadError

T = TypeVar("T", bound="Settings")


class Settings(BaseModel):
    _sources: List[BaseLoader] = []
    _current_version: int = 0
    _last_loaded_data: Dict[str, Any] = {}
    _last_loaded_time: Optional[datetime.datetime] = None
    _on_reload: Optional[Callable] = None
    _watch_enabled: bool = False
    _lock: threading.Lock = threading.Lock()

    @classmethod
    def load(
        cls: Type[T],
        sources: Optional[List[BaseLoader]] = None,
        watch: bool = False,
        on_reload: Optional[Callable[[T], None]] = None,
    ) -> T:
        """
        Load settings from one or more sources.
        """
        try:
            raw_data = {}

            sources = sources or []

            for source in sources:
                raw_data.update(source.load())

            # Decrypt any fields wrapped with ENC(...)
            raw_data = decrypt_secret_fields(raw_data)

            # Resolve identifiers from SecretFields
            raw_data = resolve_secret_identifiers(raw_data)

            # Validate and instantiate settings
            instance = cls(**raw_data)

            # Set internal metadata
            instance._sources = sources
            instance._current_version = 1
            instance._last_loaded_data = raw_data
            instance._last_loaded_time = datetime.datetime.utcnow()
            instance._on_reload = on_reload
            instance._watch_enabled = watch

            # Start hot reloader if needed
            if watch:
                from confidant.core.agent import start_file_watcher
                start_file_watcher(instance)

            return instance

        except Exception as e:
            raise SettingsLoadError(str(e))

    def reload(self) -> None:
        """
        Reload settings manually from sources.
        """
        with self._lock:
            try:
                raw_data = {}

                for source in self._sources:
                    raw_data.update(source.load())

                raw_data = decrypt_secret_fields(raw_data)
                raw_data = resolve_secret_identifiers(raw_data)

                updated_instance = self.__class__(**raw_data)

                # Copy new validated fields
                for field in updated_instance.__fields__:
                    setattr(self, field, getattr(updated_instance, field))

                # Update internal state
                self._current_version += 1
                self._last_loaded_data = raw_data
                self._last_loaded_time = datetime.datetime.utcnow()

                if self._on_reload:
                    self._on_reload(self)

            except Exception as e:
                # Optional: you can log reload error instead of crashing app
                pass

    def get_loaded_sources(self) -> List[str]:
        """
        Get a list of source info (file paths, etc.)
        """
        return [source.info() for source in self._sources]
