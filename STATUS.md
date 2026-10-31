# Project Status: Plain-English Jargon Sweeper CLI

## What Was Built

A local-only Python CLI tool (`jargon-sweeper`) that scans Markdown and plain text files for:

1. **Jargon detection** — Identifies ~165 common jargon words and phrases (e.g., "utilize" → "use", "facilitate" → "help", "in order to" → "to", "needless to say" → remove) with plain-English replacement suggestions. Uses a JSON dictionary loaded at runtime, no external dependencies.

2. **Long sentence detection** — Flags sentences exceeding a configurable word limit (default 25 words), with severity "warn" (25–37 words) or "error" (38+ words).

3. **Readability scoring** — Computes Flesch Reading Ease and Flesch-Kincaid Grade Level for the whole document using a pure-Python syllable heuristic. Warns when grade level exceeds a configurable threshold (default grade 8).

All processing is **local-only** — no network access, no API keys, no cloud uploads. Pure standard library.

## Project Structure

```
plain-english-jargon-sweeper-cli/
├── LICENSE                    # MIT License, Copyright (c) 2026 Asdale Dynamics, LLC
├── README.md                  # Usage docs, credits Asdale Dynamics, LLC
├── STATUS.md                  # This file
├── pyproject.toml             # Package config, console script entry point
├── data/
│   └── jargon.json            # 165 jargon terms with plain-English replacements
├── jargon_sweeper/
│   ├── __init__.py            # Version 0.1.0
│   ├── cli.py                 # Argument parsing, output formatting
│   ├── jargon.py              # Jargon dictionary loading & matching
│   ├── readability.py         # Flesch-Kincaid, syllable counting, sentence splitting
│   └── scanner.py             # Markdown stripping, line-by-line scanning, issue collection
└── tests/
    ├── __init__.py
    ├── test_cli.py            # CLI exit codes, output formats
    ├── test_jargon.py         # Jargon matching logic (case, boundaries, phrases)
    ├── test_readability.py    # Scoring formulas, edge cases
    └── test_scanner.py        # Markdown stripping, long sentence, readability flags
```

## How to Run

### Install (editable, for development)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Usage Examples

Scan a file (text output):
```bash
jargon-sweeper my-article.md
```

Scan from stdin:
```bash
cat my-article.md | jargon-sweeper
# or
jargon-sweeper - < my-article.md
```

JSON output (for editors/CI):
```bash
jargon-sweeper my-article.md --format json
```

Custom thresholds:
```bash
jargon-sweeper my-article.md --max-sentence-words 20 --max-grade 6
```

Exit codes:
- `0` — No issues found
- `1` — Issues found (jargon, long sentences, or high readability grade)

## Verification Results

### Test Suite
All 37 unit tests pass:
- `test_readability.py` — 9 tests (syllable counting, sentence splitting, Flesch formulas, grade labels)
- `test_jargon.py` — 11 tests (matching, case insensitivity, word boundaries, phrases, conjugated forms)
- `test_scanner.py` — 10 tests (Markdown stripping, long sentences, readability flagging)
- `test_cli.py` — 7 tests (help, clean/jargon text exit codes, JSON output, file argument)

Run with:
```bash
python -m unittest discover -s tests -v
```

### Manual CLI Verification

| Test Case | Command | Result |
|-----------|---------|--------|
| Clean text | `echo "The cat sat." \| jargon-sweeper` | Exit 0, "No plain-English issues found." |
| Jargon detected | `echo "Please utilize this." \| jargon-sweeper` | Exit 1, flags "utilize" → "use" |
| Long sentence | `echo "A very long sentence with many words that exceeds the default threshold of twenty-five words." \| jargon-sweeper --max-sentence-words 10` | Exit 1, flags long-sentence |
| High readability grade | `jargon-sweeper README.md --max-grade 8` | Exit 1, flags readability (grade 10.3) |
| JSON output | `jargon-sweeper README.md --format json` | Valid JSON with path, readability, issues |
| Stdin via pipe | `cat file.md \| jargon-sweeper` | Works, path shows `<stdin>` |
| Stdin via `-` | `jargon-sweeper - < file.md` | Works, path shows `<stdin>` |

### Package Install
```bash
pip install -e .  # Success, installs console script 'jargon-sweeper'
```

## Known Gaps / Future Improvements

1. **Syllable counter heuristic** — The vowel-group method works for most English words but can miscount some edge cases (e.g., "queue" = 1 syllable but counted as 2). Acceptable for a linter-style tool.

2. **Sentence splitting** — Regex-based splitter handles common cases but may split incorrectly on abbreviations (e.g., "e.g.", "Dr.") or split/merge around unusual punctuation.

3. **Jargon dictionary** — Currently ~165 terms, focused on business/academic jargon. Could expand with domain-specific lists (tech, legal, medical, etc.). No stemming/lemmatization — conjugated forms must be added explicitly (e.g., "utilizes", "utilized" are separate entries).

4. **Markdown stripping** — Regex-based, not a full parser. May miss edge cases (nested formatting, HTML entities, complex tables). Code fences and inline code are removed entirely (not analyzed).

5. **No configuration file** — Thresholds only via CLI flags. Could add `pyproject.toml` or `.jargon-sweeper` config.

6. **No ignore/allow list** — No way to suppress specific jargon matches for a project.

7. **Single-threaded** — Scans files sequentially. Could add parallel file processing for large codebases.

8. **No IDE integration** — No Language Server Protocol or editor plugin. JSON output enables basic integration.

9. **Test coverage** — Good unit coverage but no integration/E2E tests for multi-file scanning.

10. **Performance on huge files** — Loads entire file into memory. Could stream for very large inputs.

---

Built for **Asdale Dynamics, LLC** (Indiana, formed October 2026) — beginner-friendly AI education, books, guides, and practical local-first tools.  
Author: Dylan Asdale (RN turned AI author, founder of Asdale Dynamics, LLC).  
Style: clear, warm, polished, tested, local-first, no secrets or personal data.