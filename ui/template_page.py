from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QTextEdit, QFileDialog, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt
import json
import os

TEMPLATE_FILE = "templates.json"

class TemplatePage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Template Management")
        layout = QVBoxLayout()

        # Title
        title = QLabel("🗂 Template Management")
        title.setStyleSheet("font-weight: bold; font-size: 18px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # List of templates
        self.template_list = QListWidget()
        self.template_list.currentItemChanged.connect(self.display_template)
        layout.addWidget(self.template_list)

        # Template details view
        self.template_details = QTextEdit()
        self.template_details.setReadOnly(True)
        layout.addWidget(self.template_details)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_edit = QPushButton("Edit")
        self.btn_delete = QPushButton("Delete")
        self.btn_export = QPushButton("Export")
        self.btn_import = QPushButton("Import")
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_export)
        btn_layout.addWidget(self.btn_import)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # Connect buttons
        self.btn_edit.clicked.connect(self.edit_template)
        self.btn_delete.clicked.connect(self.delete_template)
        self.btn_export.clicked.connect(self.export_templates)
        self.btn_import.clicked.connect(self.import_templates)

        self.templates = {}
        self.load_templates()

    def load_templates(self):
        if os.path.exists(TEMPLATE_FILE):
            with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
                self.templates = json.load(f)
        else:
            self.templates = {}
        self.refresh_list()

    def save_templates(self):
        with open(TEMPLATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.templates, f, indent=2)

    def refresh_list(self):
        self.template_list.clear()
        for key in self.templates:
            self.template_list.addItem(key)
        self.template_details.clear()

    def display_template(self, current, previous):
        if current:
            key = current.text()
            details = json.dumps(self.templates.get(key, {}), indent=2)
            self.template_details.setPlainText(details)
        else:
            self.template_details.clear()

    def edit_template(self):
        current = self.template_list.currentItem()
        if not current:
            QMessageBox.warning(self, "No Selection", "Select a template to edit.")
            return
        key = current.text()
        # For simplicity, allow editing JSON directly
        text, ok = QInputDialog.getMultiLineText(self, "Edit Template", f"Edit settings for {key}", json.dumps(self.templates[key], indent=2))
        if ok:
            try:
                self.templates[key] = json.loads(text)
                self.save_templates()
                self.display_template(current, None)
            except Exception as e:
                QMessageBox.critical(self, "Invalid JSON", str(e))

    def delete_template(self):
        current = self.template_list.currentItem()
        if not current:
            QMessageBox.warning(self, "No Selection", "Select a template to delete.")
            return
        key = current.text()
        reply = QMessageBox.question(self, "Delete Template", f"Delete template '{key}'?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.templates.pop(key, None)
            self.save_templates()
            self.refresh_list()

    def export_templates(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Templates", "templates_export.json", "JSON Files (*.json)")
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.templates, f, indent=2)
            QMessageBox.information(self, "Exported", f"Templates exported to {path}")

    def import_templates(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Templates", "", "JSON Files (*.json)")
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    imported = json.load(f)
                self.templates.update(imported)
                self.save_templates()
                self.refresh_list()
                QMessageBox.information(self, "Imported", f"Templates imported from {path}")
            except Exception as e:
                QMessageBox.critical(self, "Import Failed", str(e))
