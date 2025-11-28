from typing import Optional
from model.overtime_optdrv.overtime_optdrv_comparator import OvertimeOptdrvComparator
from model.overtime_optdrv.overtime_optdrv_extractor import OvertimeOptdrvExtractor
from model.result import Result

class OvertimeOptDrvViewModel():
    def __init__ (
        self,
        extractor: Optional[OvertimeOptdrvExtractor] = None,
        comparator: Optional[OvertimeOptdrvComparator] = None
    ):
        self.overtime_data: list = []
        self.errors: list[str] = []
        self.extractor = extractor or OvertimeOptdrvExtractor()
        self.comparator = comparator or OvertimeOptdrvComparator()
        
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
