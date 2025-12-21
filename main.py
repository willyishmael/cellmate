# main.py
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ui.main_window import MainWindow

from model.helper.app_data import ensure_templates_json, resource_path

if __name__ == "__main__":
    ensure_templates_json()
    app = QApplication(sys.argv)
    # Set application window icon (taskbar/titlebar)
    try:
        # Use platform-appropriate icon format
        if sys.platform == "darwin":
            icon_file = "data/icon.icns"
        else:
            icon_file = "data/icon.ico"
        icon_path = resource_path(icon_file)
        app.setWindowIcon(QIcon(str(icon_path)))
    except (FileNotFoundError, OSError):
        # Fail silently if icon missing; app still runs
        pass
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
