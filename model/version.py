import os

# Centralized application version. Override by setting APP_VERSION at runtime/build time.
__version__ = os.environ.get("APP_VERSION", "1.0.0")


def get_version() -> str:
    """Return the current application version as a stable public API.

    This thin wrapper intentionally adds a level of indirection so that
    version retrieval logic can evolve (for example, reading from a file
    or a package resource) without requiring callers to change how they
    obtain the version string.
    """
    return __version__
