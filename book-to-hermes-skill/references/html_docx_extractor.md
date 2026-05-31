# HTML + DOCX Extractor Implementation Reference

Session-tested implementation details from Phase 0-h (2026-05-31).

---

## HTML Extractor (`extract_html`)

### Dependency Stack
- **Primary**: `beautifulsoup4` + `lxml` (lxml for speed, html.parser fallback)
- **Already present in environment**: bs4 v4.14.3, lxml v6.0.2
- **No additional install needed**

### Security Model
- **Never execute JavaScript** — no browser engine, no script execution
- **Never make network requests** — local file only
- **Explicit element blacklist** (decomposed before extraction):
  `script`, `style`, `noscript`, `svg`, `nav`, `footer`, `aside`, `iframe`, `embed`, `object`
- **No CSS parsing** — style attributes ignored

### Markdown Mapping

| HTML Element | Markdown Output |
|--------------|-----------------|
| `h1`–`h6` | `#`–`######` heading |
| `p` | plain paragraph |
| `li` | `- ` bullet |
| `blockquote` | `> ` quote line |
| `pre` / `code` | fenced code block ` ``` ` |
| `table` | Markdown table OR field-list fallback |

### Table Handling Strategy
- Simple tables (≤4 columns, ≤10 rows) → Markdown pipe table
- Complex tables → field-list (`field: value; field: value`)
- Cell text sanitized: `|` → `\|`, newlines → spaces

### Known Limitations
1. `title_guess` falls back to filename stem when `<title>` tag is present but not prioritized. Fix: check `soup.find("title")` before `guess_title()`.
2. Soft hyphens (`&shy;` or U+00AD) preserved in output as visible hyphens. Low impact.
3. Nested lists flattened to single-level bullets.
4. Images completely dropped (no alt text extraction).

---

## DOCX Extractor (`extract_docx`)

### Dependency Stack
- **Primary**: `python-docx` v1.2.0
- **Install location**: isolated venv at `~/.hermes/venvs/book-to-hermes-skill/`
- **Never install into system Python or Hermes venv**

### Venv Subprocess Pattern

When `import docx` fails in the main interpreter:

```python
VENV_PYTHON = "~/.hermes/venvs/book-to-hermes-skill/bin/python"

# Inline helper script — strictly read-only, single file path argument
helper = """
import json, sys
from docx import Document

def extract(path):
    doc = Document(path)
    lines = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text: continue
        style = para.style.name if para.style else ""
        if style.startswith("Heading"):
            level = int(style.replace("Heading ", ""))
            lines.append("#" * level + " " + text)
        else:
            lines.append(text)
        lines.append("")
    # ... table extraction ...
    return "\n".join(lines)

print(json.dumps({"text": extract(sys.argv[1]), "method": "python-docx-venv"}))
"""

result = subprocess.run(
    [VENV_PYTHON, "-c", helper, docx_path],
    capture_output=True, text=True, timeout=120
)
```

**Security properties**:
- Helper is inline string, not a file on disk
- Accepts exactly one argument: the file path
- No shell=True, no command injection
- No network, no auto-install

### Markdown Mapping

| DOCX Element | Markdown Output |
|--------------|-----------------|
| Heading 1–3 | `#`–`###` heading |
| Normal paragraph | plain paragraph |
| Table | Markdown pipe table |
| List Bullet / List Number | plain paragraph (current) — list style detection TODO |

### Known Limitations
1. **List styles not detected** — `List Bullet` / `List Number` paragraphs render as plain text. Need to inspect `para.style.name` for list prefixing.
2. **No macro execution** — python-docx does not execute macros by design
3. **No embedded object extraction** — silently skipped
4. **No image OCR** — images completely ignored
5. **No comment/revision tracking** — only current document text extracted

---

## Venv Management

### Creation (one-time)
```bash
mkdir -p ~/.hermes/venvs/book-to-hermes-skill
python3 -m venv ~/.hermes/venvs/book-to-hermes-skill
```

### Installing optional deps
```bash
~/.hermes/venvs/book-to-hermes-skill/bin/pip install python-docx
# Future: ebooklib, striprtf
```

### Verification
```bash
~/.hermes/venvs/book-to-hermes-skill/bin/python -c "import docx; print(docx.__version__)"
```

---

## Smoke Test DOCX Generation

When no real DOCX sample exists, generate a minimal test document:

```python
from docx import Document
doc = Document()
doc.add_heading('Test Document', level=1)
doc.add_heading('English Section', level=2)
doc.add_paragraph('English paragraph text.')
doc.add_heading('中文部分', level=2)
doc.add_paragraph('中文测试段落。')
doc.add_heading('Bullet List', level=2)
doc.add_paragraph('First item', style='List Bullet')
doc.add_paragraph('Second item', style='List Bullet')
doc.add_heading('Simple Table', level=2)
table = doc.add_table(rows=3, cols=3)
table.style = 'Table Grid'
# ... populate header + data rows ...
doc.save('test.docx')
```

Requirements: Heading 1/2, English + Chinese paragraphs, bullet list, simple table. No images, no macros, no external links, no sensitive content.

---

## Real Document Test Results (Phase 0-h-real)

### HTML Real Document
- **Source**: `The_Artist_Is_Dead.html` (37,337 bytes, academic article)
- **Result**: 8 chapters, validate PASS, SKILL.md 3,652 chars
- **Quality**: Title correct, paragraphs clean, no script/style noise, patterns evidence-driven
- **Glossary**: Empty (academic article, low term density — expected)

### DOCX Real Document
- **Status**: No real DOCX candidate found in `~/.hermes/workspace`, `~/Downloads`, `~/Documents`
- **Validation**: Only smoke test verified
- **Gap**: DOCX support not yet validated against real user document

---

*Reference created: 2026-05-31*
*Phase: 0-h / 0-h-real*
