from PySide6.QtWidgets import QLineEdit

class FormFieldGroup:

    def __init__(self, field_configs, parent_layout):
        self.field_configs = field_configs
        for attr, placeholder in field_configs.items():
            field = self.create_fields(placeholder)
            setattr(self, f"field_{attr.lower().replace(' ', '_')}", field)
            parent_layout.addRow(f"{attr}:", field)
    
    def for_each_field(self, callback):
        for attr in self.field_configs.keys():
            field_name = f"field_{attr.lower().replace(' ', '_')}"
            field = getattr(self, field_name, None)
            if field:
                callback(attr, field)
    
    def create_fields(self, placeholder):
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setFixedHeight(28)
        return field
    
    def load_settings(self, settings):
        def set_field(attr, field):
            if attr in settings:
                field.setText(str(settings[attr]))
        self.for_each_field(set_field)
                
    def clear_fields(self):
        self.for_each_field(lambda attr, field: field.clear())
                
    def get_field_values(self):
        values = {}
        def collect(attr, field):
            values[attr] = field.text().strip()
        self.for_each_field(collect)
        return values