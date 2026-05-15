"""Classify log entries into named categories based on rule sets."""

from __future__ import annotations

from typing import Any, Callable, Dict, Generator, Iterable, List, Optional

Entry = Dict[str, Any]
Predicate = Callable[[Entry], bool]


def _make_predicate(field: str, pattern: str) -> Predicate:
    """Return a predicate that checks whether *field* contains *pattern*."""
    import re
    rx = re.compile(pattern)

    def _check(entry: Entry) -> bool:
        value = entry.get(field)
        if value is None:
            return False
        return bool(rx.search(str(value)))

    return _check


def build_rule(
    name: str,
    field: str,
    pattern: str,
    priority: int = 0,
) -> Dict[str, Any]:
    """Build a classification rule dict."""
    return {
        "name": name,
        "field": field,
        "pattern": pattern,
        "priority": priority,
        "predicate": _make_predicate(field, pattern),
    }


def classify_entry(
    entry: Entry,
    rules: List[Dict[str, Any]],
    default: str = "unclassified",
    multi: bool = False,
) -> Entry:
    """Return a copy of *entry* with a ``_class`` field set.

    When *multi* is ``True`` every matching rule name is collected into a list;
    otherwise only the highest-priority (lowest ``priority`` value) match is
    used.  Ties are broken by insertion order.
    """
    sorted_rules = sorted(rules, key=lambda r: r["priority"])
    matches = [r["name"] for r in sorted_rules if r["predicate"](entry)]

    if multi:
        classification: Any = matches if matches else [default]
    else:
        classification = matches[0] if matches else default

    return {**entry, "_class": classification}


def classify_entries(
    entries: Iterable[Entry],
    rules: List[Dict[str, Any]],
    default: str = "unclassified",
    multi: bool = False,
) -> Generator[Entry, None, None]:
    """Yield classified copies of every entry in *entries*."""
    for entry in entries:
        yield classify_entry(entry, rules, default=default, multi=multi)


def rules_from_config(config: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Build rule dicts from a plain-config list (no callables required).

    Each item must have ``name``, ``field``, and ``pattern`` keys; ``priority``
    is optional and defaults to ``0``.
    """
    return [
        build_rule(
            name=item["name"],
            field=item["field"],
            pattern=item["pattern"],
            priority=item.get("priority", 0),
        )
        for item in config
    ]
