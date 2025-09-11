
import os
import json
from model.template_model import Template, TemplateContainer

TEMPLATE_FILE = "templates.json"

class TemplateViewModel:
	def __init__(self):
		self.container = TemplateContainer()
		self.file_path = TEMPLATE_FILE
		self.load_templates()

	def load_templates(self):
		if os.path.exists(self.file_path):
			with open(self.file_path, 'r', encoding='utf-8') as f:
				json_str = f.read()
				self.container = TemplateContainer.from_json(json_str)
		else:
			self.container = TemplateContainer()

	def save_templates(self):
		with open(self.file_path, 'w', encoding='utf-8') as f:
			f.write(self.container.to_json())

	def get_templates(self, template_type=None):
		if template_type:
			return [t for t in self.container.templates if t.template_type == template_type]
		return self.container.templates

	def add_template(self, name, template_type, settings):
		new_template = Template(name=name, template_type=template_type, settings=settings)
		self.container.templates.append(new_template)
		self.save_templates()

	def update_template(self, index, name=None, template_type=None, settings=None):
		if 0 <= index < len(self.container.templates):
			t = self.container.templates[index]
			if name is not None:
				t.name = name
			if template_type is not None:
				t.template_type = template_type
			if settings is not None:
				t.settings = settings
			self.save_templates()

	def delete_template(self, index):
		if 0 <= index < len(self.container.templates):
			del self.container.templates[index]
			self.save_templates()

	def import_templates(self, import_path):
		with open(import_path, 'r', encoding='utf-8') as f:
			json_str = f.read()
			imported = TemplateContainer.from_json(json_str)
			self.container.templates.extend(imported.templates)
			self.save_templates()

	def export_templates(self, export_path):
		with open(export_path, 'w', encoding='utf-8') as f:
			f.write(self.container.to_json())
