# Maintenance Guide

## Directory Structure

```
~/.hermes/skills/knowledge/book-to-hermes-skill/
├── SKILL.md                    # Main skill definition
├── README.md                   # Project overview
├── QUICKSTART.md               # Copy-paste examples
├── EXAMPLES.md                 # Naming conventions and modes
├── SECURITY.md                 # Safety boundaries
├── MAINTENANCE.md              # This file
├── TEST_MATRIX.md              # Test results
├── RELEASE_NOTES.md            # Changelog
├── PHASE_INDEX.md              # Phase history
├── scripts/
│   ├── extract_text.py         # Text extraction from documents
│   ├── build_book_skill.py     # Skill generation
│   └── validate_book_skill.py  # Validation
├── references/
│   ├── supported_formats.md    # Format support matrix
│   ├── output_schema.md        # Output structure
│   ├── safety_policy.md        # Safety rules
│   ├── pitfalls.md             # Known bugs and fixes
│   └── ...                     # Other reference docs
└── chapters/                   # (none — this is a tool skill)
```

## Scripts

### extract_text.py

Extracts text from supported document formats.

```bash
python3 scripts/extract_text.py <path> [--mode technical|text]
```

Output: JSON to stdout with `ok`, `format`, `title_guess`, `text`, `char_count`, `warnings`, `errors`.

### build_book_skill.py

Generates a book skill from extracted text.

```bash
python3 scripts/build_book_skill.py \
  --source <path> \
  --slug <name> \
  --title <title> \
  --language <lang> \
  --mode <mode> \
  --output-dir <dir> \
  --allow-overwrite <yes|no>
```

### validate_book_skill.py

Validates a generated book skill.

```bash
python3 scripts/validate_book_skill.py --skill-dir <path>
```

Checks: required files, token budgets, JSON validity, secret scanning.

## Venv

Location: `~/.hermes/venvs/book-to-hermes-skill/`

Contains:
- python-docx (DOCX support)
- ebooklib + beautifulsoup4 (EPUB support)

To inspect:
```bash
~/.hermes/venvs/book-to-hermes-skill/bin/python -m pip list
```

## Adding a New Format

1. Add extension to `SUPPORTED_EXTENSIONS` in `extract_text.py`
2. Implement `extract_<format>()` function
3. Add branch in `main()`
4. Update `references/supported_formats.md`
5. Create smoke test file
6. Run build + validate
7. Update `TEST_MATRIX.md`

## Regression Testing

Run after any script modification:

```bash
# Test all formats
for skill in ~/.hermes/skills/books/book-to-skill-smoke-test \
             ~/.hermes/skills/books/phase0d-lofi-engine-static-build-report \
             ~/.hermes/skills/books/phase0h-real-html-test \
             ~/.hermes/skills/books/phase0h-docx-test \
             ~/.hermes/skills/books/phase0i-epub-smoke-test \
             ~/.hermes/skills/books/phase0j-complex-epub-stress-test; do
  if [ -d "$skill" ]; then
    echo "=== $(basename $skill) ==="
    python3 ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/validate_book_skill.py --skill-dir "$skill"
  fi
done
```

## Reports

All phase reports are in:
```
~/.hermes/workspace/reports/book_to_skill/
```

## Backup and Rollback

Before major changes:
```bash
cp -r ~/.hermes/skills/knowledge/book-to-hermes-skill \
  ~/.hermes/skills/knowledge/book-to-hermes-skill.backup-$(date +%Y%m%d-%H%M%S)
```

To rollback:
```bash
rm -rf ~/.hermes/skills/knowledge/book-to-hermes-skill
cp -r ~/.hermes/skills/knowledge/book-to-hermes-skill.backup-<timestamp> \
  ~/.hermes/skills/knowledge/book-to-hermes-skill
```

## Dangerous Changes to Avoid

- Adding `pip install` or `apt install` to scripts
- Adding network requests
- Adding LLM API calls
- Removing element decomposing in HTML/EPUB extractors
- Allowing full text injection into SKILL.md
- Mixing system Python with venv packages
- Defaulting `--allow-overwrite` to `yes`

## Bilingual Glossary Review and Write-Back

### When to Use

- Same article/book exists in both English and Chinese
- Terminology alignment is needed
- Translation quality requires human review
- Cross-referencing between language versions

### Workflow

1. **Generate bilingual glossary v1** (Phase 1-g)
   - Extract terms from both skills
   - Classify confidence: high / medium / low / missing
   - Document chapter gaps

2. **Fix source if chapter gap** (Phase 1-h / 1-i)
   - Search for complete source
   - Create patched copy if needed
   - Rebuild skill and re-evaluate

3. **Generate bilingual glossary v2** (Phase 1-j)
   - Re-evaluate after any rebuild
   - Update statistics

4. **Generate review packet** (Phase 1-k)
   - Flag low-confidence terms
   - Present evidence and recommendations
   - User makes decisions

5. **Apply decisions and v3** (Phase 1-l)
   - Log user decisions
   - Update glossary with accepted/revised terms

6. **Safe write-back** (Phase 1-m)
   - Backup both skills
   - Append to glossary.md only
   - Validate after write-back

### Input

- English skill path
- Chinese skill path
- English glossary
- Chinese glossary
- chapters/

### Output

- Bilingual glossary (v1/v2/v3)
- Diff summary
- Review packet
- User decision log
- Write-back report

### Must Confirm Before Write-Back

- User has reviewed all flagged terms
- Accepted terms list is finalized
- Rejected terms will not be written back
- Both skills are backed up

### Write-Back Rules

- Only modify glossary.md
- Do not modify SKILL.md, chapters/, metadata.json
- Append user-reviewed section, do not overwrite original glossary
- Always validate after write-back
- Do not write back unreviewed terms

### Related Files

- Workflow: `references/bilingual_glossary_workflow.md`
- Review packet template: `templates/bilingual_glossary_review_packet_template.md`
- Write-back template: `templates/bilingual_glossary_writeback_template.md`

### Not Recommended for Automation

- User review decisions require human judgment
- Translation quality cannot be fully automated
- Source-specific context matters

## Health Checks

```bash
# Check venv exists
ls ~/.hermes/venvs/book-to-hermes-skill/bin/python

# Check dependencies
~/.hermes/venvs/book-to-hermes-skill/bin/python -c "import docx, ebooklib, bs4; print('OK')"

# Check scripts are executable
python3 ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/extract_text.py --help 2>&1 | head -1
python3 ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/build_book_skill.py --help 2>&1 | head -1
python3 ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/validate_book_skill.py --help 2>&1 | head -1
```
