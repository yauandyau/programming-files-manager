"""Tests for :mod:`programming_files_manager.storage`."""

from __future__ import annotations

import codecs
import csv
import json
from pathlib import Path

import pytest

from programming_files_manager.config import DEFAULT_TYPES, HEADER
from programming_files_manager.models import FileType
from programming_files_manager.storage import load_csv, save_csv


def test_header_has_five_columns() -> None:
    assert len(HEADER) == 5


def test_round_trip(tmp_path: Path, sample_type: FileType) -> None:
    path = tmp_path / "file_types.csv"
    save_csv(path, {sample_type.name: sample_type})

    loaded = load_csv(path)

    assert set(loaded) == {sample_type.name}
    assert loaded[sample_type.name] == sample_type


def test_rows_with_missing_columns_are_skipped(tmp_path: Path) -> None:
    path = tmp_path / "file_types.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(HEADER)
        writer.writerow(["TooShort", "py", "in"])
        writer.writerow(["", "py", "in", "out", "[]"])
        writer.writerow(["Good", "py", "in", "out", json.dumps([["# A:", "B"]])])

    loaded = load_csv(path)

    assert list(loaded) == ["Good"]
    assert loaded["Good"].text == [("# A:", "B")]


def test_invalid_json_propagates(tmp_path: Path) -> None:
    path = tmp_path / "file_types.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(HEADER)
        writer.writerow(["Bad", "py", "in", "out", "{not json"])

    with pytest.raises(json.JSONDecodeError):
        load_csv(path)


def test_missing_file_is_bootstrapped_from_defaults(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "file_types.csv"

    loaded = load_csv(path, DEFAULT_TYPES)

    assert path.is_file()
    assert set(loaded) == set(DEFAULT_TYPES)
    assert loaded["CSCI1130"] == DEFAULT_TYPES["CSCI1130"]

    # The returned mapping must be a copy, not the module-level catalogue.
    loaded.pop("CSCI1130")
    assert "CSCI1130" in DEFAULT_TYPES


def test_missing_file_without_defaults_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_csv(tmp_path / "absent.csv")


def test_utf8_sig_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "file_types.csv"
    file_type = FileType(
        name="程式設計",
        ext="py",
        inpath=str(Path.home() / "Downloads"),
        outpath=str(Path.home() / "Downloads" / "程式設計"),
        text=[("# 姓名 :", "小明")],
    )

    save_csv(path, {file_type.name: file_type})

    assert path.read_bytes().startswith(codecs.BOM_UTF8)
    loaded = load_csv(path)
    assert loaded["程式設計"] == file_type


def test_rename_templates_are_restored_from_defaults(tmp_path: Path) -> None:
    """The five-column format cannot store templates; defaults backfill them."""
    path = tmp_path / "file_types.csv"
    save_csv(path, DEFAULT_TYPES)

    loaded = load_csv(path, DEFAULT_TYPES)

    assert loaded["CSCI1130"].source_template == "_Lab{lab:02d}Ex{ex:02d}.java"
    assert loaded["CSCI1130"].target_template == "Lab{lab:02d}Ex{ex:02d}.java"
