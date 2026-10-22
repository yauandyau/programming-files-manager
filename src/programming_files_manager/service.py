"""File-creation business logic.

Fully parameterised: this module never reads global state, never shows a
dialog and never calls ``sys.exit``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from .models import FileType

logger = logging.getLogger(__name__)

DEFAULT_SOURCE_TEMPLATE = "lab{lab:02d}ex{ex:02d}.{ext}"
DEFAULT_TARGET_TEMPLATE = "Lab{lab:02d}Ex{ex:02d}.{ext}"


@dataclass
class CreateResult:
    """Outcome of a single :func:`create_files` call."""

    created: list[Path] = field(default_factory=list)
    skipped: list[tuple[Path, str]] = field(default_factory=list)
    missing_template: list[str] = field(default_factory=list)


def _render_template(
    template: str | None,
    fallback: str,
    *,
    ext: str,
    lab: int,
    ex: int,
) -> str:
    """Render a file-name template, falling back to the default one."""
    return (template or fallback).format(lab=lab, ex=ex, ext=ext)


def create_files(
    *,
    ft: FileType,
    in_dir: Path,
    out_dir: Path,
    date: str,
    lab: int,
    ex_count: int,
) -> CreateResult:
    """Create ``ex_count`` files for ``ft`` by rewriting template lines.

    Source files that do not exist (or cannot be read) are recorded in
    ``CreateResult.skipped``.  When not every configured template prefix is
    found the destination name is recorded in ``missing_template``, but the
    file is still written.
    """
    result = CreateResult()
    in_dir = Path(in_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    patterns = [
        (prefix, value)
        for prefix, value in ft.text
        if prefix.strip()
    ]

    for ex in range(1, ex_count + 1):
        source_name = _render_template(
            ft.source_template,
            DEFAULT_SOURCE_TEMPLATE,
            ext=ft.ext,
            lab=lab,
            ex=ex,
        )
        target_name = _render_template(
            ft.target_template,
            DEFAULT_TARGET_TEMPLATE,
            ext=ft.ext,
            lab=lab,
            ex=ex,
        )

        source = in_dir / source_name
        target = out_dir / target_name

        if not source.is_file():
            result.skipped.append((source, "source file not found"))
            logger.warning("Source file not found: %s", source)
            continue

        try:
            lines = source.read_text(encoding="utf-8").splitlines(keepends=True)
        except OSError as exc:
            result.skipped.append((source, str(exc)))
            logger.warning("Could not read %s: %s", source, exc)
            continue

        matched = 0
        for index, line in enumerate(lines):
            for prefix, value in patterns:
                if line.startswith(prefix):
                    lines[index] = f"{prefix} {value.replace('{date}', date)}\n"
                    matched += 1
            if patterns and matched >= len(patterns):
                break

        if patterns and matched < len(patterns):
            result.missing_template.append(target.name)
            logger.warning(
                "Template not fully applied to %s (%d/%d)",
                target.name,
                matched,
                len(patterns),
            )

        try:
            target.write_text("".join(lines), encoding="utf-8")
        except OSError as exc:
            result.skipped.append((target, str(exc)))
            logger.warning("Could not write %s: %s", target, exc)
            continue

        result.created.append(target)

        try:
            source.unlink()
        except OSError as exc:
            logger.warning("Could not remove source file %s: %s", source, exc)

    logger.info(
        "Created %d file(s) for %s, skipped %d",
        len(result.created),
        ft.name or ft.ext,
        len(result.skipped),
    )
    return result
