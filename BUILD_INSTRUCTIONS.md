# Cellmate Build Instructions

Building standalone executables (`.exe` for Windows, `.app` for macOS) using PyInstaller.

---

## Prerequisites

1. **Ensure PyInstaller is installed** in your virtual environment:
   ```bash
   python -m pip install -U pyinstaller
   ```

2. **Build on the target OS** — you cannot cross-compile. Always build on the OS where you want to deliver:
   - Building `.exe`? Build on **Windows**.
   - Building `.app`? Build on **macOS**.

3. **Ensure `data/templates.json` exists** in the project root before building.

---

## Windows Build

### Command
```bash
pyinstaller --noconfirm --windowed --name Cellmate --add-data "data\\templates.json;data" --collect-all PySide6 main.py
```

### Output
- **One directory (recommended)**: `dist\Cellmate\Cellmate.exe`
  - Larger but more reliable with PySide6.
- **Single file (alternative)**: Add `--onefile` flag, outputs `dist\Cellmate.exe`
  - Slower startup, can trigger antivirus warnings.

### Run
- Double-click `Cellmate.exe` or run from command line: `.\dist\Cellmate\Cellmate.exe`

### First Run
- On first launch, the app automatically copies bundled `templates.json` to:
  ```
  C:\Users\<username>\AppData\Roaming\Cellmate\templates.json
  ```

---

## macOS Build

### Command
```bash
pyinstaller --noconfirm --windowed --name Cellmate --add-data "data/templates.json:data" --collect-all PySide6 main.py
```

### Output
- `dist/Cellmate.app/` — a macOS application bundle

### Run
- Double-click `Cellmate.app` in Finder, or:
  ```bash
  open dist/Cellmate.app
  ```

### First Run
- On first launch, the app automatically copies bundled `templates.json` to:
  ```
  ~/Library/Application Support/Cellmate/templates.json
  ```

### (Optional) Create DMG Installer
```bash
hdiutil create -volname Cellmate -srcfolder dist/Cellmate.app -ov -format UDZO Cellmate.dmg
```
- Creates `Cellmate.dmg` for distribution (drag-drop install).

---

## Troubleshooting

### Missing Modules at Runtime
If the app crashes with "No module named X", add the module to the PyInstaller command:

**Windows example:**
```bash
pyinstaller --noconfirm --windowed --name Cellmate --add-data "data\\templates.json;data" --collect-all PySide6 --hidden-import=openpyxl main.py
```

**macOS example:**
```bash
pyinstaller --noconfirm --windowed --name Cellmate --add-data "data/templates.json:data" --collect-all PySide6 --hidden-import=openpyxl main.py
```

### Build Artifacts
- `build/` — intermediate build files (safe to delete)
- `dist/` — final deliverables (keep this)
- `Cellmate.spec` — PyInstaller spec file (safe to delete)

To clean up and rebuild:
```bash
rm -rf build dist Cellmate.spec  # macOS/Linux
rmdir /s build dist  # Windows
```

---

## Code Signing (macOS Only)

For distribution outside your machine, code-sign the `.app`:

1. Add bundle identifier to the build command:
   ```bash
   pyinstaller --noconfirm --windowed --name Cellmate --osx-bundle-identifier com.yourcompany.cellmate --add-data "data/templates.json:data" --collect-all PySide6 main.py
   ```

2. Sign the app (requires a developer certificate):
   ```bash
   codesign -s - dist/Cellmate.app
   ```

3. Verify:
   ```bash
   codesign -v dist/Cellmate.app
   ```

---

## Notes

- **Data embedding**: `--add-data` bundles `data/templates.json` into the executable so the app can copy it to the user's writable location on first run.
- **PySide6 collection**: `--collect-all PySide6` ensures all Qt libraries are included.
- **No console**: `--windowed` hides the console window (recommended for GUI apps).
- **Confirm**: `--noconfirm` skips the build confirmation prompt.

