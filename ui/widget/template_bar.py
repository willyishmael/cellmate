from PySide6.QtWidgets import QHBoxLayout, QComboBox, QPushButton

class TemplateBar(QHBoxLayout):
    def __init__(self, on_template_selected=None):
        super().__init__()
        self.template_dropdown = QComboBox()
        self.template_dropdown.addItem("Select Template")
        
        if on_template_selected:
            self.template_dropdown.currentIndexChanged.connect(on_template_selected)
        
        self.btn_save = QPushButton("💾 Save")
        self.btn_new = QPushButton("➕ New")
        
        self.addWidget(self.template_dropdown, 3)
        self.addWidget(self.btn_save, 1)
        self.addWidget(self.btn_new, 1)
