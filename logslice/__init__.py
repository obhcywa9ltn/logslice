"""logslice — lightweight structured log parser, filter, and processor.

Public re-exports for convenience.
"""

from logslice.aggregator import count_by_field, format_aggregation, group_by_field, top_values
from logslice.annotator import annotate_entries, annotate_entry
from logslice.checkpoint import delete_checkpoint, load_checkpoint, save_checkpoint
from logslice.correlator import (
    correlation_summary,
    find_by_correlation_id,
    group_by_correlation_id,
    iter_correlated,
)
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
from logslice.highlighter import highlight_entry, highlight_level, highlight_pattern
from logslice.limiter import counts_by_field, limit_by_field, limit_total
from logslice.masker import mask_entries, mask_entry
from logslice.merger import merge_all, merge_entries
from logslice.parser import iter_log_entries, parse_log_line, parse_timestamp
from logslice.pipeline import build_pipeline
from logslice.ratelimiter import count_by_bucket, rate_limit_entries
from logslice.redactor import redact_entries, redact_entry
from logslice.router import Router, build_router
from logslice.sampler import head_entries, sample_entries, sample_every_nth
from logslice.schema import Schema, validate_entry
from logslice.sorter import sort_by_timestamp, sort_entries
from logslice.splitter import split_by_field, split_by_predicate, split_by_rules
from logslice.stats import compute_stats, format_stats
from logslice.tagger import build_rule, filter_by_tag, tag_entries, tag_entry
from logslice.transformer import (
    add_fields,
    drop_fields,
    rename_fields,
    transform_entries,
    transform_entry,
)
from logslice.truncator import truncate_entries, truncate_entry, truncate_value
from logslice.watchdog import tail_file, watch_entries
from logslice.writer import open_output, write_entries, write_to_path

__all__ = [
    # aggregator
    "count_by_field",
    "format_aggregation",
    "group_by_field",
    "top_values",
    # annotator
    "annotate_entries",
    "annotate_entry",
    # checkpoint
    "delete_checkpoint",
    "load_checkpoint",
    "save_checkpoint",
    # correlator
    "correlation_summary",
    "find_by_correlation_id",
    "group_by_correlation_id",
    "iter_correlated",
    # deduplicator
    "count_duplicates",
    "deduplicate_entries",
    # enricher
    "enrich_entries",
    "enrich_entry",
    # exporter
    "export_as_csv",
    "export_as_ndjson",
    "export_as_tsv",
    "export_entries",
    # filter
    "filter_by_time_range",
    "filter_entries",
    "match_field_patterns",
    # formatter
    "format_entries",
    "format_entry_compact",
    "format_entry_json",
    "format_entry_pretty",
    # highlighter
    "highlight_entry",
    "highlight_level",
    "highlight_pattern",
    # limiter
    "counts_by_field",
    "limit_by_field",
    "limit_total",
    # masker
    "mask_entries",
    "mask_entry",
    # merger
    "merge_all",
    "merge_entries",
    # parser
    "iter_log_entries",
    "parse_log_line",
    "parse_timestamp",
    # pipeline
    "build_pipeline",
    # ratelimiter
    "count_by_bucket",
    "rate_limit_entries",
    # redactor
    "redact_entries",
    "redact_entry",
    # router
    "Router",
    "build_router",
    # sampler
    "head_entries",
    "sample_entries",
    "sample_every_nth",
    # schema
    "Schema",
    "validate_entry",
    # sorter
    "sort_by_timestamp",
    "sort_entries",
    # splitter
    "split_by_field",
    "split_by_predicate",
    "split_by_rules",
    # stats
    "compute_stats",
    "format_stats",
    # tagger
    "build_rule",
    "filter_by_tag",
    "tag_entries",
    "tag_entry",
    # transformer
    "add_fields",
    "drop_fields",
    "rename_fields",
    "transform_entries",
    "transform_entry",
    # truncator
    "truncate_entries",
    "truncate_entry",
    "truncate_value",
    # watchdog
    "tail_file",
    "watch_entries",
    # writer
    "open_output",
    "write_entries",
    "write_to_path",
]
