from PySide6.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QWidget, 
    QPushButton, QSpacerItem, QSizePolicy, QComboBox, QFormLayout,
    QLineEdit, QCheckBox, QDateEdit, QTextEdit
)
from PySide6.QtCore import Qt, QDate
from ui.drop_area_view import DropArea
from ui.period_dropdown import PeriodDropdown

class OvertimePage(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QHBoxLayout()

        # Left panel with two drop areas
        left_panel = QVBoxLayout()

        self.drop_area_1 = DropArea("Drop Attendance Excel File Here")
        self.drop_area_2 = DropArea("Drop HRIS Export Excel File Here")

        left_panel.addWidget(self.drop_area_1, 1)  # stretch factor = 1
        left_panel.addWidget(self.drop_area_2, 1)  # stretch factor = 1

        main_layout.addLayout(left_panel, 2)  # stretch factor = 2

        # Right panel (settings)
        right_panel = QVBoxLayout()

        self.setting_label = QLabel("⚙ Settings")
        self.setting_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        right_panel.addWidget(self.setting_label)

        # 🔹 Template selection bar (dropdown + buttons)
        template_bar = QHBoxLayout()

        self.template_dropdown = QComboBox()
        self.template_dropdown.addItem("Select Template")  # default placeholder
        template_bar.addWidget(self.template_dropdown, 3)  # stretch factor = 3

        self.btn_save = QPushButton("💾 Save")
        self.btn_new = QPushButton("➕ New")
        self.btn_delete = QPushButton("🗑 Delete")

        template_bar.addWidget(self.btn_save, 1)
        template_bar.addWidget(self.btn_new, 1)
        template_bar.addWidget(self.btn_delete, 1)

        right_panel.addLayout(template_bar)

        # Form layout for labeled fields
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)  # Labels aligned neatly on right
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_layout.setFormAlignment(Qt.AlignTop)
        form_layout.setHorizontalSpacing(15)
        form_layout.setVerticalSpacing(15)

        # Add period dropdown
        self.period_dropdown = PeriodDropdown()
        self.period_dropdown.setFixedHeight(28)  # Set height to 28
        form_layout.addRow("Period:", self.period_dropdown)

        # Add date pickers for start and end dates
        self.start_date_picker = QDateEdit()
        self.end_date_picker = QDateEdit()
        self.configure_date_picker(self.start_date_picker)
        self.configure_date_picker(self.end_date_picker)

        self.start_date_picker.setFixedHeight(28)  # Set height to 28
        self.end_date_picker.setFixedHeight(28)  # Set height to 28

        form_layout.addRow("Start Date:", self.start_date_picker)
        form_layout.addRow("End Date:", self.end_date_picker)

        # Add fields for user input
        company_codes_layout = QHBoxLayout()
        company_codes_layout.setAlignment(Qt.AlignLeft)
        self.checkbox_pm = QCheckBox("PM")
        self.checkbox_ptm = QCheckBox("PTM")
        self.checkbox_tmp = QCheckBox("TMP")
        company_codes_layout.addWidget(self.checkbox_pm)
        company_codes_layout.addWidget(self.checkbox_ptm)
        company_codes_layout.addWidget(self.checkbox_tmp)
        form_layout.addRow("Company Codes:", company_codes_layout)
        
        form_layout.addRow("Employee ID Column:", self.create_field("Enter Employee ID Column Index (e.g., 5)"))
        form_layout.addRow("Data Start Row:", self.create_field("Enter Data Start Row Index (e.g., 2)"))
        form_layout.addRow("Row Counter Column:", self.create_field("Enter Row Counter Column Index (e.g., 1)"))

        # Add text edit for sheet names
        # Suggestion: Clarify placeholder text to indicate format
        self.sheet_names_text_edit = QTextEdit()
        self.sheet_names_text_edit.setPlaceholderText("Enter sheet names separated by commas (e.g., Sheet1, Sheet2)")
        self.sheet_names_text_edit.setFixedHeight(60)  # Set height to 60
        form_layout.addRow("Sheet Names:", self.sheet_names_text_edit)

        # Add text edit for ignore list (Employee IDs)
        # Suggestion: Clarify placeholder text to indicate format
        self.employee_ids_text_edit = QTextEdit()
        self.employee_ids_text_edit.setPlaceholderText("Enter Employee IDs to ignore, separated by commas (e.g., OBI-212365, OBI-7565324)")
        self.employee_ids_text_edit.setFixedHeight(60)  # Set height to 60
        form_layout.addRow("Ignore List:", self.employee_ids_text_edit)

        right_panel.addLayout(form_layout)

        # Add spacer so button goes to bottom
        right_panel.addItem(QSpacerItem(20, 200, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Action button
        btn_extract = QPushButton("📊 Extract Data")
        btn_compare = QPushButton("🔍 Compare Data")
        btn_extract.setFixedHeight(40)
        btn_compare.setFixedHeight(40)
        right_panel.addWidget(btn_extract)
        right_panel.addWidget(btn_compare)

        # Add right panel to main layout
        main_layout.addLayout(right_panel, 3)  # stretch factor = 3

        self.setLayout(main_layout)

    def create_field(self, placeholder):
        """Helper method to create a plain input field for QFormLayout."""
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setFixedHeight(28)
        return field

    def configure_date_picker(self, date_picker):
        """Configure a date picker to default to yesterday's date."""
        yesterday = QDate.currentDate().addDays(-1)
        date_picker.setDate(yesterday)
        date_picker.setCalendarPopup(True)  # Enable calendar popup for easier selection
