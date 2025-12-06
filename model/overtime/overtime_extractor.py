from typing import Optional
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from model.helper.export_file_formatter import ExportFileFormatter, WorkbookType
from model.overtime.base_overtime_processor import BaseOvertimeProcessor
from model.helper.save_utils import save_workbook_with_fallback
from model.helper.date_utils import format_date, try_parse_date

class OvertimeExtractor(BaseOvertimeProcessor):
    def __init__(
        self,
        formatter: Optional[ExportFileFormatter]= None
    ):
        super().__init__()
        self.formatter = formatter or ExportFileFormatter()
        self.targets: dict[str, Workbook] = {}
        
    def extract(
        self,
        settings: dict,
        date_start_str: str,
        date_end_str: str, 
        overtime_file: str  
    ):
        print(f"OvertimeExtractor: Starting extraction for file: {overtime_file}")
        self.apply_settings(settings)
        self.load_overtime_wb(overtime_file)
        output_dir = self.get_output_dir(overtime_file)
        ws_sources = self.get_overtime_source_sheet()
        print(f"Date Start: {date_start_str}, Date End: {date_end_str}")
        
        self.targets = {
            code: self.formatter.prepare_workbook(code, WorkbookType.EXTRACT)
            for code, checked in self.company_codes.items()
            if checked
        }
        
        overtime_index = self._process_source_sheet(ws_sources, date_start_str, date_end_str)
        self._print_overtime_index(overtime_index)
        self._save_output_files(output_dir, date_start_str, date_end_str)
        
    def _process_source_sheet(
        self, 
        ws_source: list[Worksheet],
        date_start_str: str, 
        date_end_str: str
    ) -> dict[str, dict]:
        overtime_index: dict[str, dict] = {}
        for ws in ws_source:
            # Determine company code by ws title
            ws_title = ws.title
            company_code = self._company_code_from_sheet_title(ws_title)
            print(f"Processing sheet: {ws.title} for company code: {company_code}")
            
            if not company_code:
                return
            if company_code not in self.targets:
                return

            start_row = self.data_start_row
            id_col = self.employee_id_col
            name_col = id_col + 1
            date_col = name_col + 2
            shift_col = date_col + 1
            ovt_start_col = shift_col + 1
            ovt_end_col = ovt_start_col + 1
            ovt_hour_col = ovt_end_col + 1
            ovt_col = ovt_hour_col + 1
            notes_col = ovt_col + 2
            row_counter_col = self.row_counter_col
            
            # Find last non-empty cell in row_counter_col, from bottom up
            last_data_row = start_row
            for row in range(ws.max_row, start_row - 1, -1):
                value = ws.cell(row=row, column=row_counter_col).value
                if value is not None and str(value).strip() != "":
                    last_data_row = row
                    break
            
            # Initialize persistent variables
            employee_id = ""
            employee_name = ""
            notes = ""
            
            for row in range(start_row, last_data_row + 1):
                
                date = ws.cell(row=row, column=date_col).value
                shift = ws.cell(row=row, column=shift_col).value
                overtime = ws.cell(row=row, column=ovt_col).value
                overtime_hours = ws.cell(row=row, column=ovt_hour_col).value
                
                _id = str(ws.cell(row=row, column=id_col).value).strip()
                _name = str(ws.cell(row=row, column=name_col).value).strip()
                _notes = str(ws.cell(row=row, column=notes_col).value).strip()
                
                # Parse date as a date object and compare ranges using dates
                formatted_date = format_date(date)
                parsed_date = try_parse_date(formatted_date)
                if parsed_date is None:
                    continue
                
                try:
                    start_dt = try_parse_date(date_start_str) or parsed_date
                    end_dt = try_parse_date(date_end_str) or parsed_date
                except Exception:
                    start_dt = parsed_date
                    end_dt = parsed_date
                
                # Update persistent variables if current row has new values
                none = (None, "", "None")
                employee_id = _id if _id not in none else employee_id
                employee_name = _name if _name not in none else employee_name
                notes = _notes if _notes not in none else notes
                status, timein, timeout = self.map_status(shift)

                # Skip rows outside date range or with invalid data
                if not (start_dt <= parsed_date <= end_dt):
                    continue
                
                if not shift or not overtime or not overtime_hours:
                    continue

                key = f"{formatted_date}_{employee_id}"
                if key in overtime_index:
                    overtime_index[key]["overtime"] += overtime
                    continue
                    
                overtime_index[key] = {
                    "date": formatted_date,
                    "employee_id": employee_id,
                    "employee_name": employee_name,
                    "status": status,
                    "overtime": overtime,
                    "timein": timein,
                    "timeout": timeout,
                    "notes": notes,
                    "company_code": company_code
                }
                
        return overtime_index
            
    def _print_overtime_index(self, overtime_index: dict[str, dict]):
        for key, record in overtime_index.items():
            target_ws = self.targets[record["company_code"]].active
            target_ws.append([
                record["date"],
                record["employee_id"],
                record["employee_name"],
                record["status"],
                record["overtime"],
                record["timein"],
                record["timeout"],
                record["notes"]
            ])
            
    def _save_output_files(self, output_dir: str, date_start_str: str, date_end_str: str):
        print(f"Saving Targets Items: {list(self.targets.keys())}")
        for code, twb in self.targets.items():
            file_name = (
                f"{date_start_str} {code} Overtime.xlsx"
                if date_end_str == date_start_str
                else f"{date_start_str} to {date_end_str} {code} Overtime.xlsx"
            )
            out_path = output_dir / file_name
            save_workbook_with_fallback(twb, out_path, formatter=self.formatter)
            
            
        
        
        