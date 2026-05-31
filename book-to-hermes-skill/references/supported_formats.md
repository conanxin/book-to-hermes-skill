# Supported Formats

## Current Status (Phase 0-k: Frozen)

### Enabled Formats

| Format | Extensions | Dependencies | Notes |
|--------|-----------|--------------|-------|
| Markdown | .md, .markdown | None | Native support |
| TXT | .txt, .text | None | Native support |
| text PDF | .pdf | pdftotext → PyPDF2 → pdfminer.six fallback | Local files only |
| HTML | .html, .htm | beautifulsoup4 + lxml / html.parser fallback | Local files only, no script execution, no network |
| DOCX | .docx | python-docx in isolated venv | Local files only, no macros, no embedded objects |
| EPUB | .epub | ebooklib + beautifulsoup4 + lxml in isolated venv | Local files only, no script execution, no network |

### Unsupported Formats (Deferred)

| Format | Extensions | Dependencies | Status |
|--------|-----------|--------------|--------|
| RTF | .rtf | striprtf | Not enabled |
| MOBI / AZW / AZW3 | .mobi, .azw, .azw3 | Calibre ebook-convert | Deferred |
| OCR PDF | .pdf (scanned) | PaddleOCR / Tesseract | Not supported |
| DRM EPUB | .epub | DRM removal tools | Not supported |

## Dependency Locations

- **Base dependencies**: System Python (bs4, lxml, PyPDF2, pdfminer.six)
- **DOCX / EPUB venv**: `~/.hermes/venvs/book-to-hermes-skill/`
  - python-docx
  - ebooklib
  - beautifulsoup4
  - soupsieve

## Safety Rules

- NO automatic package installation
- NO network requests
- NO arbitrary shell execution
- NO script execution in HTML/EPUB
- NO macro execution in DOCX
- NO DRM handling
- NO OCR processing
- Missing dependencies → clear error, exit 1
