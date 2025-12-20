from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path


APP_NAME = "Cellmate"
TEMPLATES_FILENAME = "templates.json"
DEFAULT_TEMPLATES_RELATIVE_PATH = Path("data") / TEMPLATES_FILENAME


def _resource_base_dir() -> Path:
    """Return base directory for bundled resources.

    - In dev: project root
    - In PyInstaller: sys._MEIPASS
    """

    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(getattr(sys, "_MEIPASS"))

    # This file lives at: <root>/model/helper/app_data.py
    return Path(__file__).resolve().parents[2]


def resource_path(relative_path: os.PathLike | str) -> Path:
    return _resource_base_dir() / Path(relative_path)


def app_data_dir(app_name: str = APP_NAME) -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA") or (Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME") or (Path.home() / ".local" / "share"))

    return base / app_name


def user_templates_path(app_name: str = APP_NAME) -> Path:
    return app_data_dir(app_name) / TEMPLATES_FILENAME


def ensure_templates_json(app_name: str = APP_NAME) -> Path:
    """Ensure a user-writable templates.json exists.

    Copies the bundled default templates on first run; otherwise creates an empty file.
    Returns the resolved user templates path.
    """

    target_dir = app_data_dir(app_name)
    target_dir.mkdir(parents=True, exist_ok=True)

    target_path = target_dir / TEMPLATES_FILENAME
    if target_path.exists():
        return target_path

    default_path = resource_path(DEFAULT_TEMPLATES_RELATIVE_PATH)
    if default_path.exists():
        shutil.copy2(default_path, target_path)
        return target_path

    target_path.write_text(json.dumps([], indent=2), encoding="utf-8")
    return target_path
