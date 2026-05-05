# logslice

A lightweight log parser that extracts and filters structured JSON logs by time range and field patterns.

---

## Installation

```bash
pip install logslice
```

Or install from source:

```bash
git clone https://github.com/youruser/logslice.git
cd logslice && pip install -e .
```

---

## Usage

```python
from logslice import LogSlicer

slicer = LogSlicer("app.log")

results = slicer.query(
    start="2024-01-15T08:00:00",
    end="2024-01-15T09:00:00",
    filters={"level": "ERROR", "service": "auth"}
)

for entry in results:
    print(entry)
```

You can also use the CLI:

```bash
logslice --file app.log --start "2024-01-15T08:00:00" --end "2024-01-15T09:00:00" --filter level=ERROR
```

---

## Features

- Parse newline-delimited JSON log files
- Filter by time range using any ISO 8601 timestamp field
- Match entries by exact field values or regex patterns
- Lightweight with no external dependencies

---

## License

MIT © 2024 youruser