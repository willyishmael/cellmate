from PySide6.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QWidget, 
    QPushButton, QSpacerItem, QSizePolicy, QFormLayout, QCheckBox,
)
from PySide6.QtCore import Qt
from ui.widget.company_code_checkbox import CompanyCodeCheckbox
from ui.widget.drop_area_view import DropArea
from ui.widget.form_field_group import FormFieldGroup
from ui.widget.multi_text_field_group import MultiTextFieldGroup
from ui.widget.period_date_widget import PeriodDateWidget
from ui.widget.template_bar import TemplateBar

class AttendanceOptDrvPage(QWidget):
    def __init__(self, template_vm):
        super().__init__()
        self.template_vm = template_vm
        # self.attendance_vm = AttendanceOptDrvViewModel()
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
        setting_label = QLabel("⚙ Settings")
        setting_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        right_panel.addWidget(setting_label)

        # Template selection bar (refactored)
        self.template_bar = TemplateBar(self.on_template_selected)
        self.template_bar.btn_save.clicked.connect(self.on_save_template)
        self.template_bar.btn_new.clicked.connect(self.on_new_template)
        
        # Wrap TemplateBar (QHBoxLayout) in QWidget for addLayout compatibility
        template_bar_widget = QWidget()
        template_bar_widget.setLayout(self.template_bar)
        right_panel.addWidget(template_bar_widget)
        
        # Form layout for labeled fields
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_layout.setFormAlignment(Qt.AlignTop)
        form_layout.setHorizontalSpacing(15)
        form_layout.setVerticalSpacing(15)

        # Add period dropdown
        self.period_date_widget = PeriodDateWidget()
        form_layout.addRow(self.period_date_widget)
    
        # Add company codes checkbox layout
        self.company_codes_layout = CompanyCodeCheckbox()
        form_layout.addRow("Company Codes:", self.company_codes_layout)

        # Setup form field groups
        field_configs = {
            "Employee ID Column": "Enter Employee ID Column Index (e.g., 5)",
            "Employee Name Column": "Enter Employee Name Column Index (e.g., 6)",
            "Company Code Column": "Enter Company Code Column Index (e.g., 7)",
            "Data Start Row": "Enter Data Start Row Index (e.g., 2)",
            "Date Header Row": "Enter Date Header Row Index (e.g., 1)",
            "Row Counter Column": "Enter Row Counter Column Index (e.g., 3)",
        }
        self.form_field_group = FormFieldGroup(field_configs, form_layout)
        
        # Setup multi-line text field group
        edit_text_configs = {
            "Sheet Names": "Enter sheet names separated by commas (e.g., Sheet1, Sheet2)",
        }
        self.multi_text_field_group = MultiTextFieldGroup(edit_text_configs, form_layout)
        
        # Add "Time Off Only?" checkbox
        self.checkbox_time_off_only = QCheckBox("Time Off Only")
        form_layout.addRow("", self.checkbox_time_off_only)
        
        right_panel.addLayout(form_layout)
        right_panel.addItem(QSpacerItem(20, 200, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Action button
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

    def on_template_selected(self, index):
        # TODO: Implement template selection logic
        pass
    
    def on_save_template(self):
        # TODO: Implement save template logic
        pass

    def on_new_template(self):
        # TODO: Implement new template logic
        pass
    
    def on_extract(self):
        # TODO: Implement extract logic
        pass
    
    def on_compare(self):
        # TODO: Implement compare logic
        pass
    
    def load_templates_to_dropdown(self):
        # TODO: Implement loading templates to dropdown logic
        pass