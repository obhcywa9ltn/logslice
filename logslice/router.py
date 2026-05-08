"""Route log entries to multiple output sinks based on configurable rules.

A *sink* is any callable that accepts an iterable of dicts and returns the
number of entries consumed, matching the interface of ``writer.write_entries``.
"""

from __future__ import annotations

from typing import Callable, Dict, Iterable, List, Optional, Tuple

Sink = Callable[[Iterable[dict]], int]
Rule = Tuple[str, Callable[[dict], bool], Sink]


class Router:
    """Route entries to named sinks according to an ordered rule list."""

    def __init__(
        self,
        rules: List[Rule],
        default_sink: Optional[Sink] = None,
        stop_on_first_match: bool = True,
    ) -> None:
        self._rules = rules
        self._default_sink = default_sink
        self._stop_on_first_match = stop_on_first_match

    # ------------------------------------------------------------------
    def route(self, entries: Iterable[dict]) -> Dict[str, int]:
        """Route *entries* and return a dict mapping sink name -> entry count."""
        buffers: Dict[str, List[dict]] = {name: [] for name, _, _ in self._rules}
        default_buf: List[dict] = []

        for entry in entries:
            matched = False
            for name, predicate, _ in self._rules:
                if predicate(entry):
                    buffers[name].append(entry)
                    matched = True
                    if self._stop_on_first_match:
                        break
            if not matched and self._default_sink is not None:
                default_buf.append(entry)

        counts: Dict[str, int] = {}
        for name, _, sink in self._rules:
            counts[name] = sink(iter(buffers[name]))
        if self._default_sink is not None:
            counts["__default__"] = self._default_sink(iter(default_buf))
        return counts


def build_router(
    rules: List[Rule],
    default_sink: Optional[Sink] = None,
    stop_on_first_match: bool = True,
) -> Router:
    """Convenience factory for :class:`Router`."""
    return Router(
        rules=rules,
        default_sink=default_sink,
        stop_on_first_match=stop_on_first_match,
    )
