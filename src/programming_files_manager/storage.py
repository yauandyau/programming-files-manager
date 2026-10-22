"""CSV persistence for the file-type catalogue.

Pure I/O only: no Tkinter, no dialogs, no exit codes.  Errors are raised so
that the caller (CLI or GUI) can decide how to report them.
"""

from __future__ import annotations

import copy
import csv
import json
import logging
from collections.abc import Mapping
from pathlib import Path

from .config import HEADER
from .models import FileType

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = len(HEADER)


def save_csv(path: Path, data: Mapping[str, FileType]) -> None:
    """Write ``data`` to ``path`` as a UTF-8-BOM CSV file.

    Parent directories are created automatically.  Serialisation errors are
    intentionally not swallowed.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(HEADER)
        for file_type in data.values():
            writer.writerow(
                [
                    file_type.name,
                    file_type.ext,
                    file_type.inpath,
                    file_type.outpath,
                    json.dumps(file_type.text, ensure_ascii=False),
                ]
            )

    logger.info("Saved %d file type(s) to %s", len(data), path)


def load_csv(
    path: Path,
    defaults: Mapping[str, FileType] | None = None,
) -> dict[str, FileType]:
    """Load ``path``, optionally bootstrapping it from ``defaults``.

    * missing file + ``defaults`` -> write the defaults and return a copy;
    * missing file + no ``defaults`` -> :class:`FileNotFoundError`;
    * rows with fewer than five columns, empty names or the header are skipped;
    * invalid JSON is *not* caught here and propagates to the caller.

    The five-column format cannot store the optional rename templates.  When a
    ``defaults`` mapping is supplied, those two fields are therefore restored
    from the matching default entry (if any) by name.
    """
    path = Path(path)

    if not path.exists():
        if defaults is None:
            raise FileNotFoundError(f"CSV file not found: {path}")

        seeded = copy.deepcopy(dict(defaults))
        save_csv(path, seeded)
        logger.info("Created default CSV: %s", path)
        return seeded

    data: dict[str, FileType] = {}
    fallbacks: Mapping[str, FileType] = defaults if defaults is not None else {}

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.reader(handle):
            if len(row) < REQUIRED_COLUMNS:
                logger.debug("Skipping short row: %r", row)
                continue

            name = row[0].strip()
            if not name or name == HEADER[0]:
                continue

            raw_text = json.loads(row[4])
            text = [(str(pair[0]), str(pair[1])) for pair in raw_text]
            fallback = fallbacks.get(name)

            data[name] = FileType(
                name=name,
                ext=row[1].strip(),
                inpath=row[2].strip(),
                outpath=row[3].strip(),
                text=text,
                source_template=(
                    fallback.source_template if fallback is not None else None
                ),
                target_template=(
                    fallback.target_template if fallback is not None else None
                ),
            )

    logger.info("Loaded %d file type(s) from %s", len(data), path)
    return data
