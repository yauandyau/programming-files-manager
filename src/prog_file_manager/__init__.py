"""
prog_file_manager
=================

程式作業檔案產生器。

Public API（不會 import tkinter）::

    from prog_file_manager import FileType, load_csv, save_csv, create_files

GUI 需另外呼叫，才會 import tkinter::

    from prog_file_manager.gui import main
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .config import CSV_FILE, DEFAULT_TYPES, HEADER
from .models import FileType, TemplateLine
from .service import CreateResult, create_files
from .storage import load_csv, save_csv

if TYPE_CHECKING:  # 只給型別檢查器看，runtime 不執行
    from .gui import main as gui_main

__version__ = "0.1.0"

__all__ = [
    "__version__",
    # config
    "CSV_FILE",
    "DEFAULT_TYPES",
    "HEADER",
    # models
    "FileType",
    "TemplateLine",
    # storage
    "load_csv",
    "save_csv",
    # service
    "CreateResult",
    "create_files",
    # gui (lazy)
    "gui_main",
]


def __getattr__(name: str):
    """Lazy import GUI，避免在無 tkinter 的環境下 import 失敗。"""
    if name == "gui_main":
        from .gui import main as _main

        return _main
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
