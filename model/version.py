import os

# Centralized application version. Override by setting APP_VERSION at runtime/build time.
__version__ = os.environ.get("APP_VERSION", "1.0.0")


def get_version() -> str:
    return __version__
