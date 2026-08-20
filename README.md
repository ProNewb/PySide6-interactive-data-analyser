# PySide6 Interactive Data Analyser

Desktop CSV and dataframe analysis application built with PySide6 and pandas.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

## Current Features

- Import CSV files with header and delimiter options.
- Open Excel, JSON, and Parquet datasets.
- Filter, clean, aggregate, transform, merge, and concatenate datasets.
- Preview source and result data in operation dialogs.
- Undo and redo the last five dataset changes.
- Save and reload projects with complete operation logs and restorable history snapshots.
- Export data as CSV, Excel, JSON, or Parquet.

Excel support uses `openpyxl`; Parquet support uses `pyarrow`.

