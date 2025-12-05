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
        
        targets = {
            code: self.formatter.prepare_workbook(code, WorkbookType.EXTRACT)
            for code, checked in self.company_codes.items()
            if checked
        }
        
        for ws in ws_sources:
            self._process_source_sheet(ws, targets, date_start_str, date_end_str)
            
        # Save output files
        print("Saving output files...")
        print(f"Targets Items: {list(targets.keys())}")
        for code, twb in targets.items():
            print(f"Saving output for company code: {code}")
            file_name = (
                f"{date_start_str} {code} Overtime.xlsx"
                if date_end_str == date_start_str
                else f"{date_start_str} to {date_end_str} {code} Overtime.xlsx"
            )
            out_path = output_dir / file_name
            
            save_workbook_with_fallback(twb, out_path, formatter=self.formatter)
            print(f"Saved {out_path.name}")
        
    def _process_source_sheet(
        self, 
        ws: Worksheet, 
        targets: dict[str, Workbook], 
        date_start_str: str, 
        date_end_str: str
    ):
        
        # Determine company code by ws title
        ws_title = ws.title
        sheet_company_code = self._company_code_from_sheet_title(ws_title)
        print(f"Processing sheet: {ws.title} for company code: {sheet_company_code}")
        
        if not sheet_company_code:
            return
        if sheet_company_code not in targets:
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
            employee_id = _id if _id != "" else employee_id
            employee_name = _name if _name != "" else employee_name
            notes = _notes if _notes != "" else notes
            status, timein, timeout = self.map_status(shift)

            # Skip rows outside date range or with invalid data
            if not (start_dt <= parsed_date <= end_dt):
                print(f"row: {row} skipped, date are not valid")
                continue
            
            if not shift or not overtime or not overtime_hours:
                print(f"row: {row} skipped, shift or overtime value is not valid")
                continue

            target_ws = targets[sheet_company_code].active
            target_ws.append([
                formatted_date,
                employee_id,
                employee_name,
                status,
                overtime,
                timein,
                timeout,
                notes
            ])
            
            
        
        
        