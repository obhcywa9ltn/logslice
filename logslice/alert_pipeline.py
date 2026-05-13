"""High-level helpers that wire alerter + notifier into a processing pipeline."""

from __future__ import annotations

from typing import Any, Callable, Dict, Generator, Iterable, List, Optional

from logslice.alerter import alert_entries, build_rule, count_alerts
from logslice.notifier import AlertHandler, collecting_notifier, console_notifier


def build_alert_pipeline(
    entries: Iterable[dict],
    rules: List[Dict[str, Any]],
    *,
    handler: Optional[AlertHandler] = None,
    passthrough: bool = True,
) -> Generator[dict, None, None]:
    """Convenience wrapper: apply alert rules and yield entries.

    If *handler* is ``None`` a :func:`~logslice.notifier.console_notifier`
    is used.
    """
    if handler is None:
        handler = console_notifier()
    yield from alert_entries(entries, rules, handler, passthrough=passthrough)


def rules_from_config(config: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Build a list of rule dicts from a plain-dict configuration.

    Each config item must have ``name``, ``field``, ``value`` and optionally
    ``op`` (default ``"eq"``).

    Example::

        rules_from_config([
            {"name": "errors", "field": "level", "value": "ERROR"},
            {"name": "slow",   "field": "duration_ms", "value": 1000, "op": "gt"},
        ])
    """
    rules: List[Dict[str, Any]] = []
    for item in config:
        rules.append(
            build_rule(
                item["name"],
                item["field"],
                item["value"],
                op=item.get("op", "eq"),
            )
        )
    return rules


def run_and_report(
    entries: Iterable[dict],
    rules: List[Dict[str, Any]],
) -> Dict[str, int]:
    """Consume *entries*, fire rules silently and return alert counts.

    No entries are yielded; use this when you only need the summary.
    """
    return count_alerts(entries, rules)


def monitored_pipeline(
    entries: Iterable[dict],
    config: List[Dict[str, Any]],
    *,
    store: Optional[List[dict]] = None,
    passthrough: bool = True,
) -> Generator[dict, None, None]:
    """Build rules from *config*, collect alerts into *store* and yield entries.

    If *store* is ``None`` a new list is created and discarded; pass an
    external list to inspect fired alerts after the pipeline is exhausted.
    """
    if store is None:
        store = []
    rules = rules_from_config(config)
    handler = collecting_notifier(store)
    yield from build_alert_pipeline(entries, rules, handler=handler,
                                    passthrough=passthrough)
