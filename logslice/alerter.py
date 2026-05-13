"""Alert on log entries that match threshold conditions."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable, Dict, Generator, Iterable, List, Optional


AlertHandler = Callable[[str, dict], None]


def _default_handler(rule_name: str, entry: dict) -> None:
    """Print a simple alert message to stdout."""
    ts = entry.get("timestamp", "?")
    msg = entry.get("message", "")
    print(f"[ALERT] rule={rule_name!r} ts={ts} message={msg!r}")


def check_entry(
    entry: dict,
    rules: List[Dict[str, Any]],
    handler: Optional[AlertHandler] = None,
) -> List[str]:
    """Evaluate *rules* against *entry* and fire *handler* for each match.

    Returns the list of rule names that fired.
    """
    if handler is None:
        handler = _default_handler

    fired: List[str] = []
    for rule in rules:
        name: str = rule["name"]
        predicate: Callable[[dict], bool] = rule["predicate"]
        try:
            if predicate(entry):
                handler(name, entry)
                fired.append(name)
        except Exception:
            pass
    return fired


def alert_entries(
    entries: Iterable[dict],
    rules: List[Dict[str, Any]],
    handler: Optional[AlertHandler] = None,
    *,
    passthrough: bool = True,
) -> Generator[dict, None, None]:
    """Yield entries from *entries*, firing alerts as they are evaluated.

    If *passthrough* is False only entries that triggered at least one alert
    are yielded.
    """
    for entry in entries:
        fired = check_entry(entry, rules, handler)
        if passthrough or fired:
            yield entry


def build_rule(
    name: str,
    field: str,
    value: Any,
    *,
    op: str = "eq",
) -> Dict[str, Any]:
    """Build a simple comparison rule dict.

    Supported *op* values: ``eq``, ``neq``, ``contains``, ``gt``, ``lt``.
    """
    ops: Dict[str, Callable[[Any, Any], bool]] = {
        "eq": lambda a, b: a == b,
        "neq": lambda a, b: a != b,
        "contains": lambda a, b: b in str(a),
        "gt": lambda a, b: a > b,
        "lt": lambda a, b: a < b,
    }
    if op not in ops:
        raise ValueError(f"Unknown op {op!r}. Choose from {list(ops)}.")
    compare = ops[op]

    def predicate(entry: dict) -> bool:
        return field in entry and compare(entry[field], value)

    return {"name": name, "predicate": predicate}


def count_alerts(
    entries: Iterable[dict],
    rules: List[Dict[str, Any]],
) -> Dict[str, int]:
    """Return a dict mapping rule name -> number of times it fired."""
    counts: Dict[str, int] = defaultdict(int)
    for entry in entries:
        for name in check_entry(entry, rules, handler=lambda *_: None):
            counts[name] += 1
    return dict(counts)
