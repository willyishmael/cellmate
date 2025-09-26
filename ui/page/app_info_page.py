from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PySide6.QtCore import Qt

class AppInfoPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        app_version = "1.0.0"  # You can dynamically fetch this if needed

        title = QLabel("📦 Application Information")
        title.setStyleSheet("font-weight: bold; font-size: 18px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setStyleSheet("font-size: 14px;")
        info_text.setText(
            "Cellmate\n"
            "Version: " + app_version + "\n"
            "\n"
            "Developed by: William Tangka\n"
            "Contact: wtangka22@gmail.com\n"
            "\n"
            "Description:\n"
            "Cellmate is a tool for attendance and overtime report format changer.\n"
            "Features include:\n"
            "- Excel file import\n"
            "- Data extraction and comparison\n"
            "- Template management\n"
            "- And more!"
        )
        layout.addWidget(info_text)

        self.setLayout(layout)