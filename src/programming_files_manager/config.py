"""Static configuration and the built-in default catalogue."""

from __future__ import annotations

from pathlib import Path

from .models import FileType

CSV_FILE = Path("file_types.csv")

#: Exactly five columns, in the same order written by ``storage.save_csv``:
#: name, ext, inpath, outpath, text (JSON).
HEADER = ["文件類型", "副檔名", "默認輸入路徑", "默認輸出路徑", "文字"]

_DOWNLOADS = Path.home() / "Downloads"

DEFAULT_TYPES: dict[str, FileType] = {
    "CSCI2040": FileType(
        name="CSCI2040",
        ext="py",
        inpath=str(_DOWNLOADS),
        outpath=str(_DOWNLOADS / "CSCI2040"),
        text=[
            ("# Student Name :", ""),
            ("# Student ID   :", ""),
            ("# Class/Section:", "CSCI2040"),
            ("# Date         :", "{date}"),
        ],
    ),
    "ENGG1110": FileType(
        name="ENGG1110",
        ext="c",
        inpath=str(_DOWNLOADS),
        outpath=str(_DOWNLOADS / "ENGG1110"),
        text=[
            (" * Student Name :", ""),
            (" * Student ID   :", ""),
            (" * Class/Section:", "ENGG1110"),
            (" * Date         :", "{date}"),
        ],
    ),
    "CSCI1130": FileType(
        name="CSCI1130",
        ext="java",
        inpath=str(_DOWNLOADS),
        outpath=str(_DOWNLOADS / "CSCI1130"),
        text=[
            (" * Student Name :", ""),
            (" * Student ID   :", ""),
            (" * Class/Section:", "CSCI1130"),
            (" * Date         :", "{date}"),
        ],
        source_template="_Lab{lab:02d}Ex{ex:02d}.java",
        target_template="Lab{lab:02d}Ex{ex:02d}.java",
    ),
}
