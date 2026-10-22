"""Domain models shared by storage, service, CLI and GUI."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FileType:
    """A configured file type.

    ``text`` holds ``(prefix, replacement)`` pairs.  A source line is rewritten
    when it starts with ``prefix``; the replacement may contain ``{date}``.
    """

    name: str
    ext: str
    inpath: str
    outpath: str
    text: list[tuple[str, str]]
    source_template: str | None = None
    target_template: str | None = None
