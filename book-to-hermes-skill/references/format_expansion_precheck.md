# Format Expansion Precheck Reference

Session-tested dependency audit and format support evaluation from Phase 0-g (2026-05-31).

---

## Precheck Workflow

Before adding any new format support, run this exact sequence:

1. **Audit existing dependencies** — check tools + Python packages
2. **Design extractor** — signatures, docstrings, security model
3. **Design install strategy** — venv isolation, no system pollution
4. **Inventory sample files** — search limited directories only
5. **Evaluate priority** — sample availability + install impact + user value
6. **Write report** — do not install, do not modify scripts

---

## Dependency Audit Commands

### Command-line tools
```bash
for cmd in python3 pip pdftotext pdfinfo ebook-convert pandoc file unzip; do
  which "$cmd" 2>/dev/null && echo "$cmd: PRESENT" || echo "$cmd: MISSING"
done
```

### Python packages
```bash
python3 -c "
import sys
packages = ['ebooklib', 'beautifulsoup4', 'bs4', 'docx', 'striprtf', 'lxml', 'html5lib', 'pypandoc']
for pkg in packages:
    try:
        mod = __import__(pkg)
        ver = getattr(mod, '__version__', 'unknown')
        print(f'{pkg}: PRESENT (v{ver})')
    except ImportError:
        print(f'{pkg}: MISSING')
"
```

### Venv check
```bash
ls ~/.hermes/venvs/book-to-hermes-skill/bin/python 2>/dev/null && echo "venv exists" || echo "venv missing"
```

---

## Sample File Inventory

Search ONLY these directories (do not scan full filesystem):
- `~/.hermes/workspace/`
- `~/Downloads/`
- `~/Documents/`

```bash
find ~/.hermes/workspace ~/Downloads ~/Documents -maxdepth 4 -type f \
  \( -name "*.html" -o -name "*.htm" -o -name "*.docx" -o -name "*.epub" \
     -o -name "*.rtf" -o -name "*.mobi" -o -name "*.azw" -o -name "*.azw3" \) \
  2>/dev/null | while read f; do stat -c "%n|%s|%y" "$f"; done
```

**Exclusions**: smoke test files, generated skill directories, secret/config/token files, tiny template files unless no other option.

---

## Install Strategy Template

### Scheme A: Minimal Python venv
- **Path**: `~/.hermes/venvs/book-to-hermes-skill/`
- **Scope**: HTML, DOCX, EPUB, RTF
- **Packages**: beautifulsoup4, ebooklib, python-docx, striprtf, lxml
- **Rule**: Never install into system Python or Hermes venv

### Scheme B: Calibre Extension
- **Tool**: `ebook-convert` (Calibre suite)
- **Scope**: MOBI, AZW, AZW3
- **Install**: `apt install calibre` (~200-400MB)
- **Default**: Defer unless user explicitly requests Kindle format support

---

## Priority Matrix

| Format | Sample Found? | Deps Present? | Install Impact | Priority |
|--------|---------------|---------------|----------------|----------|
| HTML | Yes | Yes (bs4+lxml) | None | Immediate |
| DOCX | Maybe | No (python-docx) | Low (venv pip) | High |
| EPUB | Maybe | No (ebooklib) | Low (venv pip) | Medium |
| RTF | Rare | No (striprtf) | Low (venv pip) | Low |
| MOBI/AZW | Rare | No (Calibre) | High (apt) | Defer |

**Rule**: If zero sample files found for a format, drop it in priority regardless of technical ease.

---

## Phase 0-g Boundaries (Non-Negotiable)

- No install
- No network
- No LLM call
- No script modification
- No config change

The entire phase is read-only audit + design-only documentation.

---

## Report Template

```markdown
# Phase X-g: Format Expansion Precheck Report

## STATUS: PASS / PARTIAL / FAIL

## Dependency Status Table
| Tool/Package | Status | Version | Path |

## Sample File Candidates
| File | Size | Modified | Format |

## Format Support Design
| Format | Deps | Risk | Route |

## Install Strategy
- Scheme A: ...
- Scheme B: ...

## Code改造点 Design
- extract_text.py additions (signatures only)
- supported_formats.md updates

## Risk Assessment
- Security: ...
- Privacy: ...
- Compatibility: ...
- Maintenance: ...

## Recommended Priority
1. ...
2. ...
3. ...

## Phase X-h Suggestion
...
```

---

*Reference created: 2026-05-31*
*Phase: 0-g*
