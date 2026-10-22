"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from programming_files_manager.models import FileType
from programming_files_manager.storage import save_csv


@pytest.fixture
def sample_type() -> FileType:
    """A minimal, self-contained file type."""
    return FileType(
        name="Sample",
        ext="py",
        inpath=str(Path.home() / "Downloads"),
        outpath=str(Path.home() / "Downloads" / "Sample"),
        text=[
            ("# Student Name :", ""),
            ("# Date         :", "{date}"),
        ],
    )


@pytest.fixture
def sample_csv(tmp_path: Path, sample_type: FileType) -> Path:
    """A CSV catalogue containing :func:`sample_type`."""
    path = tmp_path / "file_types.csv"
    save_csv(path, {sample_type.name: sample_type})
    return path
