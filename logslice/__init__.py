"""logslice — lightweight JSON log parser and filter."""

from logslice.filter import filter_entries, filter_by_time_range, match_field_patterns
from logslice.parser import iter_log_entries, parse_log_line, parse_timestamp

__all__ = [
    "filter_entries",
    "filter_by_time_range",
    "match_field_patterns",
    "iter_log_entries",
    "parse_log_line",
    "parse_timestamp",
]

__version__ = "0.1.0"
