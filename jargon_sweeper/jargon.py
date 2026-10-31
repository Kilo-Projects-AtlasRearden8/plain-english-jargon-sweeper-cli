"""Jargon detection with plain-English replacement suggestions."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "jargon.json"

_FALLBACK = {
    "utilize": "use",
    "facilitate": "help",
    "leverage": "use",
    "methodology": "method",
    "implement": "do",
    "commence": "start",
    "terminate": "end",
    "subsequently": "later",
    "prior to": "before",
    "in order to": "to",
    "demonstrate": "show",
    "comprehensive": "complete",
    "substantial": "large",
    "numerous": "many",
    "sufficient": "enough",
    "currently": "now",
    "previously": "before",
}


@dataclass(frozen=True)
class JargonMatch:
    term: str
    suggestion: str
    line: int
    column: int


def load_dictionary(path: Optional[Path] = None) -> dict[str, str]:
    """Load the jargon dictionary from JSON, falling back to a built-in set."""
    source = path or _DATA_PATH
    try:
        with source.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return {str(key).lower(): str(value) for key, value in data.items()}
    except (OSError, ValueError):
        return dict(_FALLBACK)


_DICTIONARY: Optional[dict[str, str]] = None


def dictionary() -> dict[str, str]:
    """Return the cached jargon dictionary (term -> plain-English replacement)."""
    global _DICTIONARY
    if _DICTIONARY is None:
        _DICTIONARY = load_dictionary()
    return _DICTIONARY


def find_jargon(text: str, terms: Optional[dict[str, str]] = None) -> list[JargonMatch]:
    """Find jargon terms in text, case-insensitive, whole-word/phrase only."""
    lookup = terms or dictionary()
    # Group terms by first character for faster lookup
    by_first_char: dict[str, list[str]] = {}
    for term in lookup:
        if term:
            first = term[0]
            by_first_char.setdefault(first, []).append(term)
    # Sort each group by length descending (longest first)
    for group in by_first_char.values():
        group.sort(key=len, reverse=True)

    matches: list[JargonMatch] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        lower_line = line.lower()
        cursor = 0
        line_len = len(lower_line)
        while cursor < line_len:
            first_char = lower_line[cursor]
            matched = False
            # Only check terms that start with this character
            for term in by_first_char.get(first_char, ()):
                term_len = len(term)
                if cursor + term_len > line_len:
                    continue
                if lower_line[cursor:cursor + term_len] != term:
                    continue
                # Word boundary check
                start = cursor
                end = cursor + term_len
                before_ok = start == 0 or not line[start - 1].isalnum()
                after_ok = end == len(line) or not line[end].isalnum()
                if before_ok and after_ok:
                    matches.append(
                        JargonMatch(
                            term=line[start:end],
                            suggestion=lookup[term],
                            line=line_no,
                            column=start + 1,
                        )
                    )
                    cursor = end
                    matched = True
                    break
            if not matched:
                cursor += 1
    return matches