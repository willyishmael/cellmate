from PySide6.QtWidgets import QTextEdit

class MultiTextFieldGroup:
    """A group of multi-line text fields based on provided configurations."""
    
    def __init__(self, configs, parent_layout):
        self.configs = {}
        self.required_fields = ["sheet_names"]
        
        for attr, placeholder in configs.items():
            field = self.create_text_area(placeholder)
            key = self.snake_case(attr)
            self.configs[key] = placeholder
            setattr(self, f"field_{key}", field)
            parent_layout.addRow(f"{attr}:", field)
            
    def snake_case(self, text):
        """Convert text to snake_case."""
        return text.lower().replace(' ', '_')
    
    def for_each_field(self, callback):
        """Apply a callback to each text area field."""
        for key in self.configs.keys():
            field_name = f"field_{key}"
            field = getattr(self, field_name, None)
            if field:
                callback(key, field)
                
    def create_text_area(self, placeholder):
        """Create and return a QTextEdit with specified placeholder."""
        text_area = QTextEdit()
        text_area.setPlaceholderText(placeholder)
        text_area.setFixedHeight(42)
        return text_area
    
    def load_settings(self, settings):
        """Load settings dict to populate text areas."""
        def set_field(key, field):
            if key in settings:
                field.setPlainText(str(settings[key]))
        self.for_each_field(set_field)
        
    def clear_fields(self):
        """Clear all text areas."""
        self.for_each_field(lambda attr, field: field.clear())
        
    def get_field_values(self):
        """Return a dict of current text area values."""
        values = {}
        def collect(key, field):
            values[key] = field.toPlainText().strip()
        self.for_each_field(collect)
        return values
    
    def validate_fields(self):
        """Validate required fields are filled."""
        for key in self.configs.keys():
            field_name = f"field_{key}"
            field = getattr(self, field_name, None)
            if field and field.toPlainText().strip() == "" and key in self.required_fields:
                return False, f"Please fill in the '{self.configs[key]}' field."
        return True, ""
    