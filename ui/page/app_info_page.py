from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QThread, Signal

from model.helper.app_data import user_templates_path
from model.helper.update_checker import compare_versions, fetch_latest_release
from model.version import get_version

class AppInfoPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignTop)

        app_version = get_version()
        templates_path = str(user_templates_path())

        title = QLabel("Application Information")
        title.setStyleSheet("font-weight: bold; font-size: 18px;")
        title.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(title)

        tagline = QLabel("Process attendance, overtime, and optional drive data with reusable templates.")
        tagline.setStyleSheet("font-size: 13px")
        tagline.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        tagline.setWordWrap(True)
        layout.addWidget(tagline)

        info = QLabel()
        info.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        info.setStyleSheet("font-size: 13px; line-height: 1.45;")
        info.setWordWrap(True)
        info.setText(
            f"<b>Version</b><br>{app_version}<br><br>"
            "<b>Author</b><br>William Tangka<br><br>"
            "<b>Contact</b><br>wtangka22@gmail.com<br><br>"
            "<b>Key features</b><br>"
            "- Excel import and export for attendance, overtime, OPTDRV<br>"
            "- Template management with reusable presets<br>"
            "- Company code detection in sheet titles<br>"
            "- Robust date parsing and safe save fallback for Excel<br><br>"
            "<b>Where templates are stored</b><br>"
            f"{templates_path}<br><br>"
            "<b>Tips</b><br>"
            "- First launch copies bundled templates here if missing<br>"
            "- Export/import templates from the Templates tab to share presets<br>"
            "- Keep source files in .xlsx (convert .xls/.xlsb before processing)"
        )
        layout.addWidget(info)

        self.status_label = QLabel("Status: Not checked")
        self.status_label.setStyleSheet("font-size: 12px; color: #555;")
        self.status_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        self.check_button = QPushButton("Check for updates")
        self.check_button.setStyleSheet("padding: 6px 10px;")
        self.check_button.clicked.connect(self._on_check_updates)
        layout.addWidget(self.check_button)

        self.setLayout(layout)

        # Keep references
        self._app_version = app_version
        self._worker = None

    def _set_status(self, html: str, color: str, open_links: bool = False):
        self.status_label.setText(html)
        self.status_label.setStyleSheet(f"font-size: 12px; color: {color};")
        self.status_label.setOpenExternalLinks(open_links)

    def _on_check_updates(self):
        if self._worker and self._worker.isRunning():
            return
        self._set_status("Checking for updates...", "#555")
        self.check_button.setEnabled(False)
        self._worker = _UpdateCheckWorker(self._app_version)
        self._worker.result.connect(self._on_update_result)
        self._worker.error.connect(self._on_update_error)
        self._worker.finished.connect(lambda: self.check_button.setEnabled(True))
        self._worker.start()

    def _on_update_result(self, status: str, latest_version: str, url: str):
        if status == "update":
            # Needs update: orange
            self._set_status(
                f"Update available: {latest_version} — <a href='{url}'>Get it on GitHub</a>",
                "#ff8c00",
                True,
            )
        elif status == "current":
            # Current: green
            self._set_status(
                f"You are up to date. (Current: {self._app_version}, Latest: {latest_version})",
                "#2e7d32",
                False,
            )
        elif status == "ahead":
            # Ahead (development build): yellow
            self._set_status(
                f"Ahead of latest release (Current: {self._app_version}, Latest: {latest_version}).",
                "#c9a700",
                False,
            )
        else:
            # Unknown state
            self._set_status(
                f"Could not determine update status. Latest reported: {latest_version}",
                "#555",
                False,
            )

    def _on_update_error(self, message: str):
        self._set_status(f"Update check failed: {message}", "#d24646", False)


class _UpdateCheckWorker(QThread):
    result = Signal(str, str, str)  # status, latest_version, url
    error = Signal(str)

    def __init__(self, current_version: str):
        super().__init__()
        self._current_version = current_version

    def run(self):
        try:
            latest, url = fetch_latest_release()
            cmp_result = compare_versions(self._current_version, latest)
            if cmp_result < 0:
                self.result.emit("update", latest, url)
            elif cmp_result == 0:
                self.result.emit("current", latest, url)
            else:
                self.result.emit("ahead", latest, url)
        except Exception as e:  # pragma: no cover - UI thread error surface
            self.error.emit(str(e))