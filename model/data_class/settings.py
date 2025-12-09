from dataclasses import dataclass

@dataclass
class AttendanceSettings:
    """Settings for attendance processing."""
    employee_id_col: int
    employee_name_col: int
    company_code_col: int
    data_start_row: int
    date_header_row: int
    row_counter_col: int
    sheet_names: list[str]
    ignore_list: list[str]
    company_codes: dict
    
@dataclass
class OvertimeSettings:
    """Settings for overtime processing."""
    employee_id_col: int
    data_start_row: int
    row_counter_col: int
    sheet_names: list[str]
    company_codes: dict
    
@dataclass
class OvertimeOptDrvSettings:
    """Settings for overtime optdrv processing."""
    employee_id_col: int
    data_start_row: int
    row_counter_col: int
    sheet_names: list[str]
    company_codes: dict