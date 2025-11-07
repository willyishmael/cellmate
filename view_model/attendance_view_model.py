from model.attendance.attendance_extractor import AttendanceExtractor
from model.attendance.attendance_comparator import AttendanceComparator
from model.result import Result

class AttendanceViewModel:
    def __init__(self, extractor: AttendanceExtractor = None, comparator: AttendanceComparator = None):
        self.attendance_data = []
        self.errors = []
        self.extractor = extractor or AttendanceExtractor()
        self.comparator = comparator or AttendanceComparator()

    def extract_attendance(self, settings: dict, date_start_str: str, date_end_str: str, file: str) -> Result:
        try:
            self.extractor.extract(settings, date_start_str, date_end_str, file)
            self.errors = []
            return Result(success=True, data=[])
        except Exception as e:
            self.attendance_data = []
            self.errors = [str(e)]
            return Result(success=False, data=[], message=str(e))

    def compare_attendance(self, settings: dict, date_start_str: str, date_end_str: str, attendance_file: str, hris_file: str) -> Result:
        try:
            self.comparator.compare(settings, date_start_str, date_end_str, attendance_file, hris_file)
            self.errors = []
            return Result(success=True, data=[])
        except Exception as e:
            self.attendance_data = []
            self.errors = [str(e)]
            return Result(success=False, data=[], message=str(e))
    