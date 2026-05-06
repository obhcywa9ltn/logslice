"""logslice — A lightweight log parser that extracts and filters structured JSON logs."""

from logslice.aggregator import (
    count_by_field,
    format_aggregation,
    group_by_field,
    top_values,
)
from logslice.deduplicator import count_duplicates, deduplicate_entries
from logslice.filter import filter_entries, filter_by_time_range, match_field_patterns
from logslice.formatter import (
    format_entries,
    format_entry_compact,
    format_entry_json,
    format_entry_pretty,
)
from logslice.parser import iter_log_entries, parse_log_line, parse_timestamp
from logslice.redactor import redact_entries, redact_entry
from logslice.sampler import head_entries, sample_entries, sample_every_nth
from logslice.stats import compute_stats, format_stats
from logslice.writer import open_output, write_entries, write_to_path

__all__ = [
    "count_by_field",
    "count_duplicates",
    "compute_stats",
    "deduplicate_entries",
    "filter_entries",
    "filter_by_time_range",
    "format_aggregation",
    "format_entries",
    "format_entry_compact",
    "format_entry_json",
    "format_entry_pretty",
    "format_stats",
    "group_by_field",
    "head_entries",
    "iter_log_entries",
    "match_field_patterns",
    "open_output",
    "parse_log_line",
    "parse_timestamp",
    "redact_entries",
    "redact_entry",
    "sample_entries",
    "sample_every_nth",
    "top_values",
    "write_entries",
    "write_to_path",
]
