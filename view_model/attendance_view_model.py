from model.attendance_extractor import AttendanceExtractor
from model.attendance_comparator import AttendanceComparator

class AttendanceViewModel:
    def __init__(self):
        self.attendance_data = []
        self.errors = []
        
    def extract_attendance(self, settings: dict, date_start_str: str, date_end_str: str, file: str):
        extractor = AttendanceExtractor()
        try:
            extractor.extract(settings, date_start_str, date_end_str, file)
            self.attendance_data = extractor.data
            self.errors = []
        except Exception as e:
            self.attendance_data = []
            self.errors = [str(e)]
    
    def compare_attendance(self, settings: dict, date_start_str: str, date_end_str: str, attendance_file: str, hris_file: str):
        comparator = AttendanceComparator()
        try:
            comparator.compare(settings, date_start_str, date_end_str, attendance_file, hris_file)
            self.attendance_data = comparator.comparison_results
            self.errors = []
        except Exception as e:
            self.attendance_data = []
            self.errors = [str(e)]
    