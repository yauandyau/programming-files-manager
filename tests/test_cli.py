"""Tests for :mod:`programming_files_manager.cli`."""

from __future__ import annotations

from pathlib import Path

from programming_files_manager.cli import main
from programming_files_manager.config import DEFAULT_TYPES
from programming_files_manager.models import FileType
from programming_files_manager.storage import save_csv


def test_list_types_returns_zero(
    sample_csv: Path,
    capsys,
) -> None:
    assert main(["--csv", str(sample_csv), "list-types"]) == 0
    assert "Sample" in capsys.readouterr().out


def test_create_end_to_end(
    sample_csv: Path,
    sample_type: FileType,
    tmp_path: Path,
) -> None:
    in_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    in_dir.mkdir()
    (in_dir / "lab03ex01.py").write_text(
        "# Student Name :\n# Date         :\n",
        encoding="utf-8",
    )

    code = main(
        [
            "--csv",
            str(sample_csv),
            "create",
            sample_type.name,
            "--in",
            str(in_dir),
            "--out",
            str(out_dir),
            "--date",
            "01/01/2025",
            "--lab",
            "3",
            "--ex",
            "1",
        ]
    )

    assert code == 0
    target = out_dir / "Lab03Ex01.py"
    assert target.is_file()
    assert "01/01/2025" in target.read_text(encoding="utf-8")
    assert not (in_dir / "lab03ex01.py").exists()


def test_unknown_type_returns_two(sample_csv: Path, tmp_path: Path) -> None:
    code = main(
        [
            "--csv",
            str(sample_csv),
            "create",
            "NoSuchType",
            "--in",
            str(tmp_path),
            "--out",
            str(tmp_path),
            "--lab",
            "1",
            "--ex",
            "1",
        ]
    )

    assert code == 2


def test_all_skipped_returns_one(
    sample_csv: Path,
    sample_type: FileType,
    tmp_path: Path,
) -> None:
    code = main(
        [
            "--csv",
            str(sample_csv),
            "create",
            sample_type.name,
            "--in",
            str(tmp_path / "does-not-exist"),
            "--out",
            str(tmp_path / "out"),
            "--lab",
            "1",
            "--ex",
            "1",
        ]
    )

    assert code == 1


def test_create_keeps_csci1130_rename_templates(tmp_path: Path) -> None:
    csv_path = tmp_path / "file_types.csv"
    save_csv(csv_path, DEFAULT_TYPES)

    in_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    in_dir.mkdir()
    (in_dir / "_Lab01Ex01.java").write_text(
        " * Student Name :\n * Date         :\n",
        encoding="utf-8",
    )

    code = main(
        [
            "--csv",
            str(csv_path),
            "create",
            "CSCI1130",
            "--in",
            str(in_dir),
            "--out",
            str(out_dir),
            "--date",
            "01/01/2025",
            "--lab",
            "1",
            "--ex",
            "1",
        ]
    )

    assert code == 0
    assert (out_dir / "Lab01Ex01.java").is_file()
