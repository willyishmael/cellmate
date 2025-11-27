from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from model.helper.date_utils import format_date
from model.helper.save_utils import save_workbook_with_fallback
from model.overtime_optdrv.base_overtime_optdrv_processor import BaseOvertimeOptdrvProcessor


class OvertimeOptdrvExtractor(BaseOvertimeOptdrvProcessor):
    def __init__(self):
        super().__init__()
        
    def extract(
        self,
        settings: dict,
        date_start_str: str,
        date_end_str: str, 
        overtime_file: str  
    ):
        print(f"OvertimeOptdrvExtractor: Starting extraction for file: {overtime_file}")
        self.apply_settings(settings)
        self.load_overtime_wb(overtime_file)
        output_dir = self.get_output_dir(overtime_file)
        ws_sources = self.get_overtime_source_sheet()
        
        print(f"Date Start: {date_start_str}, Date End: {date_end_str}")
        
        targets = {
            code: self._init_target_sheet(code)
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
                f"{date_start_str} {code} Overtime Optdrv.xlsx"
                if date_end_str == date_start_str
                else f"{date_start_str} to {date_end_str} {code} Overtime Optdrv.xlsx"
            )
            out_path = output_dir / file_name
            
            save_workbook_with_fallback(twb, out_path)
            print(f"Saved {out_path.name}")
            
    def _init_target_sheet(self, company_code):
        wb = Workbook()
        ws = wb.active
        ws.title = company_code
        headers = ["Tanggal", "Employee ID", "Nama Karyawan", "Status", 
                   "Overtime", "Time In", "Time Out", "Keterangan"]
        ws.append(headers)
        return wb
    
    def _process_source_sheet(
        self, 
        ws: Worksheet, 
        targets: dict[str, Workbook], 
        date_start_str: str, 
        date_end_str: str
    ):
        """Process a single source worksheet and populate target workbooks."""
        print(f"Processing source sheet: {ws.title}")
        
        start_row = self.data_start_row
        date_header_row = self.date_header_row
        id_col = self.employee_id_col
        name_col = self.employee_name_col
        company_code_col = self.company_code_col
        row_counter_col = self.row_counter_col
        
        # Find last non-empty cell in row_counter_col, from bottom up
        last_data_row = start_row
        for row in range(ws.max_row, start_row - 1, -1):
            value = ws.cell(row=row, column=row_counter_col).value
            if value is not None and str(value).strip() != "":
                last_data_row = row
                break
        
        # Extract dates from header row
        header_dates = []
        for col in range(company_code_col + 1, ws.max_column + 1):
            cell_value = ws.cell(row=date_header_row, column=col).value
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
            start_col = company_code_col + 1
        if end_col is None:
            end_col = ws.max_column
            
        print(f"Data rows: {start_row} to {last_data_row}, Columns: {start_col} to {end_col}")
        
        for row in range(start_row, last_data_row + 1):
            company_code = ws.cell(row=row, column=company_code_col).value
            
            if not company_code or company_code not in targets:
                continue
            
            target_wb = targets[company_code]
            target_ws = target_wb.active
            
            employee_id = ws.cell(row=row, column=id_col).value
            employee_name = ws.cell(row=row, column=name_col).value
            
            for col in range(start_col, end_col + 1):
                date = None
                for hd_col, hd_date in header_dates:
                    if hd_col == col:
                        date = hd_date
                        break
                if not date:
                    continue
                
                overtime = ws.cell(row=row, column=col).value
                if overtime is None or str(overtime).strip() == "" or overtime == 0:
                    continue
                
                time_in = "07:00"
                time_out = "19:00"
                status = "Hadir (H)"
                
                target_ws.append([
                    date,
                    employee_id,
                    employee_name,
                    status,
                    overtime,
                    time_in,
                    time_out
                ])
        
