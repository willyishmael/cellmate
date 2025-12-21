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
```powershell
pyinstaller `
  --noconfirm `
  --windowed `
  --name Cellmate `
  --icon=data\icon.ico `
  --add-data "data\\icon.ico;data" `
  --add-data "data\\templates.json;data" `
  --hidden-import=PySide6.QtCore `
  --hidden-import=PySide6.QtGui `
  --hidden-import=PySide6.QtWidgets `
  --hidden-import=openpyxl `
  --exclude-module=matplotlib `
  --exclude-module=PIL `
  --exclude-module=numpy `
  --exclude-module=pandas `
  --exclude-module=scipy `
  --exclude-module=tkinter `
  main.py
```

**Note:** Omit `--icon` line if you don't have an icon file yet. Icon file should be `.ico` format (256x256 or 512x512 recommended).

If the window/taskbar still shows a default icon, ensure the app sets the runtime icon (done in `main.py`) and that `data/icon.ico` is included via `--add-data`. On macOS/Linux, if you rely on runtime icon setting, you should also bundle your `icon.icns` file via `--add-data` so it is available at runtime. Windows may cache file icons; if the `.exe` icon doesn't update, rebuild to a new name or clear the icon cache.

### Output
- **One directory**: `dist\Cellmate\Cellmate.exe`
  - Final size: ~100-150 MB
  - More reliable with PySide6, faster startup
- **Single file (not recommended)**: Add `--onefile` flag, outputs `dist\Cellmate.exe`
  - Slower startup, can trigger antivirus warnings

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
pyinstaller \
  --noconfirm \
  --windowed \
  --name Cellmate \
  --icon=data/icon.icns \
  --add-data "data/templates.json:data" \
  --hidden-import=PySide6.QtCore \
  --hidden-import=PySide6.QtGui \
  --hidden-import=PySide6.QtWidgets \
  --hidden-import=openpyxl \
  --exclude-module=matplotlib \
  --exclude-module=PIL \
  --exclude-module=numpy \
  --exclude-module=pandas \
  --exclude-module=scipy \
  --exclude-module=tkinter \
  main.py
```

**Note:** Omit `--icon` line if you don't have an icon file yet. Icon file should be `.icns` format for macOS.

### Output
- `dist/Cellmate.app/` — a macOS application bundle (~100-150 MB)

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
If the app crashes with "No module named X", add `--hidden-import=X` to the build command.

**Example:** Add `--hidden-import=et_xmlfile` if openpyxl dependencies are missing.

### Size Optimization Notes
- **`--collect-all PySide6`** pulls in 500+ MB of unused Qt modules (3D, multimedia, web engine, etc.)
- **Targeted imports** only include QtCore, QtGui, QtWidgets (~100 MB)
- **Exclude modules** prevent PyInstaller from bundling large unused libraries
- If you need additional PySide6 modules, add them individually: `--hidden-import=PySide6.QtNetwork`

### Build Artifacts
- `build/` — intermediate build files (safe to delete)
- `dist/` — final deliverables (keep this)
- `Cellmate.spec` — PyInstaller spec file (safe to delete)

To clean up and rebuild:
```bash
rm -rf build dist Cellmate.spec  # macOS/Linux
rmdir /s /q build dist  # Windows
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

