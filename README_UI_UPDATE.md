# DataLens — interface refresh

The existing PyQt6 desktop application retains its transformation, analysis and visualization functions. The three core modules (`cleaning.py`, `analysis.py`, `visualization.py`) have only translated comments, docstrings, error messages and chart titles. The data store and export implementation are unchanged apart from English text.

## Run in VS Code (Windows)

Open the DataLens folder. Use the existing project's virtual environment if available. Select its Python interpreter in VS Code, open `main.py` and press F5 (Python File). If you extracted to a new folder, create a new environment and install the existing requirements:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

The archive intentionally excludes the original Windows virtual environment and generated Python caches. Both original CSV files and the requirements file are included. Alternatively, copy the updated Python files into your existing project, retaining your own `.venv`.

## Changes
- Light slate and teal theme, sidebar navigation, dataset overview and row/column counters.
- Scrollable operation forms, clearer input labels and status messages, improved tables with visible result indexes, and empty states.
- English interface, messages and code comments. Dataset content and column names are not translated.

## Verification and existing limitations
Python syntax checks and sample analysis/transformation checks passed. Scatter, line, distribution and heatmap charts rendered successfully. Bar plot failed with an invalid RGBA argument in both the original and updated code under the available library versions; its implementation was deliberately preserved. PyQt6 was unavailable in that environment, so the desktop windows could not be launched or visually verified there. `export_csv()` remains unimplemented in the original code; no new export implementation was added. The original package versions in `requirements.txt` are retained, and the smoke tests used the locally available pandas/matplotlib/seaborn versions rather than the original Windows environment.

## Contrast and CSV export update
The application now sets an explicit light Qt palette and paints all operation panels and scroll viewports. This prevents inherited dark system colors from making labels unreadable. Export CSV writes the entire active dataset (including accepted transformations), without the pandas index, using UTF-8 with BOM for spreadsheet compatibility. The analysis, cleaning and visualization modules are unchanged from the previous UI refresh. Python syntax and CSV round-trip checks passed; live Qt rendering was not available in the test environment.
