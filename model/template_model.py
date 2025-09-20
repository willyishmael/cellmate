import json
from typing import List, Dict, Any

class Template:
    def __init__(self, name: str, template_type: str, settings: Dict[str, Any]):
        self.name = name
        self.template_type = template_type  # e.g. "attendance", "overtime", etc.
        self.settings = settings

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        return Template(
            name=data.get('name', ''),
            template_type=data.get('template_type', ''),
            settings=data.get('settings', {})
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'template_type': self.template_type,
            'settings': self.settings
        }

# Utility methods for Template list <-> JSON file
class TemplateUtils:
    TEMPLATE_FILE = "data/templates.json"
    @staticmethod
    def load_templates_from_file(path: str = None) -> List[Template]:
        """Load templates from JSON file. Uses default TEMPLATE_FILE if path not provided."""
        if path is None:
            path = TemplateUtils.TEMPLATE_FILE
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict) and 'templates' in data:
                data = data['templates']
            return [Template.from_dict(t) for t in data]
        except Exception:
            return []

    @staticmethod
    def save_templates_to_file(path: str = None, templates: List[Template] = None):
        """Save templates to JSON file. Uses default TEMPLATE_FILE if path not provided."""
        if path is None:
            path = TemplateUtils.TEMPLATE_FILE
        with open(path, 'w', encoding='utf-8') as f:
            json.dump([t.to_dict() for t in templates], f, indent=2)

    @staticmethod
    def import_templates_from_file(path: str = None) -> List[Template]:
        """Import templates from JSON file. Uses default TEMPLATE_FILE if path not provided."""
        return TemplateUtils.load_templates_from_file(path)

    @staticmethod
    def export_templates_to_file(path: str = None, templates: List[Template] = None):
        """Export templates to JSON file. Uses default TEMPLATE_FILE if path not provided."""
        TemplateUtils.save_templates_to_file(path, templates)
