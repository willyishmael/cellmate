from PySide6.QtWidgets import QHBoxLayout, QFormLayout, QWidget
from PySide6.QtCore import Qt, QDate
from ui.widget.period_dropdown import PeriodDropdown
from PySide6.QtWidgets import QDateEdit

class PeriodDateWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout()
        layout.setLabelAlignment(Qt.AlignRight)
        layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        layout.setFormAlignment(Qt.AlignTop)
        layout.setHorizontalSpacing(15)
        layout.setVerticalSpacing(15)

        self.period_dropdown = PeriodDropdown()
        self.period_dropdown.setFixedHeight(28)
        layout.addRow("Period:", self.period_dropdown)

        self.start_date_picker = QDateEdit()
        self.end_date_picker = QDateEdit()
        self.configure_date_picker(self.start_date_picker)
        self.configure_date_picker(self.end_date_picker)
        self.start_date_picker.setFixedHeight(28)
        self.end_date_picker.setFixedHeight(28)
        layout.addRow("Start Date:", self.start_date_picker)
        layout.addRow("End Date:", self.end_date_picker)

        self.setLayout(layout)

    def configure_date_picker(self, date_picker):
        yesterday = QDate.currentDate().addDays(-1)
        date_picker.setDate(yesterday)
        date_picker.setCalendarPopup(True)
