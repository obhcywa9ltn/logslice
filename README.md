# logslice

A lightweight log parser that extracts and filters structured JSON logs by time range and field patterns.

## Features

- **Parse** — read NDJSON log streams line by line (`parser`)
- **Filter** — narrow entries by time range and field regex patterns (`filter`)
- **Format** — render entries as JSON, pretty-printed, or compact text (`formatter`)
- **Write** — stream output to stdout or a file (`writer`)
- **Stats** — summarise a log stream (counts, levels, time span) (`stats`)
- **Sample** — probabilistic or deterministic sub-sampling (`sampler`)
- **Deduplicate** — remove repeated entries by content fingerprint (`deduplicator`)
- **Redact** — strip sensitive fields before output (`redactor`)
- **Aggregate** — group and count by any field (`aggregator`)
- **Transform** — rename, drop, add, or map fields (`transformer`)
- **Pipeline** — compose all steps into a single generator chain (`pipeline`)
- **Export** — emit NDJSON, CSV, or TSV (`exporter`)
- **Schema** — validate entries against a field specification (`schema`)
- **Enrich** — attach computed or static fields (`enricher`)
- **Highlight** — ANSI-colour entries for terminal output (`highlighter`)
- **Sort** — order entries by timestamp or any field (`sorter`)
- **Split** — partition a stream into named buckets (`splitter`)
- **Route** — dispatch entries to multiple sinks by predicate (`router`)
- **Merge** — interleave pre-sorted streams in timestamp order (`merger`)
- **Truncate** — cap long field values to a maximum length (`truncator`)
- **Rate-limit** — cap throughput per time bucket (`ratelimiter`)
- **Annotate** — attach computed metadata under a namespace (`annotator`)
- **Checkpoint** — persist and resume stream offsets (`checkpoint`)
- **Watch** — tail a live log file and stream new entries (`watchdog`)
- **Limit** — cap entries per field value or overall (`limiter`)
- **Correlate** — group entries by a shared correlation ID (`correlator`)
- **Mask** — partially obscure sensitive string values (`masker`)
- **Tag** — label entries with user-defined tags based on field predicates (`tagger`)

## Installation

```bash
pip install -e .
```

## Quick start

```bash
# Filter by time range and level, output compact lines
logslice --start 2024-01-01T00:00:00 --end 2024-01-02T00:00:00 \
         --match level=error app.log

# Tag entries and filter to a specific tag
python - <<'EOF'
from logslice import iter_log_entries, tag_entries, filter_by_tag, build_rule

rules = [
    build_rule("error", "level", "error"),
    build_rule("slow", "duration_ms", 5000),
]

with open("app.log") as fh:
    entries = iter_log_entries(fh)
    tagged  = tag_entries(entries, rules)
    errors  = filter_by_tag(tagged, "error")
    for entry in errors:
        print(entry)
EOF
```

## CLI

```
usage: logslice [-h] [--start DATETIME] [--end DATETIME]
                [--match FIELD=PATTERN] [--format {json,pretty,compact}]
                [--output FILE]
                [FILE ...]
```

## Development

```bash
pip install -e ".[dev]"
pytest
```
