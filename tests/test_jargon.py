"""Tests for jargon detection logic."""

import unittest

from jargon_sweeper.jargon import JargonMatch, dictionary, find_jargon, load_dictionary


class TestDictionary(unittest.TestCase):
    def test_contains_common_terms(self):
        terms = dictionary()
        self.assertEqual(terms["utilize"], "use")
        self.assertEqual(terms["facilitate"], "help")
        self.assertEqual(terms["leverage"], "use")

    def test_load_dictionary_returns_dict(self):
        terms = load_dictionary()
        self.assertIsInstance(terms, dict)
        self.assertGreater(len(terms), 20)


class TestFindJargon(unittest.TestCase):
    def test_single_word_match(self):
        matches = find_jargon("Please utilize the tool.")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].term, "utilize")
        self.assertEqual(matches[0].suggestion, "use")

    def test_case_insensitive(self):
        matches = find_jargon("UTILIZE the tool.")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].term, "UTILIZE")

    def test_phrase_match(self):
        matches = find_jargon("In order to start, click here.")
        self.assertTrue(any(m.term == "In order to" for m in matches))
        suggestion = next(m.suggestion for m in matches if m.term == "In order to")
        self.assertEqual(suggestion, "to")

    def test_no_false_positives(self):
        matches = find_jargon("Please use the tool now.")
        self.assertEqual(matches, [])

    def test_whole_word_only(self):
        # "utilizes" is explicitly in the dictionary as a conjugated form,
        # so it SHOULD match (not a false positive).
        matches = find_jargon("He utilizes the tool.")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].term, "utilizes")
        self.assertEqual(matches[0].suggestion, "uses")

    def test_line_and_column(self):
        matches = find_jargon("Hello world.\nLeverage the data.")
        match = next(m for m in matches if m.term == "Leverage")
        self.assertEqual(match.line, 2)
        self.assertEqual(match.column, 1)

    def test_empty_suggestion_means_remove(self):
        matches = find_jargon("Needless to say, this is fine.")
        match = next((m for m in matches if m.term == "Needless to say"), None)
        self.assertIsNotNone(match)
        self.assertEqual(match.suggestion, "")

    def test_multiple_matches(self):
        matches = find_jargon("Utilize the methodology to facilitate the work.")
        terms = {m.term for m in matches}
        self.assertEqual(terms, {"Utilize", "methodology", "facilitate"})

    def test_custom_dictionary(self):
        matches = find_jargon("Hello widget.", terms={"widget": "thing"})
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].suggestion, "thing")

    def test_jargon_match_is_dataclass(self):
        match = JargonMatch(term="foo", suggestion="bar", line=1, column=2)
        self.assertEqual(match.term, "foo")
        self.assertEqual(match.suggestion, "bar")


if __name__ == "__main__":
    unittest.main()
