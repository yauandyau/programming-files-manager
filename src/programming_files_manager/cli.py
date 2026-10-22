"""Command-line interface for programming-files-manager."""

from __future__ import annotations

import argparse
import datetime
import logging
import sys
from pathlib import Path

from .config import CSV_FILE, DEFAULT_TYPES
from .logging_config import setup_logging
from .models import FileType
from .service import create_files
from .storage import load_csv

logger = logging.getLogger(__name__)

DATE_FORMAT = "%d/%m/%Y"


def _bounded_int(value: str) -> int:
    """argparse type for a 0..99 non-negative integer."""
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{value!r} is not an integer") from exc

    if not 0 <= number <= 99:
        raise argparse.ArgumentTypeError("must be between 0 and 99")

    return number


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pfm",
        description="Create course programming files from reusable templates.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="enable debug logging",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=CSV_FILE,
        help=f"catalogue file to use (default: {CSV_FILE})",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "list-types",
        help="list the configured file types",
    )

    subparsers.add_parser(
        "gui",
        help="launch the Tkinter interface",
    )

    create = subparsers.add_parser(
        "create",
        help="create files for one file type",
    )
    create.add_argument("type", help="name of the file type")
    create.add_argument(
        "--in",
        dest="in_dir",
        type=Path,
        required=True,
        help="directory containing the source files",
    )
    create.add_argument(
        "--out",
        dest="out_dir",
        type=Path,
        required=True,
        help="directory that will receive the generated files",
    )
    create.add_argument(
        "--date",
        default=datetime.date.today().strftime(DATE_FORMAT),
        help=f"value substituted for {{date}} (default: today, {DATE_FORMAT})",
    )
    create.add_argument(
        "--lab",
        type=_bounded_int,
        required=True,
        help="lab number (0-99)",
    )
    create.add_argument(
        "--ex",
        dest="ex_count",
        type=_bounded_int,
        required=True,
        help="number of exercises to generate (0-99)",
    )

    return parser


def _load_types(csv_path: Path, *, bootstrap: bool) -> dict[str, FileType]:
    """Load the catalogue, optionally creating it from the defaults."""
    if bootstrap:
        return load_csv(csv_path, DEFAULT_TYPES)

    if not csv_path.exists():
        logger.info("No catalogue at %s, showing built-in defaults", csv_path)
        return dict(DEFAULT_TYPES)

    return load_csv(csv_path)


def _print_types(data: dict[str, FileType]) -> None:
    if not data:
        print("no file types configured")
        return

    width = max(len(name) for name in data)
    for name in sorted(data):
        file_type = data[name]
        print(
            f"{name:<{width}}  .{file_type.ext:<6}  "
            f"in={file_type.inpath}  out={file_type.outpath}"
        )


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""
    args = _build_parser().parse_args(argv)
    setup_logging(verbose=bool(args.verbose))

    csv_path = Path(args.csv)

    if args.command == "gui":
        # Imported lazily so that a machine without Tk can still use the CLI.
        from .gui.app import main as gui_main

        gui_main(csv_path)
        return 0

    try:
        data = _load_types(csv_path, bootstrap=args.command != "list-types")
    except (OSError, ValueError) as exc:
        logger.error("Could not load %s: %s", csv_path, exc)
        print(f"error: could not load {csv_path}: {exc}", file=sys.stderr)
        return 1

    if args.command == "list-types":
        _print_types(data)
        return 0

    file_type = data.get(args.type)
    if file_type is None:
        logger.error("Unknown file type: %s", args.type)
        print(f"error: unknown file type {args.type!r}", file=sys.stderr)
        return 2

    try:
        result = create_files(
            ft=file_type,
            in_dir=Path(args.in_dir),
            out_dir=Path(args.out_dir),
            date=args.date,
            lab=args.lab,
            ex_count=args.ex_count,
        )
    except OSError as exc:
        logger.error("Could not create files: %s", exc)
        print(f"error: could not create files: {exc}", file=sys.stderr)
        return 1

    for path in result.created:
        print(f"created {path}")
    for path, reason in result.skipped:
        print(f"skipped {path}: {reason}")
    for name in result.missing_template:
        print(f"warning: template not fully applied to {name}")

    logger.info(
        "Created %d file(s), skipped %d",
        len(result.created),
        len(result.skipped),
    )
    return 0 if result.created else 1
