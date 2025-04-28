# confidant/agent.py

import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import List
from confidant.settings import Settings


class SettingsFileChangeHandler(FileSystemEventHandler):
    """
    Handles file change events for settings reload.
    """

    def __init__(self, settings_instance: Settings):
        self.settings_instance = settings_instance

    def on_modified(self, event):
        if not event.is_directory:
            try:
                self.settings_instance.reload()
                if self.settings_instance._on_reload:
                    self.settings_instance._on_reload(self.settings_instance)
            except Exception:
                # Optional: you can log errors here
                pass


def start_file_watcher(settings_instance: Settings):
    """
    Start watching the source files associated with the settings instance.
    When files change, trigger settings reload automatically.
    """
    if not settings_instance._sources:
        return

    # Collect unique file paths to watch
    paths_to_watch: List[str] = []

    for source in settings_instance._sources:
        if hasattr(source, "filepath"):
            path = getattr(source, "filepath")
            if path and path not in paths_to_watch:
                paths_to_watch.append(path)

    if not paths_to_watch:
        return  # Nothing to watch

    observer = Observer()
    event_handler = SettingsFileChangeHandler(settings_instance)

    for path in paths_to_watch:
        observer.schedule(event_handler, path=path, recursive=False)

    thread = threading.Thread(target=observer.start, daemon=True)
    thread.start()

    # Optional: Keep observer reference in settings instance if you want to stop later
    settings_instance._observer = observer
