from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QTextEdit, QFileDialog, 
    QMessageBox, QInputDialog, QAbstractItemView, QHeaderView
)

from PySide6.QtCore import Qt
import json
from view_model.template_view_model import TemplateViewModel

class TemplatePage(QWidget):
    def __init__(self, template_vm: TemplateViewModel):
        super().__init__()
        self.vm = template_vm
        
        self.setWindowTitle("Template Management")
        layout = QVBoxLayout()

        # Title
        title = QLabel("🗂 Template Management")
        title.setStyleSheet("font-weight: bold; font-size: 18px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Titles for table and editor
        titles_layout = QHBoxLayout()
        table_title = QLabel("Templates List")
        table_title.setAlignment(Qt.AlignCenter)
        table_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        editor_title = QLabel("Review")
        editor_title.setAlignment(Qt.AlignCenter)
        editor_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        titles_layout.addWidget(table_title, 2)
        titles_layout.addWidget(editor_title, 3)
        layout.addLayout(titles_layout)

        editor_layout = QHBoxLayout()

        # Table of templates with headers
        self.template_table = QTableWidget()
        self.template_table.setColumnCount(2)
        self.template_table.setHorizontalHeaderLabels(["Template Name", "Type"])
        self.template_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.template_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.template_table.verticalHeader().setVisible(False)
        self.template_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.template_table.horizontalHeader().setStretchLastSection(True)
        self.template_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.template_table.cellClicked.connect(self.display_template)
        editor_layout.addWidget(self.template_table)

        # Template details view
        self.template_details = QTextEdit()
        self.template_details.setReadOnly(True)
        editor_layout.addWidget(self.template_details)

        layout.addLayout(editor_layout)

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
        
        self.vm.templates_changed.connect(self.refresh_table)
        self.refresh_table()

    def refresh_table(self):
        templates = self.vm.get_templates()
        self.template_table.setRowCount(len(templates))
        for row, t in enumerate(templates):
            self.template_table.setItem(row, 0, QTableWidgetItem(t.name))
            self.template_table.setItem(row, 1, QTableWidgetItem(t.template_type))
        self.template_details.clear()

    def display_template(self, row, col=None):
        # row: int, col: int (col is not used)
        templates = self.vm.get_templates()
        if 0 <= row < len(templates):
            template = templates[row]
            details = json.dumps(template.to_dict(), indent=2)
            self.template_details.setPlainText(details)
        else:
            self.template_details.clear()

    def edit_template(self):
        current = self.template_table.currentRow()
        if current < 0:
            QMessageBox.warning(self, "No Selection", "Select a template to edit.")
            return
        template = self.vm.get_templates()[current]
        text, ok = QInputDialog.getMultiLineText(self, "Edit Template", f"Edit settings for {template.name}", json.dumps(template.to_dict(), indent=2))
        if ok:
            try:
                data = json.loads(text)
                # Use dict identifier (name + template_type) to locate the template
                identifier = {"name": template.name, "template_type": template.template_type}
                self.vm.update_template(identifier, name=data.get('name'), template_type=data.get('template_type'), settings=data.get('settings'))
                # Refresh and attempt to re-select the updated template (by new name/type)
                self.refresh_table()
                new_name = data.get('name') or template.name
                new_type = data.get('template_type') or template.template_type
                for row in range(self.template_table.rowCount()):
                    if (self.template_table.item(row, 0).text() == new_name and
                            self.template_table.item(row, 1).text() == new_type):
                        self.template_table.selectRow(row)
                        break
            except Exception as e:
                QMessageBox.critical(self, "Invalid JSON", str(e))

    def delete_template(self):
        current = self.template_table.currentRow()
        if current < 0:
            QMessageBox.warning(self, "No Selection", "Select a template to delete.")
            return
        
        template = self.vm.get_templates()[current]
        reply = QMessageBox.question(self, "Delete Template", f"Delete template '{template.name}'?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.vm.delete_template({"name": template.name, "template_type": template.template_type})
            except Exception as e:
                QMessageBox.critical(self, "Delete Failed", str(e))
                return
            # Refresh table and select previous row if possible
            self.refresh_table()
            row_count = self.template_table.rowCount()
            if row_count == 0:
                self.template_details.clear()
                return
            # try to keep selection at the same index, or move to last row
            sel = min(current, row_count - 1)
            self.template_table.selectRow(sel)

    def export_templates(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Templates", "templates_export.json", "JSON Files (*.json)")
        if path:
            self.vm.export_templates(path)
            QMessageBox.information(self, "Exported", f"Templates exported to {path}")

    def import_templates(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Templates", "", "JSON Files (*.json)")
        if path:
            try:
                self.vm.import_templates(path)
                self.refresh_table()
                QMessageBox.information(self, "Imported", f"Templates imported from {path}")
            except Exception as e:
                QMessageBox.critical(self, "Import Failed", str(e))
