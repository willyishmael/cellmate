from PySide6.QtWidgets import QLineEdit

class FormFieldGroup:

    def __init__(self, field_configs, parent_layout):
        self.field_configs = {}
        for attr, placeholder in field_configs.items():
            field = self.create_fields(placeholder)
            key = self.snake_case(attr)
            self.field_configs[key] = placeholder
            setattr(self, f"field_{key}", field)
            parent_layout.addRow(f"{attr}:", field)
    
    def snake_case(self, text):
        return text.lower().replace(' ', '_')
    
    def for_each_field(self, callback):
        for key in self.field_configs.keys():
            field_name = f"field_{key}"
            field = getattr(self, field_name, None)
            if field:
                callback(key, field)
    
    def create_fields(self, placeholder):
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setFixedHeight(28)
        return field
    
    def load_settings(self, settings):
        def set_field(key, field):
            if key in settings:
                field.setText(str(settings[key]))
        self.for_each_field(set_field)
                
    def clear_fields(self):
        self.for_each_field(lambda attr, field: field.clear())
                
    def get_field_values(self):
        values = {}
        def collect(key, field):
            values[key] = field.text().strip()
        self.for_each_field(collect)
        return values