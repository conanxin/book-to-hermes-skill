# Release Notes

## v0.1.0-local (2026-05-31)

### Initial Release

**Book-to-Hermes Skill** — Convert local books and long-form documents into Hermes skills with progressive disclosure.

### Supported Formats

- Markdown (.md, .markdown)
- TXT (.txt, .text)
- text PDF (.pdf)
- HTML (.html, .htm)
- DOCX (.docx)
- EPUB (.epub)

### Features

- Extractive summaries (no LLM enrichment)
- Progressive disclosure: SKILL.md as map, chapters on demand
- Glossary, patterns, and cheatsheet generation
- Chinese and English support
- Quality gates: glossary filtering, topic index cleaning, table normalization
- Layered validation: errors, warnings, content notices
- Isolated venv for optional dependencies

### Quality Improvements

- Phase 0-f: Glossary/topic refinement with stricter Chinese fragment detection
- Phase 0-e: Table normalization, evidence-driven patterns, validation hardening
- Phase 0-j: EPUB extractor refactored to avoid nested-content double-processing

### Security

- No automatic dependency installation
- No network requests
- No LLM calls
- No script execution in HTML/EPUB
- No macro execution in DOCX
- Secret scanning in generated files

### Known Limitations

- No RTF support
- No MOBI / AZW / AZW3 support
- No OCR for scanned PDFs
- No DRM handling
- No LLM enrichment
- EPUB nested list indentation not implemented
- Blockquote paragraph breaks not preserved

### Dependencies

**Base:** beautifulsoup4, lxml, PyPDF2, pdfminer.six
**Venv:** python-docx, ebooklib, beautifulsoup4

### Test Coverage

7/7 test cases PASS across Markdown, HTML, DOCX, EPUB formats.
