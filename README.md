# logslice

A lightweight log parser that extracts and filters structured JSON logs by time
range and field patterns.

## Installation

```bash
pip install logslice
```

## Quick start

```python
from logslice import iter_log_entries, filter_entries, diff_entries, format_diff

with open("app.log") as fh:
    entries = list(iter_log_entries(fh))

# filter by time range and field patterns
filtered = list(filter_entries(entries, patterns={"level": "error"}))

# diff two log snapshots keyed by request-id
for result in diff_entries(baseline, current, key_field="request_id",
                            ignore_fields=["timestamp"]):
    print(format_diff(result))
```

## CLI

```bash
logslice --start "2024-01-01T00:00:00" --end "2024-01-02T00:00:00" \
         --pattern level=error app.log
```

## Modules

| Module | Purpose |
|---|---|
| `parser` | Parse raw log lines into entry dicts |
| `filter` | Filter entries by time range / field patterns |
| `formatter` | Render entries as JSON / pretty / compact |
| `writer` | Write formatted entries to a file or stdout |
| `stats` | Compute summary statistics over a stream |
| `sampler` | Random sampling and head/tail helpers |
| `deduplicator` | Remove duplicate entries by fingerprint |
| `redactor` | Scrub sensitive fields |
| `aggregator` | Group and count entries by field value |
| `transformer` | Rename, drop, add, or transform fields |
| `pipeline` | Compose processing steps into a single pipeline |
| `exporter` | Export to NDJSON, CSV, or TSV |
| `schema` | Validate entries against a field schema |
| `enricher` | Add derived or static fields to entries |
| `highlighter` | ANSI-colour entries for terminal output |
| `sorter` | Sort entries by timestamp or arbitrary field |
| `splitter` | Partition entries into named groups |
| `router` | Route entries to multiple sinks by predicate |
| `merger` | Merge sorted streams in timestamp order |
| `truncator` | Truncate long field values |
| `ratelimiter` | Bucket-based rate limiting |
| `annotator` | Attach computed annotations to entries |
| `checkpoint` | Persist and resume file-read positions |
| `watchdog` | Tail log files for new entries in real time |
| `limiter` | Cap entry counts per field value |
| `correlator` | Group entries by correlation / trace ID |
| `masker` | Partially mask sensitive string values |
| `tagger` | Apply rule-based tags to entries |
| `alerter` | Fire alerts when entries match rules |
| `notifier` | Deliver alert notifications (console, JSON, …) |
| `alert_pipeline` | High-level alert pipeline builder |
| `batcher` | Batch entries by size or time window |
| `profiler` | Measure throughput and elapsed time |
| `indexer` | Build in-memory field indexes for fast lookup |
| `query` | Structured query execution over entry streams |
| `replayer` | Replay entries at original or scaled wall-clock speed |
| `summarizer` | Generate human-readable stream summaries |
| `classifier` | Classify entries with named predicate rules |
| `differ` | Diff two entry streams and report added/removed/changed |

## Differ

The `differ` module compares two snapshots of log entries and yields
`DiffResult` named-tuples describing what changed:

```python
from logslice.differ import diff_entries, format_diff

for result in diff_entries(old_entries, new_entries,
                            key_field="id",
                            ignore_fields=["timestamp"]):
    # result.status  -> 'added' | 'removed' | 'changed'
    # result.key     -> the key field value
    # result.changed_fields -> list of field names that differ
    print(format_diff(result))
```

## License

MIT
