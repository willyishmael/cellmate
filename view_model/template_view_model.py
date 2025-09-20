from PySide6.QtCore import QObject, Signal
from model.template_model import Template, TemplateUtils

class TemplateViewModel(QObject):
	templates_changed = Signal()

	def __init__(self):
		super().__init__()
		self.templates = self.load_templates()

	def load_templates(self):
		return TemplateUtils.load_templates_from_file()

	def get_templates(self, template_type=None):
		if template_type:
			return [t for t in self.templates if t.template_type == template_type]
		return self.templates

	def add_template(self, name, template_type, settings):
		self.templates.append(Template(name, template_type, settings))
		self.save_templates()
		self.templates_changed.emit()

	def update_template(self, index, name=None, template_type=None, settings=None):
		t = self.templates[index]
		if name is not None:
			t.name = name
		if template_type is not None:
			t.template_type = template_type
		if settings is not None:
			t.settings = settings
		self.save_templates()
		self.templates_changed.emit()

	def delete_template(self, index):
		del self.templates[index]
		self.save_templates()
		self.templates_changed.emit()

	def save_templates(self):
		TemplateUtils.save_templates_to_file(templates=self.templates)

	def export_templates(self, path):
		TemplateUtils.export_templates_to_file(path, self.templates)

	def import_templates(self, path):
		self.templates = TemplateUtils.import_templates_from_file(path)
		self.save_templates()
		self.templates_changed.emit()
