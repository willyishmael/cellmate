from PySide6.QtWidgets import QWidget, QCheckBox, QHBoxLayout, QMessageBox

class CompanyCodeCheckbox(QWidget):
    """A widget containing checkboxes for company codes PM, PTM, and TMP."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.company_codes_layout = QHBoxLayout()
        self.checkbox_pm = QCheckBox("PM")
        self.checkbox_ptm = QCheckBox("PTM")
        self.checkbox_tmp = QCheckBox("TMP")
        self.company_codes_layout.addWidget(self.checkbox_pm)
        self.company_codes_layout.addWidget(self.checkbox_ptm)
        self.company_codes_layout.addWidget(self.checkbox_tmp)
        self.setLayout(self.company_codes_layout)
        
    def load_settings(self, settings):
        """Load settings dict to set checkbox states."""
        self.company_codes = settings.get("company_codes", {})
        self.checkbox_pm.setChecked(self.company_codes.get("PM", False))
        self.checkbox_ptm.setChecked(self.company_codes.get("PTM", False))
        self.checkbox_tmp.setChecked(self.company_codes.get("TMP", False))
        
    def clear_checked(self):
        """Clear all checkboxes."""
        self.checkbox_pm.setChecked(False)
        self.checkbox_ptm.setChecked(False)
        self.checkbox_tmp.setChecked(False)
        
    def get_company_codes(self):
        """Return a dict of the current checkbox states."""
        return {"company_codes": {
            "PM": self.checkbox_pm.isChecked(),
            "PTM": self.checkbox_ptm.isChecked(),
            "TMP": self.checkbox_tmp.isChecked()
        }}
        
    def has_checked_codes(self):
        """Return True if any checkbox is checked."""
        has_checked = (self.checkbox_pm.isChecked() or 
                self.checkbox_ptm.isChecked() or 
                self.checkbox_tmp.isChecked())
        
        if not has_checked:
            return False, "Please select at least one company code."
            
        return True, ""