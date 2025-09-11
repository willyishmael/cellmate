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

class TemplateContainer:
    def __init__(self):
        self.templates: List[Template] = []

    @staticmethod
    def from_json(json_str: str):
        data = json.loads(json_str)
        container = TemplateContainer()
        for t in data.get('templates', []):
            container.templates.append(Template.from_dict(t))
        return container

    def to_json(self) -> str:
        data = {
            'templates': [t.to_dict() for t in self.templates]
        }
        return json.dumps(data, indent=2)
