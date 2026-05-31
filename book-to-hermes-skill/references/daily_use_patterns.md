# Daily-Use Patterns & Known Limitations

Reference from Phase 1-a first real daily-use test (2026-05-31).

## What Worked

- 46-chapter English academic paper processed end-to-end without errors
- Validate PASS with 0 errors, 0 warnings, 0 content_notices
- HTML extraction via bs4+lxml handled 95KB source reliably
- Progressive disclosure structure held at scale (SKILL.md ~12K chars, chapters ~800-2,500 chars each)
- Patterns.md maintained evidence-driven structure across all 46 entries

## Known Limitations

### Empty Glossary for English Documents

**Symptom**: `glossary.md` contains only `"(No terms extracted from source. Consider manual enrichment.)"`

**Root cause**: English academic papers lack the bold/code technical terms that Chinese project docs have. Current term extraction relies heavily on `**bold**` and `` `code` `` markers. English papers use italics for terms, which are not currently extracted.

**Workaround**: Manually enrich glossary.md after generation. Key terms to add for art theory papers: Integrity, Generativity, Colonization, Cultivation, Institutional Layer, Relational Layer, Individual Layer, Q1/Q2/Q3/Q4 quadrants.

**Future fix**: Add italic term extraction (`*term*`) for English documents; add proper noun detection for framework names.

### HTML Title Extraction for First Chapter

**Symptom**: ch01 title becomes `art_history.pdf` (from HTML `<title>` tag) instead of the actual paper title.

**Root cause**: HTML `<title>` tag often contains the filename, not the document title. The extractor uses `<title>` as first priority for title_guess, but for converted PDFs the title tag is just the original filename.

**Workaround**: Pass `--title` explicitly when generating. Or manually rename ch01 after generation.

**Future fix**: For HTML documents, prefer first `<h1>` over `<title>` when `<title>` looks like a filename (ends with .pdf, .html, contains underscores).

### Overly Long Chapter Titles

**Symptom**: Some chapter filenames exceed 80 characters because the title includes summary text from the heading.

**Example**: `ch25-52-six-directional-transmission-instantiated-in-art-the-frameworks-six-directional-transmission-model-has-a-complete-instantiation-in-the-art-domain.md`

**Root cause**: HTML heading text sometimes contains a full sentence (heading + subtitle in same `<h1>`). The slug generator preserves all text.

**Workaround**: Acceptable for now. Filesystem handles long names. For readability, manual rename is optional.

**Future fix**: Truncate slug at first sentence boundary (period, colon, em-dash) if title exceeds 60 chars.

### Stale Limitations Text in source_manifest.md

**Symptom**: Generated `source_manifest.md` still says "Only Markdown, TXT, and text PDF are supported in this phase."

**Root cause**: Template string in build_book_skill.py was not updated when HTML/DOCX/EPUB support was added.

**Workaround**: Manually edit after generation, or ignore (the limitation note is informational, not enforced).

**Future fix**: Update template to reflect current format support matrix.

## Daily-Use Workflow

### Selecting a Source Document

1. Search limited directories: `~/.hermes/workspace/`, `~/Downloads/`, `~/Documents/`
2. Exclude: smoke tests, phase outputs, secret files, tiny templates
3. Prefer: real long-form content, clear chapter structure, recent research interest
4. Check: not already converted to a skill (avoid duplicates)

### Generation Command

```bash
source ~/.hermes/venvs/book-to-hermes-skill/bin/activate && \
python ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/build_book_skill.py \
  --source <path> \
  --slug <slug> \
  --title "<title>" \
  --language <zh|en|zh-en> \
  --mode <technical|narrative|article|api-docs|project-docs> \
  --output-dir ~/.hermes/skills/books \
  --allow-overwrite no
```

### Validation Command

```bash
python ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/validate_book_skill.py \
  --skill-dir ~/.hermes/skills/books/<slug>
```

### Post-Generation Manual Steps

1. **Check glossary.md** — if empty, manually add key terms
2. **Check ch01 title** — if it's a filename, consider renaming
3. **Check source_manifest.md** — update limitations text if needed
4. **Spot-check 2-3 chapters** — verify extractive summary quality

### Using the Skill in Hermes

```
skill_view(name='<slug>')
```

Or load a specific chapter:

```
skill_view(name='<slug>', file_path='references/chXX-<title>.md')
```

## Format-Specific Notes

| Format | Daily-use readiness | Caveats |
|--------|---------------------|---------|
| Markdown | Excellent | Native format, no extraction loss |
| TXT | Excellent | Simple and reliable |
| PDF (text) | Good | Layout may be flattened; tables lose structure |
| HTML | Good | Title extraction may use filename; long headings create long filenames |
| DOCX | Good | Requires venv with python-docx; list formatting acceptable |
| EPUB | Good | Requires venv with ebooklib; nested lists flattened |
| RTF | Not ready | Dependency not installed |
| MOBI/AZW | Not ready | Calibre not installed |
