# programming-files-manager
This respository is mainly for the lab in programming course in CUHK.  
You can fill in your name, SID, class and date to several labXXexXX files with the same lab number and the same directory in one time.  
Create course programming files from reusable templates.  
Not finished yet. Please edit prompt.py by your own to fill in your name and SID.  

The tool keeps a small CSV catalogue of file types (`file_types.csv`). Each
entry remembers the extension, the default input/output folders and the header
lines that should be rewritten. A single command then emits `Lab01Ex01.py`,
`Lab01Ex02.py`, ... for a whole exercise set, optionally renaming the files with
a custom template.

The project used to be three loose scripts (`loadcsv.py`, `main.py`,
`prompt.py`). It is now a `src/`-layout package with the business logic
(`storage`, `service`) fully separated from the Tkinter front-end.

## Install

```bash
python -m pip install -e ".[dev]"
```

## CLI

```bash
# Show every configured file type
pfm list-types

# Create files for lab 3, exercises 1..5
pfm create CSCI1130 \
  --in ~/Downloads \
  --out ~/Downloads/CSCI1130 \
  --date 01/01/2025 \
  --lab 3 \
  --ex 5

# Use an alternative catalogue
pfm --csv ./my_types.csv list-types
```

`--lab` and `--ex` must be integers between 0 and 99. `create` exits with `0`
when at least one file was produced and `1` when nothing could be produced
(e.g. every source file was missing).

## GUI

```bash
pfm gui
# or, without installing the console script:
python -m programming_files_manager
```

The GUI is the only place where `tkinter` is imported, so the CLI and the test
suite keep working on machines without Tk.

## The CSV catalogue

`file_types.csv` is written with a UTF-8 BOM (`utf-8-sig`) so that it opens
correctly in Excel. It has exactly five columns:

| Column | Meaning |
| --- | --- |
| 文件類型 | Unique name of the file type (also the dictionary key) |
| 副檔名 | Extension without the dot, e.g. `py` |
| 默認輸入路徑 | Default folder holding the source files |
| 默認輸出路徑 | Default destination folder |
| 文字 | JSON list of `[prefix, replacement]` pairs |

When the file is missing, the built-in defaults are written automatically. All
default paths are derived from `Path.home()`; no personal folder is hard-coded.

The built-in `CSCI1130` entry demonstrates the optional rename templates:

```text
source_template = "_Lab{lab:02d}Ex{ex:02d}.java"
target_template = "Lab{lab:02d}Ex{ex:02d}.java"
```

When a template is `None`, the defaults are `lab{lab:02d}ex{ex:02d}.{ext}` for
the source and `Lab{lab:02d}Ex{ex:02d}.{ext}` for the target.

## Tests

```bash
pytest -q
pytest --cov=programming_files_manager --cov-report=term-missing
```

The suite never imports the GUI. It covers CSV round-trips (including the
BOM), malformed rows, invalid JSON, default bootstrapping, file creation,
skipped sources, template renaming, missing templates and the CLI end to end.
