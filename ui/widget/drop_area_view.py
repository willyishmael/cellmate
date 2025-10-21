from PySide6.QtWidgets import QLabel, QSizePolicy
from PySide6.QtCore import Qt
import os

class DropArea(QLabel):
    """A widget that acts as a drop area for Excel files."""
    def __init__(self, placeholder_text="Drop Excel File Here"):
        super().__init__(placeholder_text)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 8px;
                font-size: 16px;
                color: #555;
                padding: 24px;
            }
        """)
        self.setAcceptDrops(True)
        self.file_path = None
        
        # Allow long filenames to wrap into multiple lines instead of expanding the widget
        self.setWordWrap(True)
        size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setRetainSizeWhenHidden(False)
        self.setSizePolicy(size_policy)

    def dragEnterEvent(self, event):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].toLocalFile().lower().endswith((".xlsx", ".xls")):
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Handle file drop event."""
        urls = event.mimeData().urls()
        if urls:
            self.file_path = urls[0].toLocalFile()
            self.setText(f"✔ Loaded: {os.path.basename(self.file_path)}")
            
    def validate_file(self):
        """Validate that a file has been dropped."""
        if not self.file_path:
            return False, "Please drop an Excel file."
        return True, ""



