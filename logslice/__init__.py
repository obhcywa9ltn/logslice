"""logslice — lightweight structured-log processing toolkit.

Public re-exports keep the top-level namespace stable; individual modules can
be imported directly for finer control.
"""

from logslice.parser import parse_log_line, iter_log_entries, parse_timestamp
from logslice.filter import filter_entries, filter_by_time_range, match_field_patterns
from logslice.formatter import (
    format_entry_json,
    format_entry_pretty,
    format_entry_compact,
    format_entries,
)
from logslice.writer import write_entries, write_to_path
from logslice.stats import compute_stats, format_stats
from logslice.sampler import sample_entries, sample_every_nth, head_entries
from logslice.deduplicator import deduplicate_entries, count_duplicates
from logslice.redactor import redact_entry, redact_entries
from logslice.aggregator import group_by_field, count_by_field, top_values
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
from logslice.highlighter import highlight_entry
from logslice.sorter import sort_entries, sort_by_timestamp
from logslice.splitter import split_by_field, split_by_predicate, split_by_rules
from logslice.router import Router, build_router
from logslice.merger import merge_entries, merge_all
from logslice.truncator import truncate_entry, truncate_entries
from logslice.ratelimiter import rate_limit_entries
from logslice.annotator import annotate_entry, annotate_entries
from logslice.limiter import limit_by_field, limit_total
from logslice.correlator import group_by_correlation_id, iter_correlated
from logslice.masker import mask_entry, mask_entries
from logslice.tagger import tag_entry, tag_entries
from logslice.alerter import check_entry, alert_entries
from logslice.batcher import batch_by_size, batch_by_time, flatten_batches
from logslice.profiler import profile_entries
from logslice.indexer import build_index, lookup, lookup_many
from logslice.query import Query, run_query, run_indexed_query
from logslice.replayer import replay_entries
from logslice.summarizer import summarize_entries, format_summary
from logslice.classifier import classify_entry, classify_entries
from logslice.differ import diff_entries, format_diff, DiffResult

__all__ = [
    # parser
    "parse_log_line", "iter_log_entries", "parse_timestamp",
    # filter
    "filter_entries", "filter_by_time_range", "match_field_patterns",
    # formatter
    "format_entry_json", "format_entry_pretty", "format_entry_compact", "format_entries",
    # writer
    "write_entries", "write_to_path",
    # stats
    "compute_stats", "format_stats",
    # sampler
    "sample_entries", "sample_every_nth", "head_entries",
    # deduplicator
    "deduplicate_entries", "count_duplicates",
    # redactor
    "redact_entry", "redact_entries",
    # aggregator
    "group_by_field", "count_by_field", "top_values",
    # transformer
    "transform_entry", "rename_fields", "drop_fields", "add_fields", "transform_entries",
    # pipeline
    "build_pipeline",
    # exporter
    "export_as_ndjson", "export_as_csv", "export_as_tsv", "export_entries",
    # schema
    "Schema", "FieldSpec", "validate_entry", "is_valid",
    # enricher
    "enrich_entry", "enrich_entries",
    # highlighter
    "highlight_entry",
    # sorter
    "sort_entries", "sort_by_timestamp",
    # splitter
    "split_by_field", "split_by_predicate", "split_by_rules",
    # router
    "Router", "build_router",
    # merger
    "merge_entries", "merge_all",
    # truncator
    "truncate_entry", "truncate_entries",
    # ratelimiter
    "rate_limit_entries",
    # annotator
    "annotate_entry", "annotate_entries",
    # limiter
    "limit_by_field", "limit_total",
    # correlator
    "group_by_correlation_id", "iter_correlated",
    # masker
    "mask_entry", "mask_entries",
    # tagger
    "tag_entry", "tag_entries",
    # alerter
    "check_entry", "alert_entries",
    # batcher
    "batch_by_size", "batch_by_time", "flatten_batches",
    # profiler
    "profile_entries",
    # indexer
    "build_index", "lookup", "lookup_many",
    # query
    "Query", "run_query", "run_indexed_query",
    # replayer
    "replay_entries",
    # summarizer
    "summarize_entries", "format_summary",
    # classifier
    "classify_entry", "classify_entries",
    # differ
    "diff_entries", "format_diff", "DiffResult",
]
