from PySide6.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QWidget, 
    QSpacerItem, QSizePolicy, QFormLayout,
    QLineEdit, QTextEdit ,QPushButton,
    QInputDialog, QMessageBox
)

from PySide6.QtCore import Qt, QDate
from ui.widget.drop_area_view import DropArea
from ui.widget.template_bar import TemplateBar
from ui.widget.period_date_widget import PeriodDateWidget
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

        # Define field labels and placeholders
        self.field_configs = {
            "Employee ID Column": "Enter Employee ID Column Index (e.g., 5)",
            "Employee Name Column": "Enter Employee Name Column Index (e.g., 6)",
            "Company Code Column": "Enter Company Code Column Index (e.g., 7)",
            "Data Start Row": "Enter Data Start Row Index (e.g., 2)",
            "Date Header Row": "Enter Date Header Row Index (e.g., 1)",
            "Row Counter Column": "Enter Row Counter Column Index (e.g., 3)",
        }
        
        for label, placeholder in self.field_configs.items():
            field = self.create_field(placeholder)
            form_layout.addRow(f"{label}:", field)
            setattr(self, f"field_{label.lower().replace(' ', '_')}", field)

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
        
        # Set QLineEdit fields based on field_configs
        for attr in self.field_configs.keys():
            field_name = f"field_{attr.lower().replace(' ', '_')}"
            field = getattr(self, field_name, None)
            if field and attr in settings:
                field.setText(str(settings[attr]))
        
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
        
        # QLineEdit fields based on field_configs
        for attr in self.field_configs.keys():
            field_name = f"field_{attr.lower().replace(' ', '_')}"
            field = getattr(self, field_name, None)
            if field:
                settings[attr] = field.text().strip()
                
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
        
        for attr in self.field_configs.keys():
            field_name = f"field_{attr.lower().replace(' ', '_')}"
            field = getattr(self, field_name, None)
            if field:
                field.clear()
                
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
        date_picker.setCalendarPopup(True)
