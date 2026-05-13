"""logslice — lightweight structured log parser and processor.

Public re-exports for the most commonly used symbols across the package.
"""

from logslice.parser import parse_log_line, iter_log_entries, parse_timestamp
from logslice.filter import filter_entries, filter_by_time_range, match_field_patterns
from logslice.formatter import (
    format_entry_json,
    format_entry_pretty,
    format_entry_compact,
    format_entries,
)
from logslice.writer import write_entries, write_to_path, open_output
from logslice.stats import compute_stats, format_stats
from logslice.sampler import sample_entries, sample_every_nth, head_entries
from logslice.deduplicator import deduplicate_entries, count_duplicates
from logslice.redactor import redact_entry, redact_entries
from logslice.aggregator import group_by_field, count_by_field, top_values, format_aggregation
from logslice.transformer import (
    transform_entry,
    rename_fields,
    drop_fields,
    add_fields,
    transform_entries,
)
from logslice.pipeline import build_pipeline
from logslice.exporter import export_as_ndjson, export_as_csv, export_as_tsv, export_entries
from logslice.schema import Schema, FieldSpec, validate_entry, is_valid
from logslice.enricher import enrich_entry, enrich_entries
from logslice.highlighter import highlight_entry, highlight_level, highlight_pattern
from logslice.sorter import sort_entries, sort_by_timestamp
from logslice.splitter import split_by_field, split_by_predicate, split_by_rules
from logslice.router import Router, build_router
from logslice.merger import merge_entries, merge_all
from logslice.truncator import truncate_entry, truncate_entries, truncate_value
from logslice.ratelimiter import rate_limit_entries, count_by_bucket
from logslice.annotator import annotate_entry, annotate_entries
from logslice.checkpoint import save_checkpoint, load_checkpoint, get_offset, delete_checkpoint
from logslice.watchdog import tail_file, watch_entries
from logslice.limiter import limit_by_field, limit_total
from logslice.correlator import (
    group_by_correlation_id,
    iter_correlated,
    find_by_correlation_id,
    correlation_summary,
)
from logslice.masker import mask_entry, mask_entries
from logslice.tagger import tag_entry, tag_entries, build_rule as build_tag_rule, filter_by_tag
from logslice.alerter import check_entry, alert_entries, build_rule as build_alert_rule
from logslice.notifier import console_notifier, collecting_notifier, json_notifier
from logslice.alert_pipeline import build_alert_pipeline, run_and_report, monitored_pipeline
from logslice.batcher import batch_by_size, batch_by_time, flatten_batches

__all__ = [
    # parser
    "parse_log_line",
    "iter_log_entries",
    "parse_timestamp",
    # filter
    "filter_entries",
    "filter_by_time_range",
    "match_field_patterns",
    # formatter
    "format_entry_json",
    "format_entry_pretty",
    "format_entry_compact",
    "format_entries",
    # writer
    "write_entries",
    "write_to_path",
    "open_output",
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
    "FieldSpec",
    "validate_entry",
    "is_valid",
    # enricher
    "enrich_entry",
    "enrich_entries",
    # highlighter
    "highlight_entry",
    "highlight_level",
    "highlight_pattern",
    # sorter
    "sort_entries",
    "sort_by_timestamp",
    # splitter
    "split_by_field",
    "split_by_predicate",
    "split_by_rules",
    # router
    "Router",
    "build_router",
    # merger
    "merge_entries",
    "merge_all",
    # truncator
    "truncate_entry",
    "truncate_entries",
    "truncate_value",
    # ratelimiter
    "rate_limit_entries",
    "count_by_bucket",
    # annotator
    "annotate_entry",
    "annotate_entries",
    # checkpoint
    "save_checkpoint",
    "load_checkpoint",
    "get_offset",
    "delete_checkpoint",
    # watchdog
    "tail_file",
    "watch_entries",
    # limiter
    "limit_by_field",
    "limit_total",
    # correlator
    "group_by_correlation_id",
    "iter_correlated",
    "find_by_correlation_id",
    "correlation_summary",
    # masker
    "mask_entry",
    "mask_entries",
    # tagger
    "tag_entry",
    "tag_entries",
    "build_tag_rule",
    "filter_by_tag",
    # alerter
    "check_entry",
    "alert_entries",
    "build_alert_rule",
    # notifier
    "console_notifier",
    "collecting_notifier",
    "json_notifier",
    # alert_pipeline
    "build_alert_pipeline",
    "run_and_report",
    "monitored_pipeline",
    # batcher
    "batch_by_size",
    "batch_by_time",
    "flatten_batches",
]
