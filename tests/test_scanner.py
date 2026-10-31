"""Tests for the scanner (Markdown stripping, long sentences, readability)."""

import unittest

from jargon_sweeper.scanner import scan_text, strip_markdown


class TestStripMarkdown(unittest.TestCase):
    def test_headings(self):
        self.assertEqual(strip_markdown("# Title"), "Title")
        self.assertEqual(strip_markdown("### Deep"), "Deep")

    def test_code_fence_removed(self):
        text = "Intro\n```\ncode here\n```\nOutro"
        result = strip_markdown(text)
        self.assertNotIn("```", result)
        self.assertNotIn("code here", result)

    def test_links_become_text(self):
        self.assertEqual(strip_markdown("[Click here](https://example.com)"), "Click here")

    def test_bold_and_italic(self):
        self.assertEqual(strip_markdown("**bold** and *italic*"), "bold and italic")

    def test_images_removed(self):
        self.assertEqual(strip_markdown("![alt](img.png)"), "")

    def test_inline_code_removed(self):
        self.assertEqual(strip_markdown("Use `foo()` now"), "Use now")


class TestScanText(unittest.TestCase):
    def test_clean_text_no_issues(self):
        text = "The cat sat. The dog ran."
        result = scan_text(text)
        self.assertEqual(result.issues, [])
        self.assertIn("flesch_kincaid_grade", result.readability)

    def test_jargon_flagged(self):
        result = scan_text("Please utilize this method.")
        self.assertTrue(any(i.kind == "jargon" for i in result.issues))

    def test_long_sentence_flagged(self):
        text = ("The quick brown fox jumps over the lazy dog while the sun sets "
                "and the stars come out slowly in the evening sky above us all.")
        result = scan_text(text, max_sentence_words=10)
        self.assertTrue(any(i.kind == "long-sentence" for i in result.issues))

    def test_readability_flagged_for_hard_text(self):
        hard = (
            "The comprehensive implementation of the methodology facilitates "
            "the subsequent optimization of the comprehensive system architecture."
        )
        result = scan_text(hard, max_grade=8)
        self.assertTrue(any(i.kind == "readability" for i in result.issues))

    def test_path_returned(self):
        result = scan_text("Hello world.", path="README.md")
        self.assertEqual(result.path, "README.md")


if __name__ == "__main__":
    unittest.main()
