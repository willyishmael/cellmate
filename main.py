# main.py
import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow

from model.helper.app_data import ensure_templates_json

if __name__ == "__main__":
    ensure_templates_json()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
