# Book-to-Hermes Skill

[中文说明](README.zh-CN.md) | English

Convert local books, articles, PDFs, HTML pages, DOCX files, and EPUBs into Hermes skills with progressive disclosure.

## What It Does

This is not a one-shot summarizer. It turns local long-form documents into **book skills** that Hermes can load, query, and reference over time.

Instead of dumping the full text into context, a book skill provides:

- **SKILL.md** — a map with chapter index, topic index, and usage guide
- **chapters/** — individual chapter files loaded on demand
- **glossary.md** — extracted terms with definitions and source references
- **patterns.md** — recurring structures, evidence-driven
- **cheatsheet.md** — quick-reference commands
- **metadata.json** — structured metadata
- **source_manifest.md** — source provenance and limitations

The top-level SKILL.md is always loaded first (~400–4,000 tokens). Individual chapters are loaded only when referenced (~800–1,200 tokens each). This keeps context usage bounded even for 100,000+ word documents.

## Why This Exists

Long articles and ebooks are hard to reuse after reading. Ordinary summaries lose context. A book skill turns your documents into **queryable knowledge modules** that stay available in your Hermes environment.

Use cases:
- Personal reading library
- Project documentation archive
- Research note collection
- Bilingual terminology reference

## Supported Formats

| Format | Extension | Status |
|--------|-----------|--------|
| Markdown | .md, .markdown | Stable |
| Plain text | .txt | Stable |
| Text-based PDF | .pdf | Stable (no OCR) |
| HTML | .html, .htm | Stable |
| DOCX | .docx | Stable |
| EPUB | .epub | Stable |

### Not Supported

- Scanned/image-based PDFs (no OCR)
- RTF
- MOBI / AZW / AZW3
- DRM-protected EPUBs

## Output Structure

```
~/.hermes/skills/books/example-book/
├── SKILL.md              # Skill definition + chapter map (~400-4,000 tokens)
├── chapters/
│   ├── ch01-intro.md     # Individual chapter files (~800-1,200 tokens each)
│   ├── ch02-chapter.md
│   └── ...
├── glossary.md           # Extracted terms with definitions
├── patterns.md           # Recurring structures, evidence-driven
├── cheatsheet.md         # Quick-reference commands
├── metadata.json         # Structured metadata
└── source_manifest.md    # Source provenance and limitations
```

### File Purposes

- **SKILL.md** — Always loaded first. Contains skill identity, chapter index, topic index, usage guide, and safety notes.
- **chapters/** — Loaded on demand. Each file contains extractive summary + key points + original content.
- **glossary.md** — Terms extracted from source with definitions, types, and chapter references.
- **patterns.md** — Recurring structures found in source (not templates — evidence-driven).
- **cheatsheet.md** — Quick commands for common queries.
- **metadata.json** — Machine-readable metadata (title, slug, language, mode, chapter count, etc.).
- **source_manifest.md** — Documents source path, format, limitations, and known issues.

## Installation

Copy the tool directory to your Hermes skills:

```bash
cp -r book-to-hermes-skill/ ~/.hermes/skills/knowledge/book-to-hermes-skill/
```

Optional: create a dedicated venv:

```bash
python3 -m venv ~/.hermes/venvs/book-to-hermes-skill
source ~/.hermes/venvs/book-to-hermes-skill/bin/activate
pip install python-docx ebooklib beautifulsoup4 lxml
```

**Important**: The tool does not automatically install dependencies. You must explicitly install them if you need DOCX or EPUB support.

## Quickstart

### Build a Book Skill

```bash
python ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/build_book_skill.py \
  --source ~/Documents/example.md \
  --slug example-book \
  --title "Example Book" \
  --language en \
  --mode article \
  --output-dir ~/.hermes/skills/books \
  --allow-overwrite no
```

### Validate the Generated Skill

```bash
python ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/validate_book_skill.py \
  --skill-dir ~/.hermes/skills/books/example-book/
```

## Examples

### 1. Convert a Markdown Article

```bash
python scripts/build_book_skill.py \
  --source ~/Documents/essay.md \
  --slug my-essay \
  --title "My Essay" \
  --language en \
  --mode article \
  --output-dir ~/.hermes/skills/books \
  --allow-overwrite no
```

### 2. Convert a TXT File

```bash
python scripts/build_book_skill.py \
  --source ~/Documents/notes.txt \
  --slug my-notes \
  --title "My Notes" \
  --language en \
  --mode article \
  --output-dir ~/.hermes/skills/books \
  --allow-overwrite no
```

### 3. Convert a Text PDF

```bash
python scripts/build_book_skill.py \
  --source ~/Documents/paper.pdf \
  --slug research-paper \
  --title "Research Paper" \
  --language en \
  --mode technical \
  --output-dir ~/.hermes/skills/books \
  --allow-overwrite no
```

### 4. Convert a Local HTML Article

```bash
python scripts/build_book_skill.py \
  --source ~/Downloads/article.html \
  --slug web-article \
  --title "Web Article" \
  --language en \
  --mode article \
  --output-dir ~/.hermes/skills/books \
  --allow-overwrite no
```

### 5. Convert a DOCX Report

```bash
python scripts/build_book_skill.py \
  --source ~/Documents/report.docx \
  --slug annual-report \
  --title "Annual Report" \
  --language en \
  --mode article \
  --output-dir ~/.hermes/skills/books \
  --allow-overwrite no
```

### 6. Convert an EPUB Book

```bash
python scripts/build_book_skill.py \
  --source ~/Books/novel.epub \
  --slug my-novel \
  --title "My Novel" \
  --language en \
  --mode book \
  --output-dir ~/.hermes/skills/books \
  --allow-overwrite no
```

## How to Use in Hermes

Once a skill is generated and validated, load it in Hermes:

```
skill_view(name='example-book')
```

Then query it:

```
@example-book What is this document about?
@example-book List the key concepts.
@example-book Summarize chapter 3.
@example-book Turn this into a Chinese reading note.
```

You can also view individual chapters:

```
skill_view(name='example-book', file_path='chapters/ch03-example.md')
```

## Bilingual Glossary Workflow

For documents available in both English and Chinese, the tool supports a complete bilingual glossary workflow:

1. Generate English skill + Chinese skill separately
2. Generate bilingual glossary v1 (rule-based alignment)
3. Fix source structure if chapter gaps exist
4. Generate bilingual glossary v2 (after any rebuild)
5. Generate review packet for low-confidence terms
6. User reviews and makes decisions
7. Generate bilingual glossary v3 (with user decisions applied)
8. Safe write-back of approved terms to both skill glossaries

**Case study**: `the-artist-is-dead-en` + `the-artist-is-dead-zh`

- 4 user-reviewed terms written back to both glossaries
- Bilingual glossary v3: 50 high-confidence, 25 medium, 14 low, 14 missing
- Workflow templates included in this repo

**Important**: The workflow does not automatically translate. It only aligns terms found in both language versions. LLM calls are not used for translation or enrichment.

## Security Model

- No automatic dependency installation
- No network fetching
- No LLM API calls
- No script execution from HTML / EPUB
- No DOCX macro execution
- No source document upload
- No secret storage
- No Hermes config modification
- No gateway restart
- No OCR
- No DRM handling

## Known Limitations

- Scanned/image-based PDFs are not supported (no OCR)
- RTF is not supported
- MOBI / AZW / AZW3 are not supported
- EPUB quality depends on source structure
- Glossary extraction is rule-based and may need manual review
- Not a full RAG system — skills are static snapshots
- Not a replacement for human reading

## Recommended Workflow

1. Pick a local document you want to keep referencing
2. Build a book skill with `build_book_skill.py`
3. Validate with `validate_book_skill.py`
4. Inspect SKILL.md, glossary, and chapters
5. Use `@skill-name` in Hermes for queries
6. For bilingual texts, run the glossary review workflow
7. Accumulate 5–10 book skills before building a higher-level Memex index

## Roadmap

See [ROADMAP.md](ROADMAP.md) for details.

## License

MIT License. See [LICENSE](LICENSE).

## Acknowledgments

Built for the Hermes agent ecosystem. Designed for local-first, privacy-respecting document management.
