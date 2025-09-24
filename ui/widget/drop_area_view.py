from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
import os

class DropArea(QLabel):
    def __init__(self, placeholder_text="Drop Excel File Here"):
        super().__init__(placeholder_text)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 8px;
                font-size: 16px;
                color: #555;
                padding: 40px;
            }
        """)
        self.setAcceptDrops(True)
        self.file_path = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].toLocalFile().lower().endswith((".xlsx", ".xls")):
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            self.file_path = urls[0].toLocalFile()
            self.setText(f"✔ Loaded: {os.path.basename(self.file_path)}")



