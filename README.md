# Plain-English Jargon Sweeper

A local-only command-line tool that scans Markdown and plain text for
jargon, long sentences, and readability issues, then suggests
plain-English rewrites.

Built and maintained by **Asdale Dynamics, LLC** — beginner-friendly AI
education, books, guides, and practical tools (Indiana, formed October
2026). No network access, no API keys, no cloud uploads. Everything runs
on your machine.

## What it does

- **Jargon detection** — flags words and phrases like "utilize",
  "facilitate", "leverage", "in order to", "at this point in time", and
  dozens more, with plain-English replacements (for example: "utilize"
  → "use").
- **Long sentences** — flags sentences longer than a configurable word
  limit and suggests splitting them.
- **Readability scoring** — reports Flesch Reading Ease and
  Flesch-Kincaid grade level for the whole document, and warns when the
  reading level is above a target grade.

## Install

```bash
pip install .
```

Or for editable development:

```bash
pip install -e .
```

This provides the `jargon-sweeper` command. No external dependencies —
Python standard library only.

## Usage

Scan a file:

```bash
jargon-sweeper my-article.md
```

Read from stdin:

```bash
cat my-article.md | jargon-sweeper
```

JSON output (useful for editors and CI):

```bash
jargon-sweeper my-article.md --format json
```

Tune the thresholds:

```bash
jargon-sweeper my-article.md --max-sentence-words 20 --max-grade 6
```

Exit status is `0` when no issues are found, `1` when issues are found,
so it can be used like a linter.

## Example

```
$ echo "Please utilize the methodology to facilitate the work." | jargon-sweeper
Jargon sweeper report for <stdin>
Readability: grade 5.2 (ease 84.3, 13 words, 1 sentences)
  [warn] jargon @ line 1:8: Use 'use' instead of 'utilize' -> use
  [warn] jargon @ line 1:24: Use 'method' instead of 'methodology' -> method
  [warn] jargon @ line 1:42: Use 'help' instead of 'facilitate' -> help
```

## Local-first

This tool processes files only on your local machine. Nothing is
uploaded, no keys are required, and no accounts are needed.

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC. See LICENSE.
