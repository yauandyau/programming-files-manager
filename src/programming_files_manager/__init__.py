"""programming-files-manager: build course files from reusable templates."""

from __future__ import annotations

from .config import CSV_FILE, DEFAULT_TYPES, HEADER
from .models import FileType

__version__ = "0.1.0"

__all__ = [
    "CSV_FILE",
    "DEFAULT_TYPES",
    "HEADER",
    "FileType",
    "__version__",
]
