from PySide6.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QWidget, 
    QSpacerItem, QSizePolicy, QFormLayout,
    QLineEdit, QTextEdit ,QPushButton,
    QInputDialog, QMessageBox
)

from PySide6.QtCore import Qt, QDate
from ui.drop_area_view import DropArea
from ui.template_bar import TemplateBar
from ui.period_date_widget import PeriodDateWidget
from ui.widget.company_code_checkbox import CompanyCodeCheckbox

class AttendancePage(QWidget):
    def __init__(self, template_vm):
        super().__init__()
        self.vm = template_vm
        self.current_template_index = None
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

        # Create and store references to QLineEdit fields
        self.field_employee_id_col = self.create_field("Enter Employee ID Column Index (e.g., 5)")
        self.field_employee_name_col = self.create_field("Enter Employee Name Column Index (e.g., 6)")
        self.field_company_code_col = self.create_field("Enter Company Code Column Index (e.g., 7)")
        self.field_data_start_row = self.create_field("Enter Data Start Row Index (e.g., 2)")
        self.field_date_header_row = self.create_field("Enter Date Header Row Index (e.g., 1)")
        self.field_row_counter_col = self.create_field("Enter Row Counter Column Index (e.g., 3)")
        form_layout.addRow("Employee ID Column:", self.field_employee_id_col)
        form_layout.addRow("Employee Name Column:", self.field_employee_name_col)
        form_layout.addRow("Company Code Column:", self.field_company_code_col)
        form_layout.addRow("Data Start Row:", self.field_data_start_row)
        form_layout.addRow("Date Header Row:", self.field_date_header_row)
        form_layout.addRow("Row Counter Column:", self.field_row_counter_col)

        self.sheet_names_text_edit = QTextEdit()
        self.sheet_names_text_edit.setPlaceholderText("Enter sheet names separated by commas (e.g., Sheet1, Sheet2)")
        self.sheet_names_text_edit.setFixedHeight(60)
        form_layout.addRow("Sheet Names:", self.sheet_names_text_edit)

        self.ignore_list_text_edit = QTextEdit()
        self.ignore_list_text_edit.setPlaceholderText("Enter Employee IDs to ignore, separated by commas (e.g., OBI-212365, OBI-7565324)")
        self.ignore_list_text_edit.setFixedHeight(60)
        form_layout.addRow("Ignore List:", self.ignore_list_text_edit)

        right_panel.addLayout(form_layout)
        right_panel.addItem(QSpacerItem(20, 200, QSizePolicy.Minimum, QSizePolicy.Expanding))

        btn_extract = QPushButton("📊 Extract Data")
        btn_compare = QPushButton("🔍 Compare Data")
        btn_extract.setFixedHeight(40)
        btn_compare.setFixedHeight(40)
        right_panel.addWidget(btn_extract)
        right_panel.addWidget(btn_compare)
        main_layout.addLayout(right_panel, 3)

        self.setLayout(main_layout)
        
        # Connect signal to update dropdown automatically
        self.vm.templates_changed.connect(self.load_templates_to_dropdown)
        self.load_templates_to_dropdown()
        
    # Handle template selection
    def on_template_selected(self, index):
        if index <= 0:
            self.current_template_index = None
            self.clear_settings_fields()
            return
        
        # Load selected template settings into form fields
        self.current_template_index = index - 1
        template = self.attendance_templates[self.current_template_index]
        self.load_settings_to_fields(template.settings)    

    # Load settings dict into form fields
    def load_settings_to_fields(self, settings):
        
        self.company_codes_layout.load_settings(settings)
        
        # Set QLineEdit fields
        self.field_employee_id_col.setText(str(settings.get("employee_id_col", "")))
        self.field_employee_name_col.setText(str(settings.get("employee_name_col", "")))
        self.field_company_code_col.setText(str(settings.get("company_code_col", "")))
        self.field_data_start_row.setText(str(settings.get("data_start_row", "")))
        self.field_date_header_row.setText(str(settings.get("date_header_row", "")))
        self.field_row_counter_col.setText(str(settings.get("row_counter_col", "")))
        self.sheet_names_text_edit.setPlainText(settings.get("sheet_names", ""))
        self.ignore_list_text_edit.setPlainText(settings.get("ignore_list", ""))

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
        self.vm.update_template(self.current_template_index, name=name, template_type="attendance", settings=settings)
        self.load_templates_to_dropdown()
        dropdown.setCurrentIndex(index)

    # Create a new template from current form values
    def on_new_template(self):
        name, ok = QInputDialog.getText(self, "New Template", "Enter template name:")
        if not ok or not name.strip():
            return
        settings = self.collect_settings_from_fields()
        self.vm.add_template(name.strip(), "attendance", settings)
        self.load_templates_to_dropdown()
        # Optionally select the new template in dropdown
        dropdown = self.template_bar.template_dropdown
        for i in range(dropdown.count()):
            if dropdown.itemText(i) == name.strip():
                dropdown.setCurrentIndex(i)
                break

    # Gather all form field values into a settings dict
    def collect_settings_from_fields(self):
        settings = {}
        
        # Company codes
        settings["company_codes"] = self.company_codes_layout.get_company_codes()
        # QLineEdit fields (direct extraction)
        settings["employee_id_col"] = self.field_employee_id_col.text()
        settings["employee_name_col"] = self.field_employee_name_col.text()
        settings["company_code_col"] = self.field_company_code_col.text()
        settings["data_start_row"] = self.field_data_start_row.text()
        settings["date_header_row"] = self.field_date_header_row.text()
        settings["row_counter_col"] = self.field_row_counter_col.text()
        # Sheet names and ignore list
        settings["sheet_names"] = self.sheet_names_text_edit.toPlainText()
        settings["ignore_list"] = self.ignore_list_text_edit.toPlainText()
        return settings
    
    # Load templates from ViewModel into dropdown
    def load_templates_to_dropdown(self):
        dropdown = self.template_bar.template_dropdown
        dropdown.blockSignals(True)
        dropdown.clear()
        dropdown.addItem("Select Template")
        self.attendance_templates = self.vm.get_templates(template_type="attendance")
        for t in self.attendance_templates:
            dropdown.addItem(t.name)
        dropdown.blockSignals(False)

    # Clear all form fields
    def clear_settings_fields(self):
        self.company_codes_layout.clear_checked()
        self.field_employee_id_col.clear()
        self.field_employee_name_col.clear()
        self.field_company_code_col.clear()
        self.field_data_start_row.clear()
        self.field_date_header_row.clear()
        self.field_row_counter_col.clear()
        self.sheet_names_text_edit.clear()
        self.ignore_list_text_edit.clear()

    # Helper method to create QLineEdit fields
    def create_field(self, placeholder):
        """Helper method to create a plain input field for QFormLayout."""
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setFixedHeight(28)
        # Give each field a unique object name for easy lookup
        if not hasattr(self, '_field_count'):
            self._field_count = 0
        field.setObjectName(f"field_{self._field_count}")
        self._field_count += 1
        return field

    # Refactored method to configure date pickers
    def configure_date_picker(self, date_picker):
        """Configure a date picker to default to yesterday's date."""
        yesterday = QDate.currentDate().addDays(-1)
        date_picker.setDate(yesterday)
        date_picker.setCalendarPopup(True)  # Enable calendar popup for easier selection
