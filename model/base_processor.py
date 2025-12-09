from abc import abstractmethod
from pathlib import Path
from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.worksheet import Worksheet

from model.data_class.settings import AttendanceSettings

class BaseProcessor:
    
    def apply_attendance_settings(self, settings: dict[str, any]) -> AttendanceSettings:
        """
        Apply or update settings before running processing.
        Should be called every time before extract/compare.
        Returns an AttendanceSettings object with parsed configuration.
        """
        
        def to_int(value, default):
            try:
                return int(value)
            except Exception:
                return default

        self.attendance_settings = AttendanceSettings(
            employee_id_col=to_int(settings.get("employee_id_column"), 2),
            employee_name_col=to_int(settings.get("employee_name_column"), 3),
            company_code_col=to_int(settings.get("company_code_column"), 5),
            data_start_row=to_int(settings.get("data_start_row"), 5),
            date_header_row=to_int(settings.get("date_header_row"), 4),
            row_counter_col=to_int(settings.get("row_counter_column"), 1),
            sheet_names=self._parse_comma_list(settings.get("sheet_names", "")),
            ignore_list=self._parse_comma_list(settings.get("ignore_list", "")),
            company_codes=settings.get("company_codes", {})
        )

        return self.attendance_settings
    
    
    def load_source_wb(self, file_path: str) -> Workbook:
        """Load Source Excel file. This will handle both attendance and overtime files."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        source_wb = load_workbook(path, data_only=True)
        return source_wb
    
    def load_hris_wb(self, hris_file: str) -> Workbook:
        """Load HRIS Excel file. This will handle both attendance and overtime HRIS files."""
        path = Path(hris_file)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        hris_wb = load_workbook(path, data_only=True)
        return hris_wb

    def get_output_dir(self, file_path: str) -> Path:
        """Return directory where output files should be saved."""
        return Path(file_path).parent

    def get_source_sheets(self, source_wb: Workbook, sheet_names: list[str]) -> list[Worksheet]:
        """Return sheet objects based on settings.sheet_names."""
        if not source_wb:
            raise ValueError("Workbook not loaded yet.")
        if not sheet_names:
            return [source_wb.active]
        return [source_wb[sheet] for sheet in sheet_names if sheet in source_wb.sheetnames]
    
    def get_hris_source_sheets(self, hris_wb: Workbook) -> list[Worksheet]:
        """Return sheet objects based on settings.sheet_names."""
        if not hris_wb: 
            raise ValueError("Workbook not loaded yet.")
        return [hris_wb[sheet] for sheet in hris_wb.sheetnames]
    
    def _map_status(self, code: str) -> tuple[str, str, str]:
        """Map attendance codes to descriptions and time ranges."""
        code = str(code).strip().upper()
        mapping = {
            "H":  ("Hadir (H)", "07:00", "18:00"),
            "HM": ("Hadir shift malam (HM)", "19:00", "06:00"),
            "A":  ("Alpa (A)", "", ""),
            "S":  ("Sakit (S)", "", ""),
            "I":  ("Izin (I)", "", ""),
            "HC": ("Cuti (C)", "", ""),
            "DLK":("Dinas Luar Kota (DLK)", "", ""),
            "OFF":("OFF", "", ""),
        }
        return mapping.get(code, (code, "", ""))
    
    def _parse_comma_list(self, value: str) -> list[str]:
        """Convert comma-separated text into a list of trimmed strings."""
        if not value:
            return []
        return [x.strip() for x in value.split(",") if x.strip()]