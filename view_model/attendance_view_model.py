from model.attendance_extract import AttendanceExtract

class AttendanceViewModel:
    def __init__(self):
        self.attendance_data = []
        self.errors = []
        
    def extract_attendance(self, settings: dict, date_start_str: str, date_end_str: str, file: str):
        extractor = AttendanceExtract()
        try:
            extractor.extract(settings, date_start_str, date_end_str, file)
            self.attendance_data = extractor.data
            self.errors = []
        except Exception as e:
            self.attendance_data = []
            self.errors = [str(e)]