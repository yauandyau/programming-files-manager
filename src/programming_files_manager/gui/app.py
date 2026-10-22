"""Tkinter front-end.

This is the only module that imports :mod:`tkinter`.  It owns the widget
layout, the user prompts and the glue to :mod:`storage` / :mod:`service`; it
does not implement CSV parsing or file rewriting itself.
"""

from __future__ import annotations

import datetime
import logging
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from ..config import CSV_FILE, DEFAULT_TYPES
from ..logging_config import setup_logging
from ..models import FileType
from ..service import CreateResult, create_files
from ..storage import load_csv, save_csv

logger = logging.getLogger(__name__)

WINDOW_TITLE = "Programming File Manager"
WINDOW_SIZE = "600x640"
DATE_FORMAT = "%d/%m/%Y"


class FileManagerApp:
    """The main window and all of its callbacks."""

    def __init__(self, csv_path: Path | None = None) -> None:
        self.csv_path: Path = (
            Path(csv_path) if csv_path is not None else CSV_FILE
        )
        self.file_data: dict[str, FileType] = {}
        self.entry: dict[str, ttk.Entry] = {}

        self.root = tk.Tk()
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.resizable(False, False)
        self.root.wm_attributes("-topmost", 1)

        self._build_ui()
        self._load_data()
        self._refresh_types()

    # ------------------------------------------------------------------ data
    def _load_data(self) -> None:
        try:
            self.file_data = load_csv(self.csv_path, DEFAULT_TYPES)
        except (OSError, ValueError) as exc:
            logger.exception("Could not load %s", self.csv_path)
            messagebox.showerror(
                "Error",
                f"Could not read {self.csv_path}:\n{exc}",
            )
            self.file_data = dict(DEFAULT_TYPES)
        else:
            self._log(f"Loaded {len(self.file_data)} file type(s) from "
                      f"{self.csv_path}")

    # ------------------------------------------------------------------- ui
    def _build_ui(self) -> None:
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=0)
        main_frame.rowconfigure(2, weight=1)

        ttk.Label(
            main_frame,
            text="PROGRAMMING FILE MANAGER",
            font=("Arial", 16, "bold"),
        ).grid(row=0, column=0, columnspan=2, pady=(0, 10))

        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))

        self._build_create_tab(notebook)
        self._build_add_tab(notebook)

        self.status_text = tk.Text(
            main_frame,
            height=8,
            width=60,
            state=tk.DISABLED,
        )
        self.status_text.grid(
            row=2,
            column=0,
            sticky=(tk.W, tk.E, tk.N, tk.S),
            pady=(15, 0),
        )
        scrollbar = ttk.Scrollbar(
            main_frame,
            orient=tk.VERTICAL,
            command=self.status_text.yview,
        )
        scrollbar.grid(row=2, column=1, sticky=(tk.N, tk.S), pady=(15, 0))
        self.status_text.configure(yscrollcommand=scrollbar.set)

    def _build_create_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook, padding="15")
        notebook.add(frame, text="建立檔案")
        frame.columnconfigure(1, weight=1)

        labels = [
            "檔案類型:",
            "輸入檔案:",
            "輸出路徑",
            "日期:",
            "Lab:",
            "Number of ex:",
        ]
        for row, text in enumerate(labels):
            ttk.Label(frame, text=text).grid(
                row=row, column=0, sticky=tk.W, pady=5
            )

        self.filetype_combo = ttk.Combobox(frame, state="readonly", width=30)
        self.filetype_combo.grid(
            row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5
        )
        self.filetype_combo.bind("<<ComboboxSelected>>", self._on_type_change)

        self.entry["inpath"] = ttk.Entry(frame, width=30)
        self.entry["inpath"].grid(
            row=1, column=1, sticky=(tk.W, tk.E), pady=5
        )
        ttk.Button(frame, text="瀏覽…", command=self._browse_file).grid(
            row=1, column=2, padx=(5, 0), pady=5
        )

        for row, key in ((2, "outpath"), (3, "date"), (4, "lab"), (5, "ex")):
            widget = ttk.Entry(frame, width=30)
            widget.grid(
                row=row,
                column=1,
                columnspan=2,
                sticky=(tk.W, tk.E),
                pady=5,
            )
            self.entry[key] = widget

        self.entry["date"].insert(
            0, datetime.date.today().strftime(DATE_FORMAT)
        )

        ttk.Button(
            frame,
            text="Create File",
            command=self._create_files,
        ).grid(row=6, column=0, columnspan=3, pady=20)

    def _build_add_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook, padding="15")
        notebook.add(frame, text="新增模式")
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(4, weight=1)

        fields = [
            ("name", "名稱"),
            ("new_type", "檔案類型:"),
            ("new_inpath", "默認輸入路徑:"),
            ("new_outpath", "默認輸出路徑:"),
        ]
        for row, (key, label) in enumerate(fields):
            ttk.Label(frame, text=label).grid(
                row=row, column=0, sticky=tk.W, pady=5
            )
            widget = ttk.Entry(frame, width=30)
            widget.grid(
                row=row,
                column=1,
                columnspan=2,
                sticky=(tk.W, tk.E),
                pady=5,
            )
            self.entry[key] = widget

        ttk.Label(frame, text="文字:").grid(
            row=4, column=0, sticky=(tk.W, tk.N), pady=5
        )
        self.new_text = tk.Text(frame, height=12, width=45)
        self.new_text.grid(
            row=4,
            column=1,
            columnspan=2,
            sticky=(tk.W, tk.E, tk.N, tk.S),
            pady=5,
        )
        text_scrollbar = ttk.Scrollbar(
            frame,
            orient=tk.VERTICAL,
            command=self.new_text.yview,
        )
        text_scrollbar.grid(row=4, column=3, sticky=(tk.N, tk.S), pady=5)
        self.new_text.configure(yscrollcommand=text_scrollbar.set)

        ttk.Button(
            frame,
            text="新增檔案類型",
            command=self._add_type,
        ).grid(row=5, column=0, columnspan=3, pady=20)

    # -------------------------------------------------------------- status
    def _log(self, message: str) -> None:
        if not message:
            return

        logger.info("%s", message)
        self.status_text.configure(state=tk.NORMAL)
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.configure(state=tk.DISABLED)

    # -------------------------------------------------------------- create
    def _create_files(self) -> None:
        filetype = self.filetype_combo.get().strip()
        if filetype not in self.file_data:
            messagebox.showerror("Error", "Please select a file type first.")
            return

        file_type = self.file_data[filetype]
        inpath = self.entry["inpath"].get().strip()
        outpath = self.entry["outpath"].get().strip()
        lab_text = self.entry["lab"].get().strip()
        ex_text = self.entry["ex"].get().strip()
        date = self.entry["date"].get().strip()

        if not all((inpath, outpath, lab_text, ex_text)):
            messagebox.showerror("Error", "All fields are required!")
            return

        if not Path(inpath).is_dir():
            messagebox.showerror(
                "Error",
                f"Input path is not a directory:\n{inpath}",
            )
            return

        try:
            lab, ex_count = int(lab_text), int(ex_text)
            if not (0 <= lab <= 99 and 0 <= ex_count <= 99):
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Error",
                "Lab and Ex must be a non-negative integer <= 99",
            )
            return

        out_dir = Path(outpath)
        if not out_dir.exists():
            if not messagebox.askyesno(
                "Warning",
                "Creating a new directory for the path",
            ):
                return
            try:
                out_dir.mkdir(parents=True)
            except OSError as exc:
                messagebox.showerror(
                    "Error",
                    f"Could not create directory: {exc}",
                )
                return

        if any(not value.strip() for _prefix, value in file_type.text):
            if not messagebox.askyesno(
                "Warning",
                "There is something wrong with your file_types.csv.\n"
                "Continue?",
            ):
                return

        try:
            result = create_files(
                ft=file_type,
                in_dir=Path(inpath),
                out_dir=out_dir,
                date=date,
                lab=lab,
                ex_count=ex_count,
            )
        except OSError as exc:
            messagebox.showerror("Error", f"Could not create files:\n{exc}")
            return

        self._report(result)

    def _report(self, result: CreateResult) -> None:
        for path in result.created:
            self._log(f"Created {path}")
        for path, reason in result.skipped:
            self._log(f"Skipped {path}: {reason}")
        for name in result.missing_template:
            self._log(f"Warning: template not fully applied to {name}")

        if result.missing_template:
            messagebox.showwarning(
                "Warning",
                "These files did not match every template line:\n"
                + "\n".join(result.missing_template),
            )

        if result.created:
            messagebox.showinfo(
                "Success",
                f"Successfully processed {len(result.created)} file(s).",
            )
        else:
            messagebox.showwarning(
                "Warning",
                "No file could be created. Check the log below.",
            )

    # -------------------------------------------------------------- browse
    def _browse_file(self) -> None:
        filetype = self.filetype_combo.get().strip()
        if filetype not in self.file_data:
            messagebox.showerror("Error", "Please select a file type first.")
            return

        file_type = self.file_data[filetype]
        suffix = f".{file_type.ext}" if file_type.ext else ""

        try:
            filename = (
                f"lab{int(self.entry['lab'].get().strip()):02d}"
                f"ex{int(self.entry['ex'].get().strip()):02d}{suffix}"
            )
        except ValueError:
            filename = f"untitle{suffix}"

        default_dir = file_type.inpath
        path = filedialog.asksaveasfilename(
            title="選擇輸出檔案",
            initialdir=default_dir if Path(default_dir).is_dir() else None,
            initialfile=filename,
            defaultextension=suffix,
            filetypes=[(suffix or "All files", f"*{suffix}"), ("All files", "*.*")],
        )

        if path:
            self.entry["inpath"].delete(0, tk.END)
            self.entry["inpath"].insert(0, str(Path(path).parent))
            self._log(f"Selected file: {path}")

    # ---------------------------------------------------------------- types
    def _on_type_change(self, _event: tk.Event | None = None) -> None:
        filetype = self.filetype_combo.get().strip()
        if filetype not in self.file_data:
            return

        file_type = self.file_data[filetype]
        self.entry["inpath"].delete(0, tk.END)
        self.entry["inpath"].insert(0, file_type.inpath)
        self.entry["outpath"].delete(0, tk.END)
        self.entry["outpath"].insert(0, file_type.outpath)
        self._log(f"Selected type: {filetype}")

    def _refresh_types(self) -> None:
        names = list(self.file_data)
        self.filetype_combo["values"] = names
        if names:
            self.filetype_combo.current(0)
            self._on_type_change()

    def _add_type(self) -> None:
        raw_text = self.new_text.get("1.0", tk.END)
        text: list[tuple[str, str]] = []
        for line in raw_text.splitlines():
            if not line.strip():
                continue
            if line.count(":") != 1:
                logger.debug("Ignoring template line: %r", line)
                continue
            prefix, value = line.split(":", 1)
            text.append((prefix, value.lstrip(" ")))

        name = self.entry["name"].get().strip()
        ext = self.entry["new_type"].get().strip()
        inpath = self.entry["new_inpath"].get().strip()
        outpath = self.entry["new_outpath"].get().strip()

        if not all((name, ext, inpath, outpath)):
            messagebox.showerror("Error", "All fields are required!")
            return

        if not text:
            messagebox.showerror(
                "Error",
                "At least one 'prefix: replacement' line is required.",
            )
            return

        if name in self.file_data:
            if not messagebox.askyesno(
                "Warning",
                f"File type '{name}' already exists!\nOverwrite it?",
            ):
                return

        self.file_data[name] = FileType(
            name=name,
            ext=ext,
            inpath=inpath,
            outpath=outpath,
            text=text,
        )

        try:
            save_csv(self.csv_path, self.file_data)
        except OSError as exc:
            messagebox.showerror("Error", f"Could not save CSV:\n{exc}")
            return

        self._refresh_types()
        self._log(f"Added / updated file type: {name}")
        messagebox.showinfo(
            "Success",
            f"File type '{name}' saved to {self.csv_path}!",
        )

        for key in ("name", "new_type", "new_inpath", "new_outpath"):
            self.entry[key].delete(0, tk.END)
        self.new_text.delete("1.0", tk.END)

    # ---------------------------------------------------------------- run
    def run(self) -> None:
        """Enter the Tk main loop."""
        self.root.mainloop()


def main(csv_path: Path | None = None) -> None:
    """Launch the GUI, optionally using ``csv_path`` as the catalogue."""
    if not logging.getLogger().handlers:
        setup_logging()

    FileManagerApp(csv_path).run()
