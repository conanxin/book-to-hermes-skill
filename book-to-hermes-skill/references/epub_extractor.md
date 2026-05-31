# EPUB Extractor Implementation Reference

Session-tested implementation details from Phase 0-i (2026-05-31).

---

## EPUB Extractor (`extract_epub`)

### Dependency Stack
- **Primary**: `ebooklib` v0.20 + `beautifulsoup4` + `lxml`
- **Install location**: isolated venv at `~/.hermes/venvs/book-to-hermes-skill/`
- **Current interpreter status**: ebooklib NOT available in main interpreter; only in venv
- **Never install into system Python or Hermes venv**

### Security Model
- **Never execute JavaScript** — no browser engine, no script execution
- **Never make network requests** — local file only
- **No DRM support** — encrypted EPUBs are rejected with clear error
- **Explicit element blacklist** (decomposed before extraction):
  `script`, `style`, `noscript`, `svg`, `nav`, `footer`, `aside`, `iframe`, `embed`, `object`

### Title Guess Priority
1. EPUB metadata `book.get_metadata('DC', 'title')`
2. First `<h1>` in the first document item
3. Filename stem

### Spine Order Extraction
```python
from ebooklib import epub

book = epub.read_epub(epub_path)
# Iterate document items in spine order
for item in book.get_items_of_type(epub.ITEM_DOCUMENT):
    # Parse XHTML with BeautifulSoup
    soup = BeautifulSoup(item.get_content(), 'lxml')
    # Decompose noise elements
    for tag in soup.find_all(['script','style','noscript','svg','nav','footer','aside','iframe','embed','object']):
        tag.decompose()
    # Extract and convert to Markdown
```

### Markdown Mapping

| HTML Element | Markdown Output |
|--------------|-----------------|
| `h1`–`h6` | `#`–`######` heading |
| `p` | plain paragraph |
| `li` | `- ` bullet |
| `blockquote` | `> ` quote line |
| `pre` / `code` | fenced code block ` ``` ` |
| `table` | Markdown table OR field-list fallback |

### Known Limitations
1. **Format detection bug** — `.epub` files may be misidentified as `docx` by the format detector. Ensure extension check routes `.epub` before zip-based formats.
2. **Complex CSS ignored** — inline styles and CSS classes are not interpreted; only raw text content is extracted.
3. **Footnotes** — EPUB footnote markup (popup, noteref) is treated as regular links; footnote text may appear inline or be dropped.
4. **Cover images** — completely dropped; no OCR or alt text extraction.
5. **Internal links** — `<a href="...">` text is preserved, but link targets are not resolved.

---

## Format Detection Bug (Phase 0-i) — FIXED

**Symptom**: `extract_text.py` returns `"format": "docx"` for `.epub` files.

**Root Cause**: `.epub` was not in `SUPPORTED_EXTENSIONS`, so `detect_format()` fell through to magic-bytes detection. ZIP header (`PK`) defaulted to `docx`.

**Fix**: 
1. Add `.epub` to `SUPPORTED_EXTENSIONS` 
2. Prioritize extension check over magic bytes
3. For ambiguous ZIP containers without extension, return unknown rather than guessing

**Verification**:
```bash
python3 ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/extract_text.py \
  test.epub | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['format'])"
# Should print: epub
```

---

## EPUB Extractor Refactoring (Phase 0-j)

**Problem**: Original extractor used `body.descendants` which caused:
- Blockquote content extracted twice (once for inner `<p>`, once for `<blockquote>`)
- List items without spacing between them
- Tables not extracted at all
- Nested list content flattened incorrectly

**Solution**: Replaced `body.descendants` with `body.find_all(recursive=False)` + recursive element processor.

### Element Processor Logic

```python
def _process_epub_element(elem, lines, depth):
    if elem.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
        level = int(elem.name[1])
        text = elem.get_text(strip=True)
        if text:
            lines.append(f"{'#' * level} {text}")
            lines.append("")
    elif elem.name == "p":
        text = elem.get_text(strip=True)
        if text:
            lines.append(text)
            lines.append("")
    elif elem.name in ("ul", "ol"):
        _process_epub_list(elem, lines)
    elif elem.name == "blockquote":
        text = elem.get_text(strip=True)
        if text:
            for line in text.splitlines():
                if line.strip():
                    lines.append(f"> {line.strip()}")
            lines.append("")
    elif elem.name == "pre":
        text = elem.get_text(strip=False)
        if text:
            lines.append("```")
            lines.append(text.rstrip())
            lines.append("```")
            lines.append("")
    elif elem.name == "table":
        table_lines = extract_html_table(elem)
        if table_lines:
            lines.extend(table_lines)
            lines.append("")
    elif elem.name in ("div", "section", "article", "header", "footer", "main"):
        for child in elem.find_all(recursive=False):
            _process_epub_element(child, lines, depth + 1)

def _process_epub_list(list_elem, lines):
    for li in list_elem.find_all("li", recursive=False):
        text = li.get_text(strip=True)
        if text:
            lines.append(f"- {text}")
    lines.append("")
```

**Key insight**: Process container elements (`div`, `section`, `article`) by recursing into their direct children. Process leaf elements (`p`, `h1`, `ul`, `blockquote`, `pre`, `table`) directly. This avoids double-processing nested content.

---

## Unicode Output Fix (Phase 0-j)

**Problem**: venv helper output JSON with Chinese characters escaped as `\uXXXX` sequences.

**Root Cause**: `json.dumps()` defaults to `ensure_ascii=True`.

**Fix**: Add `ensure_ascii=False` to all `json.dumps()` calls in venv helpers:
```python
print(json.dumps({"text": text, "method": "ebooklib-venv"}, ensure_ascii=False))
```

---

## Dependency Chain Gap (Phase 0-i)

Installing `ebooklib` alone was insufficient — `beautifulsoup4` is also required for XHTML parsing. Both must be present in the venv before EPUB extraction works.

**Pre-flight checklist**:
```bash
~/.hermes/venvs/book-to-hermes-skill/bin/python -c "import ebooklib; print('ebooklib ok')"
~/.hermes/venvs/book-to-hermes-skill/bin/python -c "import bs4; print('bs4 ok')"
```

---

## Venv Helper Pattern for EPUB

When `import ebooklib` fails in the main interpreter, use the same venv subprocess pattern as DOCX. The helper script must include the full element processor (see above) and output JSON with `ensure_ascii=False`.

---

## Smoke Test EPUB Generation

When no real EPUB sample exists, generate a test document programmatically via ebooklib. Requirements:
- 6+ chapters with diverse content types
- English + Chinese paragraphs
- h1 / h2 / h3 headings
- Bullet list, numbered list, nested list
- HTML table (simple + wide)
- Blockquote
- Code block (inline + fenced)
- Footnote-like section
- Image references (no real images needed)
- Nav / TOC
- No images, no scripts, no external links, no DRM, no sensitive content

**Caution**: When creating EPUB content with ebooklib, pass actual UTF-8 strings (not Python `\uXXXX` escape sequences) to avoid Unicode escape artifacts in the output.

---

## Real Document Test Status

| Format | Real Document Found | Tested | Validate |
|--------|---------------------|--------|----------|
| HTML | Yes (The_Artist_Is_Dead.html) | Yes | PASS |
| DOCX | No | Smoke only | PASS |
| EPUB | No | Complex stress test | PASS |

**Gap**: Neither DOCX nor EPUB has been validated against a real user document. Both formats rely on synthetic tests only.

---

## Known Residual Issues

1. **Blockquote paragraph merging**: Multiple `<p>` inside `<blockquote>` are concatenated into one line. Preserving paragraph breaks within blockquotes requires tracking `<p>` boundaries.
2. **Topic Index table noise**: Table header cells and cell values may be extracted as topics. The quality filter should reject single-word table cells.
3. **Chapter merge**: `build_book_skill.py` may merge adjacent short sections into one chapter. This is by design for token budget management.
4. **Nested list flattening**: Nested `<ul>` inside `<li>` has all items flattened at the same level. True nested list Markdown (`  - sub-item`) is not yet implemented.
5. **EPUB metadata title fallback**: If `DC:title` is missing, falls back to first `<h1>`. Some EPUBs use non-standard metadata schemes.

---

*Reference updated: 2026-05-31*
*Phases: 0-i, 0-j*