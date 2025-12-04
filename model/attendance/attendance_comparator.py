from typing import Optional
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from model.helper.date_utils import format_date
from model.helper.export_file_formatter import ExportFileFormatter, WorkbookType
from model.attendance.base_attendance_processor import BaseAttendanceProcessor
from model.helper.save_utils import save_workbook_with_fallback

class AttendanceComparator(BaseAttendanceProcessor):
    """
    Compare Attendance data (from extracted report) with HRIS export.
    Outputs differences such as missing uploads or mismatched attendance codes.
    """
    
    def __init__(self, formatter: Optional[ExportFileFormatter] = None):
        super().__init__()
        self.formatter = formatter or ExportFileFormatter()
        self.attendance_index = {} # key -> record
        self.duplicates = [] # optional list to collect duplicates
    
    def compare(
        self, 
        settings: dict, 
        date_start_str: str, 
        date_end_str: str, 
        attendance_file: str,
        hris_file: str
    ) -> None:
        """Run the comparison process with given settings and files."""
        print("Starting comparison process...")
        self.apply_settings(settings)
        self.attendance_wb = self.load_attendance_wb(attendance_file)
        self.hris_wb = self.load_hris_wb(hris_file)
        output_dir = self.get_output_dir(attendance_file)
        attendance_ws = self.get_attendance_source_sheets()
        hris_ws = self.get_hris_source_sheets()
        
        print("Preparing target workbooks...")
        
        # Prepare target workbooks for each selected company code
        self.targets = {
            code: self.formatter.prepare_workbook(code, WorkbookType.COMPARE)
            for code, checked in self.company_codes.items()
            if checked
        }

        print(f"Target workbooks prepared. Company codes: {list(self.targets.keys())}")
        # Process attendance and HRIS sheets
        for ws in attendance_ws:
            self._process_attendance_sheet(ws, date_start_str, date_end_str)
        for ws in hris_ws:
            self._process_hris_sheet(ws, date_start_str, date_end_str)
        
        # Save comparison results
        print("Saving comparison results...")
        for code, twb in self.targets.items():
            print(f"Saving comparison output for company code: {code}")
            file_name = (
                f"{date_start_str} {code} HRIS Comparison.xlsx"
                if date_end_str == date_start_str
                else f"{date_start_str} to {date_end_str} {code} Comparison.xlsx"
            )
            out_path = output_dir / file_name
            self.formatter.format_worksheet(twb.active)
            save_workbook_with_fallback(twb, out_path, formatter=self.formatter)
            print(f"Saved {out_path.name}")
    
    def _process_attendance_sheet(
        self, 
        ws: Worksheet, 
        date_start_str: str, 
        date_end_str: str
    ) -> None:
        print(f"Processing attendance sheet: {ws.title}")
        
        # Find last non-empty cell in row_counter_col, from bottom up
        last_data_row = self.data_start_row
        for row in range(ws.max_row, self.data_start_row - 1, -1):
            value = ws.cell(row=row, column=self.row_counter_col).value
            if value is not None and str(value).strip() != "":
                last_data_row = row
                break
        
        # Extract dates from header row
        header_dates = []
        for col in range(self.company_code_col + 1, ws.max_column + 1):
            cell_value = ws.cell(row=self.date_header_row, column=col).value
            try:
                date = format_date(cell_value)
                header_dates.append((col, date))
            except Exception:
                continue
            
        # Determine start and end columns based on date range
        start_col = None
        end_col = None
        
        for col, date in header_dates:
            if date == date_start_str and start_col is None:
                start_col = col
            if date == date_end_str:
                end_col = col

        if start_col is None:
            start_col = self.company_code_col + 1
        if end_col is None:
            end_col = ws.max_column
            
        print(f"Data rows: {self.data_start_row} to {last_data_row}, Columns: {start_col} to {end_col}")
        
        # Process each row of data
        for row in range(self.data_start_row, last_data_row + 1):
            employee_id = ws.cell(row=row, column=self.employee_id_col).value
            employee_name = ws.cell(row=row, column=self.employee_name_col).value
            company_code = ws.cell(row=row, column=self.company_code_col).value

            if not employee_id or str(employee_id).strip() in self.ignore_list:
                continue

            if company_code not in self.targets:
                continue

            for col in range(start_col, end_col + 1):
                code = ws.cell(row=row, column=col).value
                date = ws.cell(row=self.date_header_row, column=col).value
                if not code or str(code).strip() == "" or not date:
                    continue

                formatted_date = format_date(date)
                employee_id_str = str(employee_id).strip()

                key = f"{formatted_date}_{employee_id_str}"
                status, timein, timeout = self._map_status(code)
                
                record = {
                    "date": formatted_date,
                    "employee_id": employee_id_str,
                    "employee_name": employee_name or "",
                    "company_code": company_code,
                    "status_code": code,
                    "status": status,
                    "overtime": 0,
                    "timein": timein,
                    "timeout": timeout,
                    "notes": ""
                }
                
                if key in self.attendance_index:
                    self.duplicates.append(record)
                else:
                    self.attendance_index[key] = record

                
    def _process_hris_sheet(
        self, 
        ws: Worksheet, 
        date_start_str: str, 
        date_end_str: str
    ) -> None:
        print(f"Processing HRIS sheet: {ws.title}")
        
        start_row = 2
        id_col = 1
        name_col = 2
        
        # Extract dates from header row
        header_dates = []
        for col in range(5, ws.max_column + 1):
            cell_value = ws.cell(row=1, column=col).value
            try:
                date = format_date(cell_value)
                header_dates.append((col, date))
            except Exception:
                continue
            
        # Determine start and end columns based on date range
        start_col = None
        end_col = None
        
        for col, date in header_dates:
            if date == date_start_str and start_col is None:
                start_col = col
            if date == date_end_str:
                end_col = col

        if start_col is None:
            start_col = self.company_code_col + 1
        if end_col is None:
            end_col = ws.max_column
        
        # Process each row of data
        for row in range(start_row, ws.max_row + 1):
            employee_id = ws.cell(row=row, column=id_col).value

            for col in range(start_col, end_col + 1):
                date = ws.cell(row=1, column=col).value
                status = ws.cell(row=row, column=col).value
                if not status or str(status).strip() == "" or not date:
                    continue
                
                formatted_date = format_date(date)
                employee_id_str = str(employee_id).strip()
                key = f"{formatted_date}_{employee_id_str}"
                matched_record = self.attendance_index.get(key)
                
                if matched_record:
                    ws_target = self.targets[matched_record["company_code"]].active
                    ws_target.append([
                        matched_record["status"], # Manual
                        status, # HRIS
                        matched_record["status"] == status, # Difference
                        matched_record["date"],
                        matched_record["employee_id"],
                        matched_record["employee_name"],
                        matched_record["status"],
                        matched_record["overtime"],
                        matched_record["timein"],
                        matched_record["timeout"],
                        matched_record["notes"]
                    ])

        