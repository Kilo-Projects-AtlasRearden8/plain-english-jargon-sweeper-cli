"""Command-line interface for the plain-English jargon sweeper."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .scanner import scan_text, scan_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jargon-sweeper",
        description=(
            "Scan Markdown and text for jargon, long sentences, and "
            "readability issues, suggesting plain-English rewrites."
        ),
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="File to scan. Reads from stdin when omitted.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--max-sentence-words",
        type=int,
        default=25,
        help="Flag sentences longer than this many words (default: 25).",
    )
    parser.add_argument(
        "--max-grade",
        type=int,
        default=8,
        help="Maximum Flesch-Kincaid grade level allowed (default: 8).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.file and args.file != "-":
        result = scan_file(
            args.file,
            max_sentence_words=args.max_sentence_words,
            max_grade=args.max_grade,
        )
    else:
        text = sys.stdin.read()
        result = scan_text(
            text,
            path="<stdin>",
            max_sentence_words=args.max_sentence_words,
            max_grade=args.max_grade,
        )

    if args.format == "json":
        payload = {
            "path": result.path,
            "readability": result.readability,
            "issues": [
                {
                    "kind": issue.kind,
                    "line": issue.line,
                    "column": issue.column,
                    "message": issue.message,
                    "suggestion": issue.suggestion,
                    "severity": issue.severity,
                }
                for issue in result.issues
            ],
        }
        print(json.dumps(payload, indent=2))
    else:
        scores = result.readability
        print(f"Jargon sweeper report for {result.path}")
        print(
            "Readability: grade "
            f"{scores['flesch_kincaid_grade']} "
            f"(ease {scores['flesch_reading_ease']}, "
            f"{scores['words']} words, {scores['sentences']} sentences)"
        )
        if not result.issues:
            print("No plain-English issues found.")
            return 0
        for issue in sorted(result.issues, key=lambda item: (item.line, item.column or 0)):
            location = f"line {issue.line}"
            if issue.column:
                location += f":{issue.column}"
            hint = f" -> {issue.suggestion}" if issue.suggestion else ""
            print(f"  [{issue.severity}] {issue.kind} @ {location}: {issue.message}{hint}")

    return 1 if result.issues else 0


if __name__ == "__main__":
    sys.exit(main())
