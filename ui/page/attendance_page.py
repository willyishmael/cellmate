from PySide6.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QWidget, 
    QSpacerItem, QSizePolicy, QFormLayout, 
    QPushButton, QInputDialog, QMessageBox, QCheckBox
)

from PySide6.QtCore import Qt
from ui.widget.drop_area_view import DropArea
from ui.widget.template_bar import TemplateBar
from ui.widget.period_date_widget import PeriodDateWidget
from ui.widget.company_code_checkbox import CompanyCodeCheckbox
from ui.widget.form_field_group import FormFieldGroup
from ui.widget.multi_text_field_group import MultiTextFieldGroup
from view_model.attendance_view_model import AttendanceViewModel
from model.template_model import Template
from view_model.template_view_model import TemplateViewModel

class AttendancePage(QWidget):
    def __init__(self, template_vm: TemplateViewModel):
        super().__init__()
        self.template_vm = template_vm
        self.attendance_vm = AttendanceViewModel()
        self.current_template_index = None
        self.template_type = "attendance"
        self.attendance_templates = []
        main_layout = QHBoxLayout()
        
        # Left panel with two drop areas
        left_panel = QVBoxLayout()
        self.drop_area_1 = DropArea("Drop Attendance Excel File Here")
        self.drop_area_2 = DropArea("Drop HRIS Export Excel File Here")
        left_panel.addWidget(self.drop_area_1, 1)
        left_panel.addWidget(self.drop_area_2, 1)
        main_layout.addLayout(left_panel, 2)

        # Right panel (settings)
        right_panel = QVBoxLayout()
        self.setting_label = QLabel("⚙ Settings")
        self.setting_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        right_panel.addWidget(self.setting_label)

        # Template selection bar (refactored)
        self.template_bar = TemplateBar(self.on_template_selected)
        self.template_bar.btn_save.clicked.connect(self.on_save_template)
        self.template_bar.btn_new.clicked.connect(self.on_new_template)
        
        # Wrap TemplateBar (QHBoxLayout) in QWidget for addLayout compatibility
        template_bar_widget = QWidget()
        template_bar_widget.setLayout(self.template_bar)
        right_panel.addWidget(template_bar_widget)

        # Period and Start/End Date section (refactored)
        self.period_date_widget = PeriodDateWidget()

        # Continue with the rest of the form
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_layout.setFormAlignment(Qt.AlignTop)
        form_layout.setHorizontalSpacing(15)
        form_layout.setVerticalSpacing(15)

        # Add period/date widget as a row
        form_layout.addRow(self.period_date_widget)

        self.company_codes_layout = CompanyCodeCheckbox()
        form_layout.addRow("Company Codes:", self.company_codes_layout)

        # Define field labels and placeholders
        field_configs = {
            "Employee ID Column": "Enter Employee ID Column Index (e.g., 5)",
            "Employee Name Column": "Enter Employee Name Column Index (e.g., 6)",
            "Company Code Column": "Enter Company Code Column Index (e.g., 7)",
            "Data Start Row": "Enter Data Start Row Index (e.g., 2)",
            "Date Header Row": "Enter Date Header Row Index (e.g., 1)",
            "Row Counter Column": "Enter Row Counter Column Index (e.g., 3)",
        }
        self.form_field_group = FormFieldGroup(field_configs, form_layout)
        
        edit_text_configs = {
            "Sheet Names": "Enter sheet names separated by commas (e.g., Sheet1, Sheet2)",
            "Ignore List": "Enter Employee IDs to ignore, separated by commas (e.g., OBI-212365, OBI-756532)"
        }
        self.multi_text_field_group = MultiTextFieldGroup(edit_text_configs, form_layout)

        # Add "Time Off Only?" checkbox
        self.checkbox_time_off_only = QCheckBox("Time Off Only")
        form_layout.addRow("", self.checkbox_time_off_only)

        right_panel.addLayout(form_layout)
        right_panel.addItem(QSpacerItem(20, 200, QSizePolicy.Minimum, QSizePolicy.Expanding))

        btn_extract = QPushButton("📊 Extract Data")
        btn_compare = QPushButton("🔍 Compare Data")
        btn_extract.setFixedHeight(40)
        btn_compare.setFixedHeight(40)
        btn_extract.clicked.connect(self.on_extract)
        btn_compare.clicked.connect(self.on_compare)
        right_panel.addWidget(btn_extract)
        right_panel.addWidget(btn_compare)
        main_layout.addLayout(right_panel, 3)

        self.setLayout(main_layout)
        
        # Connect signal to update dropdown automatically
        self.template_vm.templates_changed.connect(self.load_templates_to_dropdown)
        self.load_templates_to_dropdown()
        
    def load_templates_to_dropdown(self):
        dropdown = self.template_bar.template_dropdown
        dropdown.blockSignals(True)
        dropdown.clear()
        dropdown.addItem("Select Template")
        self.attendance_templates = self.template_vm.get_templates(template_type=self.template_type)
        for t in self.attendance_templates:
            dropdown.addItem(t.name)
        dropdown.blockSignals(False)
        
    def on_template_selected(self, index):
        if index <= 0:
            self.current_template_index = None
            self._clear_fields()
            return
        
        self.current_template_index = index - 1
        template: Template = self.attendance_templates[self.current_template_index]
        self._load_settings_to_fields(template)

    def _clear_fields(self):
        self.company_codes_layout.clear_checked()
        self.form_field_group.clear_fields()        
        self.multi_text_field_group.clear_fields()
        self.checkbox_time_off_only.setChecked(False)
        
    def _load_settings_to_fields(self, template: Template):
        settings = template.settings
        self.company_codes_layout.load_settings(settings)
        self.form_field_group.load_settings(settings)
        self.multi_text_field_group.load_settings(settings)
        self.checkbox_time_off_only.setChecked(settings["time_off_only"])

    # Save current form values to the selected template
    def on_save_template(self):
        dropdown = self.template_bar.template_dropdown
        index = dropdown.currentIndex()
        if index <= 0 or self.current_template_index is None:
            return
        
        name = dropdown.currentText()
        confirm = QMessageBox.question(
            self,
            "Confirm Overwrite",
            f"Are you sure you want to overwrite the template '{name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return

        settings = self.collect_settings_from_fields()
        self.template_vm.update_template(
            identifier={"name": name, "template_type": self.template_type}, 
            name=name, 
            template_type=self.template_type, 
            settings=settings)
        
        self.load_templates_to_dropdown()
        dropdown.setCurrentIndex(index)

    def on_new_template(self):
        name, ok = QInputDialog.getText(self, "New Template", "Enter template name:")
        if not ok or not name.strip():
            return
        
        settings = self.collect_settings_from_fields()
        if settings == {}:
            return
        
        self.template_vm.add_template(name.strip(), self.template_type, settings)
        self.load_templates_to_dropdown()
        
        dropdown = self.template_bar.template_dropdown
        for i in range(dropdown.count()):
            if dropdown.itemText(i) == name.strip():
                dropdown.setCurrentIndex(i)
                break

    def collect_settings_from_fields(self):
        settings = {}
        
        validated_company_codes, validated_company_codes_message = self.company_codes_layout.has_checked_codes()
        if not validated_company_codes:
            QMessageBox.warning(self, "Warning", validated_company_codes_message)
            return {}
        
        validated_form_fields, validated_form_message = self.form_field_group.validate_fields()
        if not validated_form_fields:
            QMessageBox.warning(self, "Warning", validated_form_message)
            return {}

        validated_multi_text, validated_multi_text_message = self.multi_text_field_group.validate_fields()
        if not validated_multi_text:
            QMessageBox.warning(self, "Warning", validated_multi_text_message)
            return {}

        settings.update(self.company_codes_layout.get_company_codes())
        settings.update(self.form_field_group.get_field_values())    
        settings.update(self.multi_text_field_group.get_field_values())
        settings.update({"time_off_only": self.checkbox_time_off_only.isChecked()})
        return settings

    def on_extract(self):
        settings = self.collect_settings_from_fields()
        if settings == {}:
            return
        
        file = self.drop_area_1.file_path
        
        date_start = self.period_date_widget.start_date_picker.date()
        date_end = self.period_date_widget.end_date_picker.date()
        date_start_str = date_start.toString("yyyy-MM-dd")
        date_end_str = date_end.toString("yyyy-MM-dd")
        
        if not file:
            QMessageBox.warning(self, "Warning", "Please drop an Attendance Excel file.")
            return
        
        # Extract data using ViewModel
        try:
            result = self.attendance_vm.extract_attendance(settings, date_start_str, date_end_str, file)
            if result.success:
                QMessageBox.information(self, "Success", "Data extraction completed successfully.")
            else:
                QMessageBox.warning(self, "Warning", f"Data extraction failed: {result.message}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred during extraction: {str(e)}")
            
    def on_compare(self):
        settings = self.collect_settings_from_fields()
        if settings == {}:
            return
        
        validated_attendance_file, attendance_file_message = self.drop_area_1.validate_file()
        validated_hris_file, hris_file_message = self.drop_area_2.validate_file()
        
        if not validated_attendance_file:
            QMessageBox.warning(self, "Warning", attendance_file_message)
            return
        
        if not validated_hris_file:
            QMessageBox.warning(self, "Warning", hris_file_message)
            return
        
        attendance_file = self.drop_area_1.file_path
        hris_file = self.drop_area_2.file_path
        
        date_start = self.period_date_widget.start_date_picker.date()
        date_end = self.period_date_widget.end_date_picker.date()
        date_start_str = date_start.toString("yyyy-MM-dd")
        date_end_str = date_end.toString("yyyy-MM-dd")

        # Compare data using ViewModel
        try:
            result = self.attendance_vm.compare_attendance(settings, date_start_str, date_end_str, attendance_file, hris_file)
            if result.success:
                QMessageBox.information(self, "Success", "Data comparison completed successfully.")
            else:
                QMessageBox.warning(self, "Warning", f"Data comparison failed: {result.message}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred during comparison: {str(e)}")
    