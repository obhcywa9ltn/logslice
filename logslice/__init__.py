"""logslice — lightweight structured log parser and filter."""

from logslice.parser import parse_log_line, iter_log_entries
from logslice.filter import filter_entries
from logslice.formatter import format_entries
from logslice.writer import write_entries
from logslice.stats import compute_stats
from logslice.sampler import sample_entries
from logslice.deduplicator import deduplicate_entries, count_duplicates

__all__ = [
    "parse_log_line",
    "iter_log_entries",
    "filter_entries",
    "format_entries",
    "write_entries",
    "compute_stats",
    "sample_entries",
    "deduplicate_entries",
    "count_duplicates",
]
