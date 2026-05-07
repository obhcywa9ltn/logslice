"""logslice — lightweight structured log parser, filter, and processor."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("logslice")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"

from logslice.aggregator import count_by_field, format_aggregation, group_by_field, top_values
from logslice.deduplicator import count_duplicates, deduplicate_entries
from logslice.enricher import enrich_entries, enrich_entry
from logslice.exporter import export_as_csv, export_as_ndjson, export_as_tsv, export_entries
from logslice.filter import filter_by_time_range, filter_entries, match_field_patterns
from logslice.formatter import (
    format_entries,
    format_entry_compact,
    format_entry_json,
    format_entry_pretty,
)
from logslice.parser import iter_log_entries, parse_log_line, parse_timestamp
from logslice.pipeline import build_pipeline
from logslice.redactor import redact_entries, redact_entry
from logslice.sampler import head_entries, sample_entries, sample_every_nth
from logslice.schema import Schema, validate_entry
from logslice.stats import compute_stats, format_stats
from logslice.transformer import (
    add_fields,
    drop_fields,
    rename_fields,
    transform_entries,
    transform_entry,
)
from logslice.writer import open_output, write_entries, write_to_path

__all__ = [
    "__version__",
    # parser
    "parse_timestamp",
    "parse_log_line",
    "iter_log_entries",
    # filter
    "match_field_patterns",
    "filter_by_time_range",
    "filter_entries",
    # formatter
    "format_entry_json",
    "format_entry_pretty",
    "format_entry_compact",
    "format_entries",
    # writer
    "open_output",
    "write_entries",
    "write_to_path",
    # stats
    "compute_stats",
    "format_stats",
    # sampler
    "sample_entries",
    "sample_every_nth",
    "head_entries",
    # deduplicator
    "deduplicate_entries",
    "count_duplicates",
    # redactor
    "redact_entry",
    "redact_entries",
    # aggregator
    "group_by_field",
    "count_by_field",
    "top_values",
    "format_aggregation",
    # transformer
    "transform_entry",
    "rename_fields",
    "drop_fields",
    "add_fields",
    "transform_entries",
    # pipeline
    "build_pipeline",
    # exporter
    "export_as_ndjson",
    "export_as_csv",
    "export_as_tsv",
    "export_entries",
    # schema
    "Schema",
    "validate_entry",
    # enricher
    "enrich_entry",
    "enrich_entries",
]
