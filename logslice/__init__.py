"""logslice — lightweight structured log parser and processor.

Public re-exports are grouped by module so callers can do::

    from logslice import parse_log_line, filter_entries, run_query
"""

# parser
from logslice.parser import iter_log_entries, parse_log_line, parse_timestamp

# filter
from logslice.filter import filter_by_time_range, filter_entries, match_field_patterns

# formatter
from logslice.formatter import (
    format_entries,
    format_entry_compact,
    format_entry_json,
    format_entry_pretty,
)

# writer
from logslice.writer import open_output, write_entries, write_to_path

# stats
from logslice.stats import compute_stats, format_stats

# sampler
from logslice.sampler import head_entries, sample_entries, sample_every_nth

# deduplicator
from logslice.deduplicator import count_duplicates, deduplicate_entries

# redactor
from logslice.redactor import redact_entries, redact_entry

# aggregator
from logslice.aggregator import (
    count_by_field,
    format_aggregation,
    group_by_field,
    top_values,
)

# transformer
from logslice.transformer import (
    add_fields,
    drop_fields,
    rename_fields,
    transform_entries,
    transform_entry,
)

# pipeline
from logslice.pipeline import build_pipeline

# exporter
from logslice.exporter import export_as_csv, export_as_ndjson, export_as_tsv, export_entries

# schema
from logslice.schema import Schema, FieldSpec, is_valid, validate_entry

# enricher
from logslice.enricher import enrich_entries, enrich_entry

# highlighter
from logslice.highlighter import highlight_entry, highlight_level, highlight_pattern

# sorter
from logslice.sorter import sort_by_timestamp, sort_entries

# splitter
from logslice.splitter import split_by_field, split_by_predicate, split_by_rules

# router
from logslice.router import Router, build_router

# merger
from logslice.merger import merge_all, merge_entries

# truncator
from logslice.truncator import truncate_entries, truncate_entry, truncate_value

# ratelimiter
from logslice.ratelimiter import count_by_bucket, rate_limit_entries

# annotator
from logslice.annotator import annotate_entries, annotate_entry

# checkpoint
from logslice.checkpoint import (
    delete_checkpoint,
    get_offset,
    load_checkpoint,
    save_checkpoint,
)

# watchdog
from logslice.watchdog import tail_file, watch_entries

# limiter
from logslice.limiter import counts_by_field, limit_by_field, limit_total

# correlator
from logslice.correlator import (
    correlation_summary,
    find_by_correlation_id,
    group_by_correlation_id,
    iter_correlated,
)

# masker
from logslice.masker import mask_entries, mask_entry

# tagger
from logslice.tagger import build_rule as build_tag_rule
from logslice.tagger import filter_by_tag, tag_entries, tag_entry

# alerter
from logslice.alerter import alert_entries, build_rule as build_alert_rule
from logslice.alerter import check_entry

# notifier
from logslice.notifier import console_notifier, json_notifier, collecting_notifier

# alert_pipeline
from logslice.alert_pipeline import (
    build_alert_pipeline,
    monitored_pipeline,
    rules_from_config,
    run_and_report,
)

# batcher
from logslice.batcher import batch_by_size, batch_by_time, flatten_batches

# profiler
from logslice.profiler import format_profile, profile_entries

# indexer
from logslice.indexer import build_index, index_keys, lookup, lookup_many, reindex

# query
from logslice.query import Query, run_indexed_query, run_query

__all__ = [
    # parser
    "parse_timestamp", "parse_log_line", "iter_log_entries",
    # filter
    "match_field_patterns", "filter_by_time_range", "filter_entries",
    # formatter
    "format_entry_json", "format_entry_pretty", "format_entry_compact", "format_entries",
    # writer
    "open_output", "write_entries", "write_to_path",
    # stats
    "compute_stats", "format_stats",
    # sampler
    "sample_entries", "sample_every_nth", "head_entries",
    # deduplicator
    "deduplicate_entries", "count_duplicates",
    # redactor
    "redact_entry", "redact_entries",
    # aggregator
    "group_by_field", "count_by_field", "top_values", "format_aggregation",
    # transformer
    "transform_entry", "rename_fields", "drop_fields", "add_fields", "transform_entries",
    # pipeline
    "build_pipeline",
    # exporter
    "export_as_ndjson", "export_as_csv", "export_as_tsv", "export_entries",
    # schema
    "FieldSpec", "Schema", "validate_entry", "is_valid",
    # enricher
    "enrich_entry", "enrich_entries",
    # highlighter
    "highlight_level", "highlight_pattern", "highlight_entry",
    # sorter
    "sort_entries", "sort_by_timestamp",
    # splitter
    "split_by_field", "split_by_predicate", "split_by_rules",
    # router
    "Router", "build_router",
    # merger
    "merge_entries", "merge_all",
    # truncator
    "truncate_value", "truncate_entry", "truncate_entries",
    # ratelimiter
    "rate_limit_entries", "count_by_bucket",
    # annotator
    "annotate_entry", "annotate_entries",
    # checkpoint
    "save_checkpoint", "load_checkpoint", "get_offset", "delete_checkpoint",
    # watchdog
    "tail_file", "watch_entries",
    # limiter
    "limit_by_field", "limit_total", "counts_by_field",
    # correlator
    "group_by_correlation_id", "iter_correlated", "find_by_correlation_id",
    "correlation_summary",
    # masker
    "mask_entry", "mask_entries",
    # tagger
    "tag_entry", "tag_entries", "build_tag_rule", "filter_by_tag",
    # alerter
    "check_entry", "alert_entries", "build_alert_rule",
    # notifier
    "console_notifier", "json_notifier", "collecting_notifier",
    # alert_pipeline
    "build_alert_pipeline", "rules_from_config", "run_and_report", "monitored_pipeline",
    # batcher
    "batch_by_size", "batch_by_time", "flatten_batches",
    # profiler
    "profile_entries", "format_profile",
    # indexer
    "build_index", "lookup", "lookup_many", "index_keys", "reindex",
    # query
    "Query", "run_query", "run_indexed_query",
]
