"""Scan Markdown and plain text for plain-English issues."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .jargon import JargonMatch, find_jargon
from .readability import (
    DEFAULT_MAX_GRADE,
    DEFAULT_MAX_SENTENCE_WORDS,
    count_words,
    grade_label,
    readability_scores,
    split_sentences,
)

_MARKDOWN_RULES = (
    (re.compile(r"```[\s\S]*?```"), " "),          # fenced code blocks
    (re.compile(r"`[^`]*`"), " "),                 # inline code
    (re.compile(r"!\[[^\]]*\]\([^)]*\)"), " "),    # images
    (re.compile(r"\[([^\]]*)\]\([^)]*\)"), r"\1"), # links -> link text
    (re.compile(r"#{1,6}\s+"), ""),                # ATX headings
    (re.compile(r"^\s*[-*_]{3,}\s*$", re.M), ""),  # thematic breaks
    (re.compile(r"\*\*|__"), ""),                  # bold
    (re.compile(r"[*_~`]"), ""),                   # italic / strikethrough remnants
    (re.compile(r"^\s*[\*\-\+]\s+", re.M), ""),    # unordered list markers
    (re.compile(r"^\s*\d+\.\s+", re.M), ""),       # ordered list markers
    (re.compile(r">\s?"), ""),                     # blockquotes
    (re.compile(r"\[[^\]]*\]"), ""),               # leftover reference links
    (re.compile(r"\([^)]*https?://[^)]*\)"), ""),  # leftover URLs
    (re.compile(r"<[^>]+>"), ""),                  # HTML tags
    (re.compile(r"\s+"), " "),
)


def strip_markdown(text: str) -> str:
    """Return the prose content of a Markdown string, formatting removed."""
    result = text
    for pattern, replacement in _MARKDOWN_RULES:
        result = pattern.sub(replacement, result)
    return result.strip()


@dataclass(frozen=True)
class Issue:
    kind: str          # "jargon" | "long-sentence" | "readability"
    line: int          # 1-based line number
    column: int | None
    message: str
    suggestion: str | None
    severity: str      # "error" | "warn" | "info"


@dataclass(frozen=True)
class ScanResult:
    path: str
    issues: list[Issue]
    readability: dict


def scan_text(
    text: str,
    path: str = "<stdin>",
    max_sentence_words: int = DEFAULT_MAX_SENTENCE_WORDS,
    max_grade: int = DEFAULT_MAX_GRADE,
) -> ScanResult:
    """Scan text and return a ScanResult with all detected issues."""
    issues: list[Issue] = []

    # Jargon matches (checked on the raw text so line numbers stay exact).
    for match in find_jargon(text):
        if match.suggestion:
            message = f"Use '{match.suggestion}' instead of '{match.term}'"
        else:
            message = f"Remove '{match.term}'"
        issues.append(
            Issue(
                kind="jargon",
                line=match.line,
                column=match.column,
                message=message,
                suggestion=match.suggestion or None,
                severity="warn",
            )
        )

    # Long sentences, checked line by line so reporting stays exact.
    for line_no, line in enumerate(text.splitlines(), start=1):
        clean_line = strip_markdown(line)
        for sentence in split_sentences(clean_line):
            word_count = count_words(sentence)
            if word_count > max_sentence_words:
                severity = "error" if word_count > max_sentence_words * 1.5 else "warn"
                issues.append(
                    Issue(
                        kind="long-sentence",
                        line=line_no,
                        column=None,
                        message=(
                            f"Long sentence ({word_count} words). "
                            "Consider splitting it into shorter sentences."
                        ),
                        suggestion=None,
                        severity=severity,
                    )
                )

    # Overall readability grade for the document.
    clean = strip_markdown(text)
    scores = readability_scores(clean)
    grade = scores["flesch_kincaid_grade"]
    if grade > max_grade:
        issues.append(
            Issue(
                kind="readability",
                line=1,
                column=None,
                message=(
                    f"Reading level is about grade {grade} "
                    f"({grade_label(grade)}). Aim for grade {max_grade} or lower."
                ),
                suggestion=None,
                severity="info",
            )
        )

    return ScanResult(path=path, issues=issues, readability=scores)


def scan_file(path: str, **kwargs) -> ScanResult:
    """Read a file from disk and scan its contents."""
    text = Path(path).read_text(encoding="utf-8")
    return scan_text(text, path=path, **kwargs)
