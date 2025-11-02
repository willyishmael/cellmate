from PySide6.QtWidgets import (
    QMainWindow, QWidget, QStackedWidget, QTabWidget,
    QVBoxLayout
)

from ui.page.attendance_page import AttendancePage
from ui.page.overtime_page import OvertimePage
from ui.page.attendance_optdrv_page import AttendanceOptDrvPage
from ui.page.overtime_optdrv_page import OvertimeOptDrvPage
from ui.page.template_page import TemplatePage
from ui.page.app_info_page import AppInfoPage
from view_model.template_view_model import TemplateViewModel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cellmate")
        self.setGeometry(200, 200, 800, 600)

        # Central widget with stacked pages
        self.stacked = QStackedWidget()

        # Placeholder pages
        self.template_vm = TemplateViewModel()
        self.attendance_page = AttendancePage(self.template_vm)
        self.overtime_page = OvertimePage(self.template_vm)
        self.attendance_optdrv_page = AttendanceOptDrvPage(self.template_vm)
        self.overtime_optdrv_page = OvertimeOptDrvPage(self.template_vm)
        self.templates_page = TemplatePage(self.template_vm)
        self.app_info_page = AppInfoPage()

        self.stacked.addWidget(self.attendance_page)  # index 0
        self.stacked.addWidget(self.overtime_page)    # index 1
        self.stacked.addWidget(self.attendance_optdrv_page)  # index 2
        self.stacked.addWidget(self.overtime_optdrv_page)    # index 3
        self.stacked.addWidget(self.templates_page)   # index 4
        self.stacked.addWidget(self.app_info_page)    # index 5

        # Replace navigation layout with QTabWidget
        self.tabs = QTabWidget()
        self.tabs.addTab(self.attendance_page, "Attendance")
        self.tabs.addTab(self.overtime_page, "Overtime")
        self.tabs.addTab(self.attendance_optdrv_page, "Attendance OPTDRV")
        self.tabs.addTab(self.overtime_optdrv_page, "Overtime OPTDRV")
        self.tabs.addTab(self.templates_page, "Templates")
        self.tabs.addTab(self.app_info_page, "App Info")

        # Set up the main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)

        main_container = QWidget()
        main_container.setLayout(main_layout)
        self.setCentralWidget(main_container)
