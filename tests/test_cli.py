"""Tests for the CLI entry point."""

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

from jargon_sweeper.cli import main


class TestCli(unittest.TestCase):
    def _run(self, args, text=None):
        old_stdin, old_stdout = sys.stdin, sys.stdout
        try:
            if text is not None:
                sys.stdin = io.StringIO(text)
            out = io.StringIO()
            sys.stdout = out
            try:
                code = main(args)
            except SystemExit as exc:
                code = exc.code if isinstance(exc.code, int) else 0
            return code, out.getvalue()
        finally:
            sys.stdin, sys.stdout = old_stdin, old_stdout

    def test_help_exits_zero(self):
        code, _ = self._run(["--help"])
        self.assertEqual(code, 0)

    def test_clean_text_exits_zero(self):
        code, output = self._run(["--format", "text"], "The cat sat. The dog ran.")
        self.assertEqual(code, 0)
        self.assertIn("No plain-English issues found.", output)

    def test_jargon_exits_nonzero(self):
        code, output = self._run(["--format", "text"], "Please utilize the tool.")
        self.assertEqual(code, 1)
        self.assertIn("utilize", output)
        self.assertIn("use", output)

    def test_json_output(self):
        code, output = self._run(["--format", "json"], "Please utilize the tool.")
        self.assertEqual(code, 1)
        payload = json.loads(output)
        self.assertEqual(payload["path"], "<stdin>")
        self.assertIn("flesch_kincaid_grade", payload["readability"])
        self.assertTrue(any(i["kind"] == "jargon" for i in payload["issues"]))

    def test_file_argument(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as handle:
            handle.write("Please utilize this methodology.")
            name = handle.name
        try:
            code, output = self._run([name])
            self.assertEqual(code, 1)
            self.assertIn(name, output)
        finally:
            import os

            os.unlink(name)


if __name__ == "__main__":
    unittest.main()
