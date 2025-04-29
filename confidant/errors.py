# confidant/errors.py

class SettingsLoadError(Exception):
    """
    Raised when settings could not be loaded properly.
    """
    pass


class SecretsError(Exception):
    """
    Raised when encryption or decryption of secrets fails.
    """
    pass


class WatcherError(Exception):
    """
    Raised when file watcher agent fails.
    """
    pass
