from typing import Optional
from model.overtime.overtime_comparator import OvertimeComparator
from model.overtime.overtime_extractor import OvertimeExtractor
from model.result import Result

class OvertimeViewModel():
    def __init__ (
        self,
        extractor: Optional[OvertimeExtractor] = None,
        comparator: Optional[OvertimeComparator] = None
    ):
        self.overtime_data: list = []
        self.errors: list[str] = []
        self.extractor = extractor or OvertimeExtractor()
        self.comparator = comparator or OvertimeComparator()
        
    def extract_overtime(
        self,
        settings: dict,
        date_start_str: str,
        date_end_str: str,
        overtime_file: str
    ) -> Result:
        try:
            self.extractor.extract(settings, date_start_str, date_end_str, overtime_file)
            self.errors = []
            return Result(success=True, data=[])
        except Exception as e:
            self.overtime_data = []
            self.errors = [str(e)]
            return Result(success=False, data=[], message=str(e))
        
    def compare_overtime(
        self,
        settings: dict,
        date_start_str: str,
        date_end_str: str,
        overtime_file: str,
        hris_file: str
    ) -> Result:
        try:
            self.comparator.compare(settings, date_start_str, date_end_str, overtime_file, hris_file)
            self.errors = []
            return Result(success=True, data=[])
        except Exception as e:
            self.overtime_data = []
            self.errors = [str(e)]
            return Result(success=False, data=[], message=str(e))
