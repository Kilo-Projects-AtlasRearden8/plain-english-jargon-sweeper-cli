"""Tests for readability scoring logic."""

import unittest

from jargon_sweeper.readability import (
    count_syllables,
    grade_label,
    readability_scores,
    split_sentences,
)


class TestCountSyllables(unittest.TestCase):
    def test_short_words(self):
        self.assertEqual(count_syllables("the"), 1)
        self.assertEqual(count_syllables("a"), 1)
        self.assertEqual(count_syllables("I"), 1)

    def test_multi_syllable(self):
        self.assertGreaterEqual(count_syllables("syllable"), 2)
        self.assertGreaterEqual(count_syllables("readability"), 3)
        self.assertGreaterEqual(count_syllables("comprehensive"), 3)

    def test_empty(self):
        self.assertEqual(count_syllables(""), 0)
        self.assertEqual(count_syllables("'"), 0)


class TestSplitSentences(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(split_sentences("Hello world. How are you?"), ["Hello world", "How are you"])

    def test_empty(self):
        self.assertEqual(split_sentences(""), [])
        self.assertEqual(split_sentences("   "), [])


class TestReadabilityScores(unittest.TestCase):
    def test_keys(self):
        text = "The cat sat on the mat. The dog ran fast."
        scores = readability_scores(text)
        self.assertIn("words", scores)
        self.assertIn("sentences", scores)
        self.assertIn("syllables", scores)
        self.assertIn("avg_words_per_sentence", scores)
        self.assertIn("flesch_reading_ease", scores)
        self.assertIn("flesch_kincaid_grade", scores)

    def test_simple_text_low_grade(self):
        text = "The cat sat on the mat. The dog ran."
        scores = readability_scores(text)
        self.assertLessEqual(scores["flesch_kincaid_grade"], 5)

    def test_empty_text(self):
        scores = readability_scores("")
        self.assertEqual(scores["words"], 0)
        self.assertEqual(scores["sentences"], 1)  # fallback to avoid div/0
        self.assertEqual(scores["flesch_kincaid_grade"], 0.0)


class TestGradeLabel(unittest.TestCase):
    def test_boundaries(self):
        self.assertEqual(grade_label(6), "easy (elementary)")
        self.assertEqual(grade_label(8), "plain English (middle school)")
        self.assertEqual(grade_label(10), "fairly easy")
        self.assertEqual(grade_label(12), "fairly difficult (high school)")
        self.assertEqual(grade_label(16), "difficult (college+)")


if __name__ == "__main__":
    unittest.main()
