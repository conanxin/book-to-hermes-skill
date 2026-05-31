# book-to-hermes-skill — Local GitHub-Ready Export

This is a **local export** of the book-to-hermes-skill tool, ready for GitHub upload or private backup.

## Original Tool Path

`~/.hermes/skills/knowledge/book-to-hermes-skill/`

## Export Info

- **Exported at**: 2026-05-31
- **Version**: v0.1.0-local
- **Phase**: 1-c (GitHub-ready export)

## What This Tool Does

Converts documents (books, papers, articles) into Hermes-native skills — structured, on-demand knowledge bases with progressive disclosure.

## Supported Formats

- Markdown (.md)
- Plain text (.txt)
- Text PDF (.pdf)
- HTML (.html, .htm)
- DOCX (.docx)
- EPUB (.epub)

## Not Supported

- OCR PDF
- DRM EPUB
- RTF
- MOBI / AZW / AZW3

## Safety Boundaries

- No LLM API calls during generation
- No network requests during extraction or generation
- HTML/EPUB: scripts and styles removed before processing
- DOCX: macros and embedded objects not executed
- Extractive summaries only — no synthetic content

## How to Install on Another Hermes Instance

1. Copy `book-to-hermes-skill/` to `~/.hermes/skills/knowledge/`
2. Create venv:
   ```bash
   python -m venv ~/.hermes/venvs/book-to-hermes-skill
   source ~/.hermes/venvs/book-to-hermes-skill/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install beautifulsoup4 lxml
   pip install python-docx
   pip install ebooklib
   ```
4. Run regression tests:
   ```bash
   python scripts/extract_text.py sample.md --mode article
   python scripts/build_book_skill.py --source sample.md --slug test --title Test --language en --mode article --output-dir ./test_output
   python scripts/validate_book_skill.py --skill-dir ./test_output/test
   ```

## What's Included

- `SKILL.md` — Hermes skill manifest
- `README.md` — Tool documentation
- `QUICKSTART.md` — Quick start guide
- `EXAMPLES.md` — Usage examples
- `SECURITY.md` — Security policy
- `MAINTENANCE.md` — Maintenance guide
- `TEST_MATRIX.md` — Test coverage
- `RELEASE_NOTES.md` — Release history
- `PHASE_INDEX.md` — Phase development index
- `scripts/` — Core scripts (extract, build, validate)
- `templates/` — Skill generation templates
- `references/` — Design docs and references
- `examples/` — Sample commands

## What's NOT Included

- Source documents (PDFs, EPUBs, etc.)
- Generated personal book skills
- Secrets, tokens, API keys
- Logs, backups, caches
- Hermes config files

## Publishing Notes

- Do NOT commit source documents unless you have rights to publish them
- Do NOT commit generated personal book skills unless intended for public sharing
- Choose a license before public release (see LICENSE_PENDING.md)
- Consider keeping the repo private if it contains personal knowledge bases

## License

See LICENSE_PENDING.md — no license selected yet.
