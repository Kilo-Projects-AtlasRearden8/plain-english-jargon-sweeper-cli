"""Readability scoring for plain-English checks.

Pure standard library. No network, no keys, no cloud. All scoring is
done locally with the Flesch Reading Ease and Flesch-Kincaid Grade Level
formulas plus a heuristic English syllable counter.
"""

from __future__ import annotations

import re

_WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")
_SENTENCE_SPLIT_RE = re.compile(r"[.!?]+[\s)\]\"]*|[.!?]+$")

DEFAULT_MAX_SENTENCE_WORDS = 25
DEFAULT_MAX_GRADE = 8


def count_syllables(word: str) -> int:
    """Estimate the syllable count of a single English word."""
    word = word.lower().strip("'-")
    if not word:
        return 0
    if len(word) <= 3:
        return 1
    word = re.sub(r"e$", "", word)
    groups = re.findall(r"[aeiouy]+", word)
    return max(1, len(groups))


def split_sentences(text: str) -> list[str]:
    """Split text into sentences, dropping empty fragments."""
    text = text.strip()
    if not text:
        return []
    parts = _SENTENCE_SPLIT_RE.split(text)
    return [part.strip() for part in parts if part.strip()]


def count_words(text: str) -> int:
    """Count words in a text string."""
    return len(_WORD_RE.findall(text))


def readability_scores(text: str) -> dict:
    """Return readability metrics for a text string."""
    words = _WORD_RE.findall(text)
    num_words = len(words)
    sentences = split_sentences(text)
    num_sentences = len(sentences) or 1
    syllables = sum(count_syllables(word) for word in words)

    words_per_sentence = num_words / num_sentences
    syllables_per_word = syllables / num_words if num_words else 0.0

    flesch_ease = 206.835 - 1.015 * words_per_sentence - 84.6 * syllables_per_word
    fk_grade = 0.39 * words_per_sentence + 11.8 * syllables_per_word - 15.59

    return {
        "words": num_words,
        "sentences": num_sentences,
        "syllables": syllables,
        "avg_words_per_sentence": round(words_per_sentence, 2),
        "flesch_reading_ease": round(max(0.0, min(100.0, flesch_ease)), 1),
        "flesch_kincaid_grade": round(max(0.0, fk_grade), 1),
    }


def grade_label(grade: float) -> str:
    """Return a plain-English label for a Flesch-Kincaid grade level."""
    if grade <= 6:
        return "easy (elementary)"
    if grade <= 8:
        return "plain English (middle school)"
    if grade <= 10:
        return "fairly easy"
    if grade <= 12:
        return "fairly difficult (high school)"
    return "difficult (college+)"
