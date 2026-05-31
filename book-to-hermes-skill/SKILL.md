---
name: book-to-hermes-skill
description: "Convert Markdown / TXT / PDF text documents into Hermes-native book skills. Generates structured, on-demand knowledge bases with chapter summaries, glossary, patterns, and cheatsheets. Supports Chinese and English."
category: knowledge
toolsets:
  - terminal
  - file
argument-hint: <source_path> [--slug <name>] [--title <title>] [--language zh|en|zh-en] [--mode technical|narrative|article|api-docs|project-docs] [--output-dir <dir>] [--allow-overwrite yes|no]
---

# Book-to-Hermes-Skill Converter

Transform written knowledge into actionable Hermes skills by extracting structure — not producing summaries.

## Phase History

| Phase | Status | Key Deliverable |
|-------|--------|-----------------|
| 0-a | PASS | Readiness audit of local Hermes environment |
| 0-b | PASS | Skill skeleton creation + smoke test with synthetic document |
| 0-c | PASS | Offline extractive summary filling (no placeholders, no LLM) |
| 0-d | PARTIAL | Real document test (lofi-engine build report, 17.6K chars, 19 chapters) |
| 0-e | PASS | Quality hardening: table normalization, topic filtering, evidence-driven patterns, layered validation |
| 0-f | PARTIAL | Glossary/topic refinement: stricter Chinese fragment detection, table syntax cleanup, version number filtering, strong suffix whitelist narrowing |
| 0-f-resume | PASS | Final quality gate: tool loop handling, glossary count limit (29 terms), Topic Index clean, validate PASS with 3 content_notices |
| 0-g | PASS | Format expansion precheck: dependency audit, install strategy design, code改造点 design, no install |
| 0-h | PASS | HTML + DOCX first-batch support: bs4+lxml HTML extractor, python-docx DOCX extractor via isolated venv, smoke tests PASS |
| 0-h-real | PASS | Real HTML document end-to-end test (The_Artist_Is_Dead.html, 37K, 8 chapters, validate PASS) |
| 0-i | PASS | EPUB support: ebooklib + bs4 in isolated venv, EPUB extractor implemented, smoke test EPUB created, format-detection bug fixed and verified |
| 0-j | PASS | Real EPUB test: complex stress test with 8 chapters, extractor refactored to avoid nested-content double-processing, table/list/blockquote extraction fixed, validate PASS |
| 0-k | PASS | Release freeze: format support frozen, documentation finalized, regression validation complete |
| 1-a | PASS | First real daily-use test: 46-chapter English academic paper (art_history.html), validate PASS, glossary empty for English docs |
| 1-b | PASS | English glossary extraction enhancement + HTML title fix + source_manifest update. 40 terms extracted (was 0). ch01 title fixed from `art_history.pdf` to full paper title. |

### Phase 1-b Techniques (2026-05-31)

**English academic term extraction**: Added `_is_quality_english_term()` with dedicated filtering for English academic papers. Sources: title/h1/h2/h3 noun phrases, bold terms, code terms, Title Case phrases (e.g., "Horizontal Axis Integrity"), hyphenated concepts (e.g., "non-instrumentality"), and a hardcoded academic concept list (integrity, generativity, colonization, cultivation, autonomy, instrumentalization, non-instrumentality, aesthetics, agency, practice, form, meaning, value, tradition, medium, subject, object, relation, axis, structure, self, world). Quality rules: 1-4 words, 5-60 chars, single word >=5 letters, filter stop words/version numbers/URLs/file extensions/shell commands. Priority: academic concepts > Title Case > bold/code > frequent terms. Max 40 terms for article mode.

**Title Case false positive filtering**: Title Case regex must check surrounding context — skip if preceded by lowercase letter or followed by lowercase letter (indicates sentence mid-flow). Skip common sentence starters (The, This, That, These, Those, There, Their, They, Then, Than). Skip if all words are common function words.

**Extractive glossary explanations**: `generate_glossary()` now attempts to find a sentence containing the term in the source text and uses it as the explanation. Falls back to "Appears in source; definition requires manual enrichment." No LLM-generated definitions.

**HTML filename-title detection**: Added `_looks_like_filename()` helper that detects: file extensions (.pdf/.html/.htm/.docx/.epub/.txt/.md), pure filename characters (alphanumeric + _ - .), underscore-separated stems (e.g., "art_history"). `guess_title()` skips filename-like headings and tries the next candidate. `split_into_chapters()` tracks `seen_real_title` and skips filename-like h1 headings without flushing current chapter.

**source_manifest template update**: Updated to list all 6 supported formats (Markdown, TXT, text PDF, HTML, DOCX, EPUB) and 4 unsupported formats (OCR PDF, DRM EPUB, RTF, MOBI/AZW/AZW3). Added safety notes section documenting no script execution, no macro execution, no network, no LLM.

**EPUB import bug fix**: `_extract_epub_with_ebooklib()` was missing `import ebooklib` at module level, causing `NameError: name 'ebooklib' is not defined` when checking `item.get_type() == ebooklib.ITEM_DOCUMENT`. Fix: add `import ebooklib` before `from ebooklib import epub`.

### Phase 1-a Techniques (2026-05-31)

**Daily-use workflow**: Tool is now ready for converting real documents to skills. Workflow: (1) search limited dirs for candidate, (2) run build_book_skill.py with explicit title/language/mode, (3) validate, (4) manual post-check of glossary and ch01 title, (5) use via `skill_view(name='slug')`.

**English document glossary gap**: English academic papers produce empty glossaries because term extraction relies on `**bold**` and `` `code` `` markers, while English papers use italics for terms. **Fixed in Phase 1-b** — now extracts Title Case phrases, hyphenated concepts, and frequent academic words.

**HTML title extraction pitfall**: For HTML documents converted from PDF, the `<title>` tag often contains the original filename (`art_history.pdf`) rather than the document title. The first chapter title becomes this filename. **Fixed in Phase 1-b** — `_looks_like_filename()` now skips filename-like headings.

**Long chapter title filenames**: HTML headings that contain full sentences produce very long filenames (80+ chars). Acceptable for filesystems but hurts readability. Future fix: truncate slug at first sentence boundary if title exceeds 60 chars.

**Stale source_manifest.md template**: Generated files still claim "Only Markdown, TXT, and text PDF are supported" even though HTML/DOCX/EPUB are now supported. **Fixed in Phase 1-b** — template now lists all 6 supported formats.

### Phase 0-i Techniques (2026-05-31)

**EPUB extractor via ebooklib + bs4**: Uses `ebooklib.epub.read_epub()` to load the book, iterates spine-ordered document items, parses each XHTML chapter with BeautifulSoup, decomposes script/style/nav/svg, then converts h1-h6/p/li/blockquote/pre/code/table to Markdown. Title guess priority: (1) EPUB metadata `book.get_metadata('DC', 'title')`, (2) first `<h1>`, (3) filename stem. Venv helper pattern used since ebooklib is only in isolated venv.

**Format detection bug — EPUB misidentified as DOCX**: `.epub` was not in `SUPPORTED_EXTENSIONS`, so `detect_format()` fell through to magic-bytes detection. ZIP header (`PK`) defaulted to `docx`. Fix: add `.epub` to extension whitelist, prioritize extension over magic bytes, return unknown for ambiguous ZIP containers. See `references/format_detection_pitfalls.md`.

**Venv dependency chain gap**: Installing `ebooklib` alone was insufficient — `beautifulsoup4` is also required for XHTML parsing. Fix: install complete dependency chain before testing. See `references/format_detection_pitfalls.md` for pre-flight checklist.

**HTML title extraction optimization**: `title_guess` now checks `<title>` tag first, then first `<h1>`, then `meta[property="og:title"]`, then `meta[name="twitter:title"]`, then filename stem. Body extraction prefers `<main>` if present, then `<article>`, then `<body>`.

**DOCX list style detection**: Paragraphs with style names containing `List Bullet`, `List Number`, `Bullet`, or `Number` are now prefixed with `- ` or `1. ` respectively. If numbering cannot be determined reliably, falls back to `- `.

### Phase 0-h Techniques (2026-05-31)

**HTML extractor safety**: Use BeautifulSoup with explicit element blacklist — script, style, noscript, svg, nav, footer, aside, iframe, embed, object. Never execute JavaScript. Never make network requests. Prefer lxml parser, fallback to html.parser. Convert extracted structure to Markdown: h1-h6 → #/##/###, p → paragraphs, li → bullets, blockquote → > quotes, pre/code → fenced blocks, tables → Markdown tables or field-list fallback.

**DOCX extractor isolation**: python-docx is installed in an isolated venv (`~/.hermes/venvs/book-to-hermes-skill/`). The main extract_text.py attempts `import docx` first; on ImportError, it spawns the venv Python with an inline helper script that reads the DOCX and returns JSON. The helper is strictly read-only and accepts only a file path argument. No arbitrary code execution.

**Venv Python subprocess pattern**: For optional dependencies that must not pollute the main environment, use a controlled subprocess pattern: (1) detect missing import, (2) check venv exists, (3) run inline helper via subprocess with timeout, (4) parse JSON stdout, (5) propagate errors clearly. Never auto-install inside the helper.

**Smoketest DOCX generation**: When no real DOCX sample exists, create a minimal test document programmatically via python-docx. Must include: Heading 1, Heading 2, English paragraph, Chinese paragraph, bullet list, simple table. No images, no macros, no external links, no sensitive content.

### Phase 0-g Techniques (2026-05-31)

**Dependency-first design**: Before writing any extractor code, audit the environment for existing tools and packages. Classify each as PRESENT/MISSING with version and path. This prevents mid-implementation surprises and informs the install strategy.

**Venv isolation for optional deps**: Propose `~/.hermes/venvs/book-to-hermes-skill/` for all new Python packages. Never install into system Python or the active Hermes venv. This keeps the skill self-contained and uninstallable by directory deletion.

**Calibre deferral criteria**: MOBI/AZW/AZW3 support requires Calibre (~200-400MB apt install). Defer when: (a) no sample files exist to test with, (b) format is low-priority for user's workflow, (c) install impact exceeds value. Document the deferral decision with clear re-evaluation trigger.

**Sample file inventory before implementation**: Search limited directories (`~/.hermes/workspace`, `~/Downloads`, `~/Documents`) for candidate files of each target format. If zero files found, that format drops in priority regardless of technical ease.

**Extractor design without implementation**: Write complete function signatures and docstrings for each new extractor. Include dependency probe, error message template, and security considerations (script removal, no network). Do not modify the production script until dependencies are installed and sample files are available.

**Phase 0-g boundaries**: No install, no network, no LLM, no script modification, no config change. The entire phase is read-only audit + design-only documentation.

### Phase 0-f Techniques (2026-05-31)

**Stricter Chinese fragment detection**: `_is_meaningful_chinese()` now tests ALL fragment endings and rejects if ANY match with a bad prefix. Added `_BAD_2CHAR_TERMS` set for low-quality 2-character terms. Expanded fragment start list to 27 entries.

**Table syntax cleanup**: `_clean_term()` strips `|`, `-`, em-dash, bullets. `_is_quality_topic()` rejects code terms containing `|` or multiple `...` sequences.

**Version number filtering**: `_is_quality_topic()` rejects pure numbers with units (`37 MB`, `65+`) and mixed version strings via regex.

**Strong suffix whitelist narrowing**: Replaced broad `has_high_quality` bypass with explicit `strong_suffixes` list (80+ entries). Low-quality prefixes (无/有/是/否/已/未/不) only pass if combined with strong technical suffixes.

**Universal quality gate**: `extract_terms()` now applies `_is_quality_topic()` to ALL term types, not just Topic Index. Glossary and Topic Index share the same filtering.

**Known residual issues**:
- Long sentence fragments with mixed Chinese-English (`skill 骨架 如果 wslview 验证失败 如 file`) — rare edge case
- Status phrases with novel forms may bypass `_STATUS_WORDS` — requires ongoing expansion
- Chapter title references in glossary are expected metadata, not glossary terms

**Phase 0-f-resume lessons**:
- Negative verification commands (`grep` for absence) must handle exit code 1 as success
- Glossary term count should be capped at ~30 for project-docs mode; technical mode may allow up to 40
- Topic Index must be explicitly checked against a deny-list of status words after generation
- Tool loop warnings block progress — design verification commands to avoid repeated identical calls

### Phase 0-j Techniques (2026-05-31)

**EPUB extractor nested-content fix**: Original `body.descendants` traversal caused double-processing of nested elements (e.g., blockquote's inner `p` extracted separately, then blockquote itself extracted again). Fix: use `body.find_all(recursive=False)` for top-level elements only, with a recursive `_process_epub_element()` function that handles container elements (`div`, `section`, `article`) by recursing into direct children, and leaf elements (`p`, `h1`, `ul`, `blockquote`, `pre`, `table`) directly. This eliminates duplicate extraction and preserves structural boundaries.

**EPUB list formatting**: `ul`/`ol` elements are now processed as units. Each `li` becomes a `- ` bullet line, and a blank line is added after the list. Nested lists are flattened (all items at same level) — true nested Markdown list indentation is not yet implemented.

**EPUB table extraction**: Tables are now correctly passed to `extract_html_table()` which converts them to Markdown tables or field-list fallback. Previously tables were silently dropped.

**EPUB blockquote handling**: Blockquote content is extracted once as a unit, with `> ` prefix on each line. Multiple paragraphs inside a blockquote are concatenated — preserving paragraph breaks within blockquotes is a known residual issue.

**EPUB code block handling**: `pre` elements are extracted as fenced code blocks. `code` elements inside `pre` are not double-processed because `pre` is handled as a leaf element.

**Unicode JSON output fix**: Venv helper `json.dumps()` must use `ensure_ascii=False` to preserve Chinese characters in output. Without this, Chinese text appears as `\uXXXX` escape sequences.

**Complex EPUB stress test**: When no real EPUB sample exists, create a comprehensive test document with 8 chapters covering: English/Chinese paragraphs, h1/h2/h3 headings, bullet/numbered/nested lists, simple/wide HTML tables, blockquote, inline code, fenced code block, footnote-like section, image references, nav/TOC. No external links, no scripts, no sensitive content.
- EPUB format misrouted to DOCX extractor: add explicit `.epub` extension check BEFORE zip-magic detection
- ebooklib only available in venv, not main interpreter: use venv helper pattern, do not install into main interpreter
- EPUB smoke test creation: use `ebooklib.epub` programmatically; require 3+ chapters with diverse content types

## Design Principles

1. **On-demand loading** — chapter files load only when queried, never all at once
2. **Structure over summary** — extract frameworks, mental models, principles, anti-patterns
3. **Chinese compatible** — supports Chinese chapter detection, terminology, and patterns
4. **Graceful degradation** — missing dependencies trigger clear errors, never auto-install
5. **Safety first** — no network calls, no arbitrary shell execution, no secret exposure

## Supported Formats

| Format | Status | Extractor | Dependencies | Notes |
|--------|--------|-----------|--------------|-------|
| Markdown | ENABLED | direct read | none | UTF-8 with encoding fallback |
| Plain text | ENABLED | direct read | none | UTF-8 with encoding fallback |
| PDF (text) | ENABLED | pdftotext → pdfminer.six | poppler-utils or pdfminer.six | Layout preserved with pdftotext |
| HTML | ENABLED | beautifulsoup4 | bs4 + lxml present | Local files only; no script execution; no network |
| DOCX | ENABLED | python-docx | python-docx installed in isolated venv | Local files only; no macros; no embedded objects; no image OCR |
| EPUB | ENABLED | ebooklib + bs4 | ebooklib, beautifulsoup4 | Local files only; no DRM; no script execution |
| RTF | DISABLED | striprtf | striprtf | install to enable |
| MOBI/AZW/AZW3 | DISABLED | ebook-convert (Calibre) | Calibre | install to enable; defer to later phase |

## Input Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `source_path` | yes | — | Path to source document |
| `slug` | no | derived from filename | Skill directory name under `books/` |
| `title` | no | auto-detected | Book title |
| `language` | no | `auto` | `zh` / `en` / `zh-en` / `auto` |
| `mode` | no | `auto` | `technical` / `narrative` / `article` / `api-docs` / `project-docs` |
| `output_dir` | no | `~/.hermes/skills/books/` | Output root directory |
| `allow_overwrite` | no | `no` | `yes` to overwrite existing skill directory |

## Output Structure

```
<output_dir>/<slug>/
├── SKILL.md              # Core skill definition (~4,000 tokens max)
├── metadata.json         # Machine-readable metadata
├── source_manifest.md    # Source file provenance
├── chapters/             # Per-chapter summaries (~800-1,200 tokens each)
│   ├── ch01-<slug>.md
│   ├── ch02-<slug>.md
│   └── ...
├── glossary.md           # Key terms alphabetically sorted (~1,500 tokens)
├── patterns.md           # Techniques and design patterns (~2,000 tokens)
└── cheatsheet.md         # Quick reference tables (~1,000 tokens)
```

## Execution Flow

### Step 1 — Validate Source

- Verify `source_path` exists and is a file
- Detect format by extension and magic bytes
- Check required dependencies for the detected format
- If dependencies missing, report clearly and stop (no auto-install)

### Step 2 — Extract Text

Run `scripts/extract_text.py`:

```bash
python3 ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/extract_text.py \
  "$SOURCE_PATH" --mode "$MODE"
```

Output: JSON to stdout with fields `ok`, `source_path`, `format`, `title_guess`, `text`, `char_count`, `warnings`, `errors`.

### Step 3 — Split into Chapters/Sections

- Detect chapter boundaries (supports `Chapter N`, `CHAPTER N`, `第N章`, `第 N 章`, `# Heading`, `## Heading`)
- For documents without clear chapters, split by heading level or word count (~3,000 words per section)
- Generate chapter metadata: number, title, estimated tokens, key frameworks

### Step 4 — Build Generated Skill

Run `scripts/build_book_skill.py`:

```bash
python3 ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/build_book_skill.py \
  --source "$SOURCE_PATH" \
  --slug "$SLUG" \
  --title "$TITLE" \
  --language "$LANGUAGE" \
  --mode "$MODE" \
  --output-dir "$OUTPUT_DIR" \
  --allow-overwrite "$ALLOW_OVERWRITE"
```

Generates all output files.

### Step 5 — Validate Generated Skill

Run `scripts/validate_book_skill.py`:

```bash
python3 ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/validate_book_skill.py \
  --skill-dir "$OUTPUT_DIR/$SLUG"
```

Checks:
- All required files exist
- SKILL.md is valid and under token budget
- chapters/ are individually under budget
- metadata.json is valid JSON
- No secrets or PII in generated files

## Progressive Disclosure

- **SKILL.md** — core mental models, chapter index, topic index only
- **chapters/** — loaded on-demand via `read_file` when user queries a topic
- **glossary.md / patterns.md / cheatsheet.md** — lightweight reference files

Never load the entire book text into context. Maximum loaded at once: SKILL.md (~4K) + one chapter (~1K) = ~5K tokens.

## Safety Policy

| Rule | Enforcement |
|------|-------------|
| No auto-install | `extract_text.py` has no `pip install`, `apt install`, or package manager calls |
| No network | No HTTP requests, no downloads, no API calls |
| No overwrite without consent | If `books/<slug>/` exists, append `-2` or prompt user |
| No secret exposure | Generated files are scanned for patterns matching API keys, tokens, passwords |
| No full-text injection | Only structured summaries enter skill files; raw text stays in temp files |

## Usage Examples

```bash
# Convert a technical PDF
hermes skill run book-to-hermes-skill ~/books/designing-data-intensive-apps.pdf \
  --slug ddia --mode technical

# Convert a Chinese EPUB (once dependencies installed)
hermes skill run book-to-hermes-skill ~/books/深入理解计算机系统.epub \
  --slug csapp-zh --language zh --mode technical

# Convert a Markdown article
hermes skill run book-to-hermes-skill ~/articles/raft-paper.md \
  --slug raft --mode article
```

## Post-Conversion Usage

```bash
# Load core frameworks
hermes skill load books/ddia

# Query a specific topic (loads relevant chapter on-demand)
hermes skill load books/ddia --query "replication strategies"

# Load a specific chapter
hermes skill load books/ddia --chapter ch05

# Browse available chapters
hermes skill load books/ddia --list-chapters
```

## Scope & Limits

- This skill covers the source document content only
- For implementation guidance, combine with project-specific tools
- For topics beyond the book, use research skills or direct queries
- Scanning PDFs (image-based) require OCR — not supported in current phase

## References

- `references/english_term_extraction.md` — English academic term detection, Title Case filtering, hyphenated concepts, extractive explanations (Phase 1-b)
- `references/html_title_extraction.md` — Filename-like title detection and skipping for HTML/PDF-converted documents (Phase 1-b)
- `references/output_schema.md` — output directory structure and file specifications
- `references/supported_formats.md` — format support matrix and dependency install commands
- `references/safety_policy.md` — prohibited operations and input/output validation rules
- `references/pitfalls.md` — session-tested bugs, fixes, and verification steps
- `references/extractive_summary_rules.md` — offline summary generation without LLM (Phase 0-c)
- `references/chinese_term_extraction.md` — Chinese term filtering and mixed-language detection (Phase 0-d)
- `references/table_normalization.md` — Markdown table → readable bullet conversion (Phase 0-e)
- `references/validate_layered_safety.md` — Tool-safety vs content-notice validation split (Phase 0-e)
- `references/html_docx_extractor.md` — HTML + DOCX extractor implementation details, venv helper pattern, known limitations (Phase 0-h)
- `references/format_detection_pitfalls.md` — format detection bugs and dependency chain gaps (Phase 0-i)
- `references/format_expansion_precheck.md` — Dependency audit and format support evaluation (Phase 0-g)
- `references/release_freeze_pattern.md` — Release freeze documentation suite structure and regression checklist (Phase 0-k)
- `references/daily_use_patterns.md` — Daily-use workflow, known limitations, and post-generation manual steps (Phase 1-a)

## License

MIT — adapted from virgiliojr94/book-to-skill
