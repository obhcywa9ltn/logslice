"""Export log entries to various file formats (CSV, NDJSON, TSV)."""

from __future__ import annotations

import csv
import io
import json
from typing import Iterable, Iterator, Literal

ExportFormat = Literal["csv", "ndjson", "tsv"]

_DEFAULT_FIELDS = ["timestamp", "level", "message"]


def export_as_ndjson(entries: Iterable[dict]) -> Iterator[str]:
    """Yield each entry serialised as a single JSON line (NDJSON)."""
    for entry in entries:
        yield json.dumps(entry, default=str)


def export_as_csv(
    entries: Iterable[dict],
    fields: list[str] | None = None,
    delimiter: str = ",",
) -> Iterator[str]:
    """Yield CSV rows for *entries*, including a header row.

    If *fields* is not supplied the union of all keys found in the first
    entry is used; if no entries exist nothing is yielded.
    """
    entries = list(entries)
    if not entries:
        return

    if fields is None:
        seen: list[str] = []
        for entry in entries:
            for k in entry:
                if k not in seen:
                    seen.append(k)
        fields = seen

    buf = io.StringIO()
    writer = csv.DictWriter(
        buf,
        fieldnames=fields,
        delimiter=delimiter,
        extrasaction="ignore",
        lineterminator="\n",
    )
    writer.writeheader()
    yield buf.getvalue()

    for entry in entries:
        buf = io.StringIO()
        writer = csv.DictWriter(
            buf,
            fieldnames=fields,
            delimiter=delimiter,
            extrasaction="ignore",
            lineterminator="\n",
        )
        row = {f: entry.get(f, "") for f in fields}
        writer.writerow(row)
        yield buf.getvalue()


def export_as_tsv(
    entries: Iterable[dict],
    fields: list[str] | None = None,
) -> Iterator[str]:
    """Yield TSV rows — thin wrapper around :func:`export_as_csv`."""
    yield from export_as_csv(entries, fields=fields, delimiter="\t")


def export_entries(
    entries: Iterable[dict],
    fmt: ExportFormat = "ndjson",
    fields: list[str] | None = None,
) -> Iterator[str]:
    """Dispatch to the appropriate exporter based on *fmt*."""
    if fmt == "ndjson":
        yield from export_as_ndjson(entries)
    elif fmt == "csv":
        yield from export_as_csv(entries, fields=fields)
    elif fmt == "tsv":
        yield from export_as_tsv(entries, fields=fields)
    else:
        raise ValueError(f"Unsupported export format: {fmt!r}")
