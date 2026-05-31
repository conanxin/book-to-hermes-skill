# Release Freeze Pattern

Pattern for freezing a tool project's feature set and creating comprehensive documentation before daily use.

## When to Freeze

Freeze when:
- Core functionality is stable and tested
- No critical bugs remain
- User has approved the current feature set
- Adding more features would delay daily use

## Documentation Suite

Create these 8 files in the project root:

| File | Purpose | Key Sections |
|------|---------|--------------|
| `README.md` | Project overview | What it does, supported formats, quick start, safety boundaries |
| `QUICKSTART.md` | Copy-paste examples | One example per format, common parameters, troubleshooting |
| `EXAMPLES.md` | Naming conventions | Mode selection guide, slug/title/language rules |
| `SECURITY.md` | Safety boundaries | What the tool does NOT do, privacy considerations |
| `MAINTENANCE.md` | Developer guide | Directory structure, script usage, regression testing, backup/rollback |
| `TEST_MATRIX.md` | Test results | All test cases with source/output/validate status |
| `RELEASE_NOTES.md` | Changelog | Version, features, limitations, dependencies |
| `PHASE_INDEX.md` | Project history | Phase list with status, deliverables, report paths |

## Regression Validation Checklist

After any script modification, run:

1. **Validate all test skills**
   ```bash
   for skill in ~/.hermes/skills/books/*; do
     validate_book_skill.py --skill-dir "$skill"
   done
   ```

2. **Test extract_text.py on all format samples**
   ```bash
   for src in sample.md sample.html sample.docx sample.epub; do
     extract_text.py "$src" | jq '{ok, format, char_count}'
   done
   ```

3. **Security scan**
   ```bash
   grep -n "pip install\|apt install\|curl\|wget\|requests\|openai\|anthropic" scripts/*.py
   ```

## Release Freeze Decision Log

Document in PHASE_INDEX.md:
- What was frozen (format list, feature set)
- What was deferred (with reasons)
- What would trigger unfreezing (user request, critical bug)

## Example from book-to-hermes-skill Phase 0-k

**Frozen**: Markdown, TXT, PDF, HTML, DOCX, EPUB
**Deferred**: RTF (striprtf not installed), MOBI/AZW/AZW3 (Calibre not installed), OCR PDF (no OCR engine), DRM EPUB (no DRM tools)
**Trigger for unfreezing**: User explicitly requests a deferred format and approves dependency installation
