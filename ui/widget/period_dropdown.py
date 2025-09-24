
from PySide6.QtWidgets import QComboBox
from datetime import datetime, timedelta

class PeriodDropdown(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.populate_period_dropdown()

    def populate_period_dropdown(self):
        """Populate the dropdown with period options and auto-select the appropriate period."""
        today = datetime.now()
        yesterday = today - timedelta(days=1)

        # Determine the current period based on yesterday's date
        if yesterday.day >= 26:
            start_month = yesterday.month
            start_year = yesterday.year
            end_month = (yesterday.month % 12) + 1
            end_year = yesterday.year if yesterday.month < 12 else yesterday.year + 1
        else:
            start_month = (yesterday.month - 2) % 12 + 1
            start_year = yesterday.year if yesterday.month > 1 else yesterday.year - 1
            end_month = yesterday.month
            end_year = yesterday.year

        # Generate the period string
        current_period = f"{datetime(start_year, start_month, 1).strftime('%B')} to {datetime(end_year, end_month, 1).strftime('%B')}"

        # Populate the dropdown with the current and previous periods
        self.addItem(current_period)
        for i in range(1, 12):  # Add up to 12 previous periods
            start_date = datetime(start_year, start_month, 1) - timedelta(days=1)
            end_date = datetime(end_year, end_month, 1) - timedelta(days=1)
            start_month = start_date.month
            start_year = start_date.year
            end_month = end_date.month
            end_year = end_date.year
            period = f"{datetime(start_year, start_month, 1).strftime('%B')} to {datetime(end_year, end_month, 1).strftime('%B')}"
            self.addItem(period)

        # Auto-select the first item (current period)
        self.setCurrentIndex(0)