"""Terminal colour highlighting for log entries."""

from __future__ import annotations

import re
from typing import Dict, Iterable, Iterator, Optional

# ANSI escape codes
_RESET = "\033[0m"
_COLOURS: Dict[str, str] = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "bold": "\033[1m",
}

_LEVEL_COLOURS: Dict[str, str] = {
    "debug": _COLOURS["cyan"],
    "info": _COLOURS["green"],
    "warning": _COLOURS["yellow"],
    "warn": _COLOURS["yellow"],
    "error": _COLOURS["red"],
    "critical": _COLOURS["magenta"],
    "fatal": _COLOURS["magenta"],
}


def _colour(text: str, colour: str) -> str:
    """Wrap *text* with the given ANSI colour code."""
    code = _COLOURS.get(colour.lower(), "")
    if not code:
        return text
    return f"{code}{text}{_RESET}"


def highlight_level(entry: Dict) -> str:
    """Return the entry's level value wrapped in an appropriate colour.

    Falls back to plain text when the level field is absent or unknown.
    """
    level = str(entry.get("level", "")).lower()
    raw = entry.get("level", "")
    colour_code = _LEVEL_COLOURS.get(level, "")
    if colour_code:
        return f"{colour_code}{raw}{_RESET}"
    return str(raw)


def highlight_pattern(text: str, pattern: str, colour: str = "yellow") -> str:
    """Highlight every occurrence of *pattern* (regex) in *text*."""
    code = _COLOURS.get(colour.lower(), _COLOURS["yellow"])

    def _replace(m: re.Match) -> str:  # type: ignore[type-arg]
        return f"{code}{m.group(0)}{_RESET}"

    return re.sub(pattern, _replace, text)


def highlight_entry(
    entry: Dict,
    patterns: Optional[Iterable[str]] = None,
    colour: str = "yellow",
) -> Dict:
    """Return a *copy* of *entry* with string values highlighted.

    The ``level`` field is coloured by severity; additional regex *patterns*
    are highlighted across every string value.
    """
    result: Dict = {}
    compiled = [re.compile(p) for p in (patterns or [])]

    for key, value in entry.items():
        if key == "level":
            result[key] = highlight_level(entry)
        elif isinstance(value, str) and compiled:
            highlighted = value
            for pat in compiled:
                highlighted = highlight_pattern(highlighted, pat.pattern, colour)
            result[key] = highlighted
        else:
            result[key] = value

    return result


def highlight_entries(
    entries: Iterable[Dict],
    patterns: Optional[Iterable[str]] = None,
    colour: str = "yellow",
) -> Iterator[Dict]:
    """Yield highlighted copies of each entry in *entries*."""
    pattern_list = list(patterns or [])
    for entry in entries:
        yield highlight_entry(entry, pattern_list, colour)
