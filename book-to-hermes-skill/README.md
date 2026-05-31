# Book-to-Hermes Skill

Convert local books and long-form documents into Hermes skills with progressive disclosure.

## What This Does

Transforms written knowledge into actionable Hermes skills by extracting structure — not producing summaries. The output is a book skill that loads on demand: only the map and requested chapter enter context, never the full text.

## Good For

- Technical books
- Long articles
- Academic papers
- Project reports
- API documentation
- Personal knowledge base documents

## Supported Formats

| Format | Extensions | Status |
|--------|-----------|--------|
| Markdown | .md, .markdown | Enabled |
| TXT | .txt, .text | Enabled |
| text PDF | .pdf | Enabled |
| HTML | .html, .htm | Enabled |
| DOCX | .docx | Enabled |
| EPUB | .epub | Enabled |
| RTF | .rtf | Not supported |
| MOBI / AZW / AZW3 | .mobi, .azw, .azw3 | Not supported |
| OCR PDF | .pdf (scanned) | Not supported |
| DRM EPUB | .epub | Not supported |

## Dependencies

**Base dependencies** (system Python):
- beautifulsoup4 + lxml
- PyPDF2 / pdfminer.six

**Isolated venv** (`~/.hermes/venvs/book-to-hermes-skill/`):
- python-docx (for DOCX)
- ebooklib + beautifulsoup4 (for EPUB)

## Quick Start

```bash
# Convert a Markdown book
python3 ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/build_book_skill.py \
  --source ~/books/my-book.md \
  --slug my-book \
  --title "My Book" \
  --language en \
  --mode technical \
  --output-dir ~/.hermes/skills/books \
  --allow-overwrite yes

# Validate the result
python3 ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/validate_book_skill.py \
  --skill-dir ~/.hermes/skills/books/my-book
```

See `QUICKSTART.md` for format-specific examples.

## Output Structure

```
~/.hermes/skills/books/<slug>/
├── SKILL.md              # Core map and chapter index
├── metadata.json         # Machine-readable metadata
├── source_manifest.md    # Source file provenance
├── chapters/             # Per-chapter summaries
│   ├── ch01-<slug>.md
│   ├── ch02-<slug>.md
│   └── ...
├── glossary.md           # Key terms
├── patterns.md           # Techniques and patterns
└── cheatsheet.md         # Quick reference
```

## Progressive Disclosure

- **SKILL.md** is always loaded first (~400-4,000 tokens)
- **Individual chapters** load only when referenced (~800-1,200 tokens each)
- **Glossary / patterns / cheatsheet** load on explicit request
- **Full source text** never loads into context

## Safety Boundaries

- No automatic package installation
- No network requests
- No arbitrary shell execution
- No script execution in HTML/EPUB
- No macro execution in DOCX
- No DRM handling
- No OCR processing
- No overwrite without `--allow-overwrite yes`

## Known Limits

- Extractive summaries only (no LLM enrichment)
- No image processing or OCR
- No DRM-protected documents
- Chinese text in EPUB smoke tests may show as Unicode escapes (creation script issue, not extractor)
- Nested Markdown list indentation not yet implemented for EPUB

## Next Steps

See `QUICKSTART.md` for examples, `SECURITY.md` for safety details, `MAINTENANCE.md` for development guide.
