"""logslice — lightweight structured log parser and processor."""

from __future__ import annotations

from logslice.aggregator import count_by_field, format_aggregation, group_by_field, top_values
from logslice.deduplicator import count_duplicates, deduplicate_entries
from logslice.exporter import export_entries
from logslice.filter import filter_entries
from logslice.formatter import format_entries
from logslice.parser import iter_log_entries, parse_log_line
from logslice.pipeline import build_pipeline
from logslice.redactor import redact_entries
from logslice.sampler import head_entries, sample_entries, sample_every_nth
from logslice.schema import FieldSpec, Schema, validate_entries
from logslice.stats import compute_stats, format_stats
from logslice.transformer import transform_entries
from logslice.writer import write_entries, write_to_path

__all__ = [
    # parser
    "parse_log_line",
    "iter_log_entries",
    # filter
    "filter_entries",
    # formatter
    "format_entries",
    # writer
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
    "redact_entries",
    # aggregator
    "group_by_field",
    "count_by_field",
    "top_values",
    "format_aggregation",
    # transformer
    "transform_entries",
    # pipeline
    "build_pipeline",
    # exporter
    "export_entries",
    # schema
    "FieldSpec",
    "Schema",
    "validate_entries",
]
