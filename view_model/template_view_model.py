from typing import Optional, Dict, List
from PySide6.QtCore import QObject, Signal
from model.template_model import Template, TemplateUtils

class TemplateViewModel(QObject):
	"""ViewModel for managing templates used across pages.

	Templates are identified by the pair (name, template_type). Names may be
	duplicated across different template_types, so callers should provide both
	values when updating or deleting templates.
	"""

	templates_changed = Signal()

	def __init__(self) -> None:
		super().__init__()
		self.templates: List[Template] = self.load_templates()

	def load_templates(self) -> List[Template]:
		return TemplateUtils.load_templates_from_file()

	def get_templates(self, template_type: Optional[str] = None) -> List[Template]:
		if template_type:
			return [t for t in self.templates if t.template_type == template_type]
		return self.templates

	def add_template(self, name: str, template_type: str, settings: dict) -> None:
		self.templates.append(Template(name, template_type, settings))
		self.save_templates()
		self.templates_changed.emit()

	def update_template(self,
		identifier: Dict[str, str],
		name: Optional[str] = None,
		template_type: Optional[str] = None,
		settings: Optional[dict] = None
  	) -> None:
		"""Update a template identified by a dict: {'name': <name>, 'template_type': <type>}.

		Raises ValueError if the identifier is invalid or the template is not found.
		"""
		if not isinstance(identifier, dict):
			raise ValueError("identifier must be a dict with keys 'name' and 'template_type'")

		name_key = identifier.get("name")
		type_key = identifier.get("template_type")
		if not name_key or not type_key:
			raise ValueError("Both 'name' and 'template_type' must be provided in identifier")

		idx = None
		for i, t in enumerate(self.templates):
			if t.name == name_key and t.template_type == type_key:
				idx = i
				break
		if idx is None:
			raise ValueError(f"Template not found: name={name_key}, template_type={type_key}")

		# perform update
		t = self.templates[idx]
		if name is not None:
			t.name = name
		if template_type is not None:
			t.template_type = template_type
		if settings is not None:
			t.settings = settings

		self.save_templates()
		self.templates_changed.emit()

	def delete_template(self, identifier: Dict[str, str]) -> None:
		"""Delete a template identified by {'name': <name>, 'template_type': <type>}.

		Raises ValueError if the identifier is invalid or template not found.
		"""
		if not isinstance(identifier, dict):
			raise ValueError("identifier must be a dict with keys 'name' and 'template_type'")

		name_key = identifier.get("name")
		type_key = identifier.get("template_type")
		if not name_key or not type_key:
			raise ValueError("Both 'name' and 'template_type' must be provided in identifier")

		idx = None
		for i, t in enumerate(self.templates):
			if t.name == name_key and t.template_type == type_key:
				idx = i
				break
		if idx is None:
			raise ValueError(f"Template not found: name={name_key}, template_type={type_key}")

		del self.templates[idx]
		self.save_templates()
		self.templates_changed.emit()

	def save_templates(self) -> None:
		TemplateUtils.save_templates_to_file(templates=self.templates)

	def export_templates(self, path: str) -> None:
		TemplateUtils.export_templates_to_file(path, self.templates)

	def import_templates(self, path: str) -> None:
		self.templates = TemplateUtils.import_templates_from_file(path)
		self.save_templates()
		self.templates_changed.emit()
