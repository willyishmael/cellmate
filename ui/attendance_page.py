from PySide6.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QWidget, 
    QSpacerItem, QSizePolicy, QFormLayout,
    QLineEdit, QCheckBox, QTextEdit ,QPushButton
)

from PySide6.QtCore import Qt, QDate
from ui.drop_area_view import DropArea
from ui.template_bar import TemplateBar
from ui.period_date_widget import PeriodDateWidget
from view_model.template_view_model import TemplateViewModel

class AttendancePage(QWidget):
    def __init__(self):
        super().__init__()
        self.vm = TemplateViewModel()
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

        company_codes_layout = QHBoxLayout()
        self.checkbox_pm = QCheckBox("PM")
        self.checkbox_ptm = QCheckBox("PTM")
        self.checkbox_tmp = QCheckBox("TMP")
        company_codes_layout.addWidget(self.checkbox_pm)
        company_codes_layout.addWidget(self.checkbox_ptm)
        company_codes_layout.addWidget(self.checkbox_tmp)
        form_layout.addRow("Company Codes:", company_codes_layout)

        form_layout.addRow("Employee ID Column:", self.create_field("Enter Employee ID Column Index (e.g., 5)"))
        form_layout.addRow("Employee Name Column:", self.create_field("Enter Employee Name Column Index (e.g., 6)"))
        form_layout.addRow("Company Code Column:", self.create_field("Enter Company Code Column Index (e.g., 7)"))
        form_layout.addRow("Data Start Row:", self.create_field("Enter Data Start Row Index (e.g., 2)"))
        form_layout.addRow("Date Header Row:", self.create_field("Enter Date Header Row Index (e.g., 1)"))
        form_layout.addRow("Row Counter Column:", self.create_field("Enter Row Counter Column Index (e.g., 3)"))

        self.sheet_names_text_edit = QTextEdit()
        self.sheet_names_text_edit.setPlaceholderText("Enter sheet names separated by commas (e.g., Sheet1, Sheet2)")
        self.sheet_names_text_edit.setFixedHeight(60)
        form_layout.addRow("Sheet Names:", self.sheet_names_text_edit)

        self.employee_ids_text_edit = QTextEdit()
        self.employee_ids_text_edit.setPlaceholderText("Enter Employee IDs to ignore, separated by commas (e.g., OBI-212365, OBI-7565324)")
        self.employee_ids_text_edit.setFixedHeight(60)
        form_layout.addRow("Ignore List:", self.employee_ids_text_edit)

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
        self.load_templates_to_dropdown()
        
    # 
    def on_template_selected(self, index):
        if index <= 0:
            self.current_template_index = None
            self.clear_settings_fields()
            return
        
        
        self.current_template_index = index - 1
        template = self.attendance_templates[self.current_template_index]
        self.load_settings_to_fields(template.settings)    

    def on_save_template(self):
        # Save/update the currently selected template with current form values
        dropdown = self.template_bar.template_dropdown
        index = dropdown.currentIndex()
        if index <= 0 or self.current_template_index is None:
            # No template selected
            return
        name = dropdown.currentText()
        settings = self.collect_settings_from_fields()
        self.vm.update_template(self.current_template_index, name=name, template_type="attendance", settings=settings)
        self.load_templates_to_dropdown()
        dropdown.setCurrentIndex(index)

    def on_new_template(self):
        # Create a new template from current form values
        dropdown = self.template_bar.template_dropdown
        name = dropdown.currentText()
        if not name or name == "Select Template":
            # Optionally prompt for a name here
            return
        settings = self.collect_settings_from_fields()
        self.vm.add_template(name, "attendance", settings)
        self.load_templates_to_dropdown()
        # Optionally select the new template

    def collect_settings_from_fields(self):
        # Gather all form field values into a settings dict
        settings = {}
        # Period and dates
        settings["period"] = self.period_date_widget.period_dropdown.currentText()
        settings["start_date"] = self.period_date_widget.start_date_picker.date().toString("yyyy-MM-dd")
        settings["end_date"] = self.period_date_widget.end_date_picker.date().toString("yyyy-MM-dd")
        # Company codes
        settings["company_codes"] = {
            "PM": self.checkbox_pm.isChecked(),
            "PTM": self.checkbox_ptm.isChecked(),
            "TMP": self.checkbox_tmp.isChecked(),
        }
        # QLineEdit fields
        keys = ["employee_id_col", "employee_name_col", "company_code_col", "data_start_row", "date_header_row", "row_counter_col"]
        for i, key in enumerate(keys):
            field = self.findChild(QLineEdit, f"field_{i}")
            if field:
                settings[key] = field.text()
        # Sheet names and ignore list
        settings["sheet_names"] = self.sheet_names_text_edit.toPlainText()
        settings["ignore_list"] = self.employee_ids_text_edit.toPlainText()
        return settings
    
    def load_templates_to_dropdown(self):
        dropdown = self.template_bar.template_dropdown
        dropdown.blockSignals(True)
        dropdown.clear()
        dropdown.addItem("Select Template")
        self.attendance_templates = self.vm.get_templates(template_type="attendance")
        for t in self.attendance_templates:
            dropdown.addItem(t.name)
        dropdown.blockSignals(False)



    def clear_settings_fields(self):
        # Clear all form fields (implement as needed)
        self.period_dropdown.setCurrentIndex(0)
        self.start_date_picker.setDate(QDate.currentDate().addDays(-1))
        self.end_date_picker.setDate(QDate.currentDate().addDays(-1))
        self.checkbox_pm.setChecked(False)
        self.checkbox_ptm.setChecked(False)
        self.checkbox_tmp.setChecked(False)
        # Assuming fields are in order as created
        for i in range(6):
            field = self.findChild(QLineEdit, f"field_{i}")
            if field:
                field.clear()
        self.sheet_names_text_edit.clear()
        self.employee_ids_text_edit.clear()

    def load_settings_to_fields(self, settings):
        # Set form fields from settings dict
        self.period_date_widget.period_dropdown.setCurrentText(settings.get("period", ""))
        self.start_date_picker.setDate(QDate.fromString(settings.get("start_date", QDate.currentDate().addDays(-1).toString("yyyy-MM-dd")), "yyyy-MM-dd"))
        self.end_date_picker.setDate(QDate.fromString(settings.get("end_date", QDate.currentDate().addDays(-1).toString("yyyy-MM-dd")), "yyyy-MM-dd"))
        self.checkbox_pm.setChecked(settings.get("company_codes", {}).get("PM", False))
        self.checkbox_ptm.setChecked(settings.get("company_codes", {}).get("PTM", False))
        self.checkbox_tmp.setChecked(settings.get("company_codes", {}).get("TMP", False))
        # Set QLineEdit fields
        for i, key in enumerate(["employee_id_col", "employee_name_col", "company_code_col", "data_start_row", "date_header_row", "row_counter_col"]):
            field = self.findChild(QLineEdit, f"field_{i}")
            if field:
                field.setText(str(settings.get(key, "")))
        self.sheet_names_text_edit.setPlainText(settings.get("sheet_names", ""))
        self.employee_ids_text_edit.setPlainText(settings.get("ignore_list", ""))

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

    def configure_date_picker(self, date_picker):
        """Configure a date picker to default to yesterday's date."""
        yesterday = QDate.currentDate().addDays(-1)
        date_picker.setDate(yesterday)
        date_picker.setCalendarPopup(True)  # Enable calendar popup for easier selection
