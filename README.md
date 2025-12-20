# Cellmate

**Cellmate** is a desktop application for processing and comparing HR data (attendance, overtime, and optional drive records) from Excel workbooks. It extracts data by company code, applies templates, and generates comparison reports.

---

## Features

- **Attendance Processing**: Extract and compare employee attendance records by company code (PM, PTM, TMP).
- **Overtime Tracking**: Extract overtime hours and compare against HRIS data.
- **Optional Drive (OPTDRV)**: Process optional drive records.
- **Template Management**: Save, load, and manage reusable extraction templates.
- **Multi-Sheet Support**: Automatically detect company codes from worksheet titles.
- **Robust Date Parsing**: Supports multiple date formats (ISO, DD/MM, month names, datetime strings).
- **Safe Excel Saving**: Fallback mechanism for handling problematic Excel external references.

---

## Project Structure

```
cellmate/
├── main.py                      # Entry point
├── data/
│   └── templates.json           # Default templates (bundled with app)
├── model/
│   ├── base_processor.py        # Shared processing logic
│   ├── template_model.py        # Template CRUD
│   ├── attendance/              # Attendance extraction/comparison
│   ├── overtime/                # Overtime extraction/comparison
│   ├── overtime_optdrv/         # Optional drive extraction/comparison
│   ├── helper/
│   │   ├── app_data.py          # Platform-specific app-data paths
│   │   ├── date_utils.py        # Date parsing & formatting
│   │   ├── export_file_formatter.py  # Workbook header creation
│   │   └── save_utils.py        # Safe workbook saving
│   └── data_class/
│       └── settings.py          # Settings dataclasses
├── ui/
│   ├── main_window.py           # Main window UI
│   ├── page/                    # Tab pages (Attendance, Overtime, etc.)
│   └── widget/                  # Reusable UI widgets
├── view_model/
│   ├── template_view_model.py   # Template ViewModel
│   └── attendance_view_model.py # Attendance ViewModel
├── venv/                        # Python virtual environment
├── BUILD_INSTRUCTIONS.md        # PyInstaller build commands
└── README.md                    # This file
```

---

## Requirements

- **Python**: 3.11 or higher
- **OS**: macOS, Windows, or Linux
- **Dependencies** (installed via `requirements.txt`):
  - `openpyxl>=3.0` — Excel file reading/writing
  - `PySide6>=6.0` — GUI framework
  - `pandas>=2.0` (optional) — data manipulation

---

## First-Time Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd cellmate
```

### 2. Create Virtual Environment
```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist, install manually:
```bash
pip install openpyxl PySide6
```

### 4. Verify Installation
```bash
python main.py
```

A window titled "Cellmate" should appear with tabs for Attendance, Overtime, Overtime OPTDRV, Templates, and App Info.

---

## Running the App

### Development Mode
```bash
# macOS / Linux
source venv/bin/activate
python main.py

# Windows
venv\Scripts\activate
python main.py
```

### First Launch
- On first run, the app automatically creates `templates.json` in:
  - **macOS**: `~/Library/Application Support/Cellmate/templates.json`
  - **Windows**: `C:\Users\<username>\AppData\Roaming\Cellmate\templates.json`
  - **Linux**: `~/.local/share/Cellmate/templates.json`
- The bundled default templates are copied to this location if it doesn't exist.

---

## Building Executables

See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) for detailed PyInstaller commands:

- **macOS**: Build `.app` bundle or `.dmg` installer
- **Windows**: Build `.exe` (one-dir or one-file)

Quick commands:

**macOS:**
```bash
pyinstaller --noconfirm --windowed --name Cellmate --add-data "data/templates.json:data" --collect-all PySide6 main.py
```

**Windows:**
```bash
pyinstaller --noconfirm --windowed --name Cellmate --add-data "data\\templates.json;data" --collect-all PySide6 main.py
```

---

## Usage

### 1. **Attendance Tab**
   - Upload Excel workbook with attendance records
   - Select a template or configure manually (employee ID column, date format, etc.)
   - Extract: generates a new workbook with attendance by company code
   - Compare: compares extracted data against HRIS export

### 2. **Overtime Tab**
   - Upload overtime data workbook
   - Select/configure template
   - Extract and compare overtime hours

### 3. **Overtime OPTDRV Tab**
   - Upload optional drive records
   - Extract and compare

### 4. **Templates Tab**
   - View, create, edit, delete templates
   - Export/import templates from JSON files

### 5. **App Info Tab**
   - View app version and information

---

## Troubleshooting

### "No module named X" error
Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install openpyxl PySide6
```

### Virtual environment not activated
Verify activation:
```bash
which python  # macOS/Linux — should show .../venv/bin/python
where python  # Windows — should show ...\venv\Scripts\python.exe
```

### App won't start on first run
Check that `data/templates.json` exists in the project root (it should be in the repo).

### Excel file errors
- Ensure files are in `.xlsx` format (not `.xls` or `.xlsb`).
- For `.xlsb` files, convert to `.xlsx` first using Excel or another tool.

---

## Development Notes

### Adding a New Processor
1. Create a new folder under `model/` (e.g., `model/newfeature/`)
2. Inherit from `BaseProcessor` for shared logic
3. Implement extractor and comparator classes
4. Add corresponding ViewModel and UI page
5. Wire into `MainWindow`

### Date Parsing
The app supports multiple date formats via `model/helper/date_utils.py`:
- ISO: `2025-10-08`, `2025/10/08`
- European: `08/10/2025`, `08-10-2025`, `08/10`
- Month names: `26-Oct-2025`, `26 October 2025`
- Datetime: `2025-11-26 00:00:00`

### Templates Location
Templates are stored in a user-writable platform-specific location (see **First Launch** above) via `model/helper/app_data.py`.

---

## License

[Add license info if applicable]

---

## Support

For issues or questions, contact the development team or open an issue in the repository.
