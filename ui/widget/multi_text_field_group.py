from PySide6.QtWidgets import QTextEdit

class MultiTextFieldGroup:
    def __init__(self, configs, parent_layout):
        self.configs = {}
        for attr, placeholder in configs.items():
            field = self.create_text_area(placeholder)
            key = self.snake_case(attr)
            self.configs[key] = placeholder
            setattr(self, f"field_{key}", field)
            parent_layout.addRow(f"{attr}:", field)
            
    def snake_case(self, text):
        return text.lower().replace(' ', '_')
    
    def for_each_field(self, callback):
        for key in self.configs.keys():
            field_name = f"field_{key}"
            field = getattr(self, field_name, None)
            if field:
                callback(key, field)
                
    def create_text_area(self, placeholder):
        text_area = QTextEdit()
        text_area.setPlaceholderText(placeholder)
        text_area.setFixedHeight(42)
        return text_area
    
    def load_settings(self, settings):
        def set_field(key, field):
            if key in settings:
                field.setPlainText(str(settings[key]))
        self.for_each_field(set_field)
        
    def clear_fields(self):
        self.for_each_field(lambda attr, field: field.clear())
        
    def get_field_values(self):
        values = {}
        def collect(key, field):
            values[key] = field.toPlainText().strip()
        self.for_each_field(collect)
        return values
    
    
                
    