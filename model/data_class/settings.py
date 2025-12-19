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
    time_off_only: bool
    
@dataclass
class OvertimeSettings:
    """Settings for overtime processing."""
    employee_id_col: int
    data_start_row: int
    row_counter_col: int
    sheet_names: list[str]
    company_codes: dict
    employee_name_col: int
    date_col: int
    shift_col: int
    ovt_start_col: int
    ovt_end_col: int
    ovt_hour_col: int
    ovt_col: int
    notes_col: int
    
@dataclass
class OvertimeOptDrvSettings:
    """Settings for overtime optdrv processing."""
    employee_id_col: int
    data_start_row: int
    date_header_row: int
    employee_name_col: int
    row_counter_col: int
    sheet_names: list[str]
    company_code_col: int
    company_codes: dict