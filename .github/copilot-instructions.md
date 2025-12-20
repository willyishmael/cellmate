# Cellmate Copilot Instructions

## Project Overview
**Cellmate** is a PySide6 desktop app for processing HR data (attendance, overtime, optional drive records) from Excel workbooks. It extracts data by company code using configurable templates and generates comparison reports against HRIS exports.

## Architecture

### MVVM Pattern with Three Data Processing Pipelines
The app follows **Model-View-ViewModel** architecture with three parallel processing tracks:
- **Attendance**: Extract/compare employee attendance records by company code (PM, PTM, TMP)
- **Overtime**: Extract/compare overtime hours against HRIS data  
- **Overtime OPTDRV**: Process optional drive records

Each track has identical structure:
```
model/{track}/          # Business logic (extractor + comparator)
view_model/{track}_view_model.py  # Orchestrates model calls, returns Result
ui/page/{track}_page.py # PySide6 UI, binds to ViewModel
```

### Template System
Templates store extraction settings (column indices, sheet names, company codes) in JSON. See [data/templates.json](data/templates.json).
- **TemplateModel** ([model/template_model.py](model/template_model.py)): CRUD operations on templates
- **TemplateViewModel** ([view_model/template_view_model.py](view_model/template_view_model.py)): Shared across all pages for template selection
- Templates bundled in app and copied to platform-specific app data dir on first launch via [model/helper/app_data.py](model/helper/app_data.py)

### BaseProcessor Pattern
All extractors/comparators inherit from [model/base_processor.py](model/base_processor.py):
- `apply_{track}_settings(dict) -> {Track}Settings`: Parses template settings into dataclasses ([model/data_class/settings.py](model/data_class/settings.py))
- `load_source_wb()`, `get_source_sheets()`, `get_output_dir()`: Shared Excel handling
- Each track has derived column logic (e.g., OvertimeSettings derives 8+ columns from just 3 config values)

### Safe Excel Saving with Fallback
[model/helper/save_utils.py](model/helper/save_utils.py) implements `save_workbook_with_fallback()`:
1. Try normal save
2. On failure, clear `externalReferences` metadata and retry
3. Final fallback: copy values-only (no formulas) to new workbook
This handles problematic Excel external references that crash openpyxl.

## Development Workflows

### Running the App
```bash
# Activate venv first
python main.py
```
Entry point: [main.py](main.py) calls `ensure_templates_json()` then shows [ui/main_window.py](ui/main_window.py).

### Building Executables
See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md). **Critical**: Build on target OS (no cross-compilation).

**Windows**:
```bash
pyinstaller --noconfirm --windowed --name Cellmate --add-data "data\\templates.json;data" --collect-all PySide6 main.py
```
Output: `dist\Cellmate\Cellmate.exe` (one-directory mode preferred for PySide6)

**macOS**:
```bash
pyinstaller --noconfirm --windowed --name Cellmate --add-data "data/templates.json:data" --collect-all PySide6 main.py
```
Output: `dist/Cellmate.app`

If runtime crashes with "No module named X", add `--hidden-import=X`.

### App Data Locations
On first run, bundled `data/templates.json` copied to:
- **Windows**: `%APPDATA%\Cellmate\templates.json`
- **macOS**: `~/Library/Application Support/Cellmate/templates.json`
- **Linux**: `~/.local/share/Cellmate/templates.json`

See [model/helper/app_data.py](model/helper/app_data.py) for `resource_path()` (bundled) vs `user_templates_path()` (writable).

## Code Conventions

### Date Handling
[model/helper/date_utils.py](model/helper/date_utils.py) `format_date()` normalizes dates to `YYYY-MM-DD`:
- Handles datetime objects, ISO strings, DD/MM/YYYY, DD-MMM-YYYY, DD/MM (assumes current year)
- Excel serial dates via `openpyxl.utils.datetime.from_excel()`
- Always parse dates through this function before comparisons

### Result Pattern
ViewModels return `Result` dataclass ([model/data_class/result.py](model/data_class/result.py)):
```python
Result(success=True/False, data=[], message=str)
```
UI pages check `result.success` to show success/error messages.

### UI Widget Composition
Pages compose reusable widgets from [ui/widget/](ui/widget/):
- **TemplateBar**: Template dropdown + New/Save buttons
- **PeriodDateWidget**: Period dropdown + Start/End date pickers
- **CompanyCodeCheckbox**: PM/PTM/TMP checkboxes
- **FormFieldGroup**: Dynamic form fields from config dict
- **DropArea**: Drag-and-drop file input

See [ui/page/attendance_page.py](ui/page/attendance_page.py) for composition pattern.

### Column Indexing Convention
Templates store 1-based column indices (matching Excel UI). Code uses openpyxl's 1-based indexing directly—no zero-conversion needed.

### Sheet Name Handling
Settings store comma-separated sheet names: `"26 NOV - 25 DES 2025, Format Baru"`. `BaseProcessor._parse_comma_list()` splits and strips whitespace.

## Critical Implementation Details

### Derived Columns in Overtime
[model/base_processor.py](model/base_processor.py) `apply_overtime_settings()` derives 9 columns from 3 config values:
```python
emp_col = config["employee_id_column"]  # Base
name_col = emp_col + 1
date_col = name_col + 2
shift_col = date_col + 1
# ... continues for ovt_start, ovt_end, ovt_hour, ovt, notes
```
**Why**: Overtime sheets have fixed column layout; only one anchor column needed.

### Time-Off-Only Flag
Attendance extraction has `time_off_only` setting. When true, extraction logic filters for time-off markers (implementation in [model/attendance/attendance_extractor.py](model/attendance/attendance_extractor.py)).

### ExportFileFormatter
[model/helper/export_file_formatter.py](model/helper/export_file_formatter.py) creates output workbooks with:
- Company code as worksheet title
- Formatted headers (bold, borders, alignment)
- `WorkbookType` enum: `EXTRACT` vs `COMPARE` determines header columns

### Ignore List
Attendance settings support `ignore_list` of employee IDs to skip (e.g., "OBI-1072322, OBI-29771024"). Parsed via `_parse_comma_list()`.

## Common Tasks

### Adding a New Processing Track
1. Create `model/{track}/{track}_extractor.py` and `{track}_comparator.py` inheriting `BaseProcessor`
2. Add settings dataclass to [model/data_class/settings.py](model/data_class/settings.py)
3. Add `apply_{track}_settings()` to [model/base_processor.py](model/base_processor.py)
4. Create `view_model/{track}_view_model.py` wrapping extractor/comparator
5. Create `ui/page/{track}_page.py` with template bar, form fields, drop areas
6. Add tab to [ui/main_window.py](ui/main_window.py)

### Modifying Template Fields
1. Update JSON structure in [data/templates.json](data/templates.json)
2. Update Settings dataclass in [model/data_class/settings.py](model/data_class/settings.py)
3. Update `apply_*_settings()` in [model/base_processor.py](model/base_processor.py)
4. Update UI form fields in `ui/page/{track}_page.py` (FormFieldGroup config)
5. Rebuild app to bundle new templates.json

### Debugging Excel Issues
If save fails, check logs in `save_workbook_with_fallback()` for:
- `externalReferences` errors → fallback clears them
- Formula errors → fallback copies values-only
- If all fails, check Excel file isn't open elsewhere
