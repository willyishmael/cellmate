from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout, QProgressBar
from PySide6.QtCore import Qt


class LoadingDialog(QDialog):
    """A reusable loading dialog with progress indicator for long-running operations."""
    
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Processing")
        self.setModal(True)
        self.setFixedSize(280, 80)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        
        label = QLabel(message)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # indeterminate
        self.progress.setFixedHeight(20)
        self.progress.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress)
        
        self.setLayout(layout)
