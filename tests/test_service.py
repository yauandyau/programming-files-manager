"""Tests for :mod:`programming_files_manager.service`."""

from __future__ import annotations

from pathlib import Path

from programming_files_manager.config import DEFAULT_TYPES
from programming_files_manager.models import FileType
from programming_files_manager.service import create_files

PY_SOURCE = (
    "# Student Name :\n"
    "# Date         :\n"
    "print('hello')\n"
)

JAVA_SOURCE = (
    " * Student Name :\n"
    " * Date         :\n"
    "class Lab {\n"
    "}\n"
)


def _write(directory: Path, name: str, content: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    path.write_text(content, encoding="utf-8")
    return path


def test_creates_files_and_rewrites_template_lines(
    tmp_path: Path, sample_type: FileType
) -> None:
    in_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    _write(in_dir, "lab01ex01.py", PY_SOURCE)
    _write(in_dir, "lab01ex02.py", PY_SOURCE)

    result = create_files(
        ft=sample_type,
        in_dir=in_dir,
        out_dir=out_dir,
        date="01/01/2025",
        lab=1,
        ex_count=2,
    )

    assert len(result.created) == 2
    assert result.skipped == []
    assert result.missing_template == []

    created = out_dir / "Lab01Ex01.py"
    assert created in result.created
    content = created.read_text(encoding="utf-8")
    assert "# Student Name : \n" in content
    assert "# Date         : 01/01/2025\n" in content
    assert "print('hello')" in content


def test_missing_source_is_skipped(
    tmp_path: Path, sample_type: FileType
) -> None:
    in_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    _write(in_dir, "lab01ex01.py", PY_SOURCE)

    result = create_files(
        ft=sample_type,
        in_dir=in_dir,
        out_dir=out_dir,
        date="01/01/2025",
        lab=1,
        ex_count=2,
    )

    assert len(result.created) == 1
    assert len(result.skipped) == 1
    assert result.skipped[0][0].name == "lab01ex02.py"
    assert "not found" in result.skipped[0][1]


def test_csci1130_templates_rename_the_files(tmp_path: Path) -> None:
    file_type = DEFAULT_TYPES["CSCI1130"]
    in_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    _write(in_dir, "_Lab02Ex01.java", JAVA_SOURCE)

    result = create_files(
        ft=file_type,
        in_dir=in_dir,
        out_dir=out_dir,
        date="02/02/2025",
        lab=2,
        ex_count=1,
    )

    target = out_dir / "Lab02Ex01.java"
    assert result.created == [target]
    assert target.is_file()
    assert not (in_dir / "_Lab02Ex01.java").exists()
    assert "02/02/2025" in target.read_text(encoding="utf-8")


def test_unmatched_template_is_reported_but_file_written(
    tmp_path: Path,
) -> None:
    file_type = FileType(
        name="TwoLines",
        ext="py",
        inpath=str(tmp_path),
        outpath=str(tmp_path),
        text=[("# A:", "1"), ("# B:", "2")],
    )
    in_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    _write(in_dir, "lab01ex01.py", "# A:\nprint('x')\n")

    result = create_files(
        ft=file_type,
        in_dir=in_dir,
        out_dir=out_dir,
        date="01/01/2025",
        lab=1,
        ex_count=1,
    )

    assert result.missing_template == ["Lab01Ex01.py"]
    assert (out_dir / "Lab01Ex01.py").is_file()


def test_source_file_is_deleted_after_success(
    tmp_path: Path, sample_type: FileType
) -> None:
    in_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    source = _write(in_dir, "lab01ex01.py", PY_SOURCE)

    create_files(
        ft=sample_type,
        in_dir=in_dir,
        out_dir=out_dir,
        date="01/01/2025",
        lab=1,
        ex_count=1,
    )

    assert not source.exists()
