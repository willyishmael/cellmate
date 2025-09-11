from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PySide6.QtCore import Qt

class AppInfoPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        title = QLabel("📦 Application Information")
        title.setStyleSheet("font-weight: bold; font-size: 18px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setText(
            "Cellmate\n"
            "Version: 1.0.0\n"
            "\n"
            "Developed by: Your Name or Team\n"
            "Contact: your.email@example.com\n"
            "\n"
            "Description:\n"
            "Cellmate is a tool for managing attendance and overtime data.\n"
            "Features include:\n"
            "- Excel file import\n"
            "- Data extraction and comparison\n"
            "- Template management\n"
            "- And more!"
        )
        layout.addWidget(info_text)

        self.setLayout(layout)