# Format Detection Pitfalls

Session-tested bugs and fixes related to format detection in extract_text.py.

## Phase 0-i: EPUB Misidentified as DOCX (2026-05-31)

**Symptom**: `extract_text.py` returns `"format": "docx"` for `.epub` files, causing the DOCX extractor to fail with a corrupted-file error.

**Root Cause**: `SUPPORTED_EXTENSIONS` did not include `.epub`. The `detect_format()` function fell through to magic-bytes detection, which saw the ZIP header (`PK`) and defaulted to `docx` (comment in code: "Simplified; EPUB detection would need more").

**Fix**: Three changes:
1. Add `.epub` to `SUPPORTED_EXTENSIONS`
2. Prioritize extension over magic bytes: check `Path(input_path).suffix.lower()` first
3. For extensionless files with ZIP header, return `""` (unknown) rather than guessing `docx`

**Verification**:
```bash
python3 ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/extract_text.py \
  test.epub | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['format'] == 'epub'"
```

**Lesson**: Extension-based detection must be exhaustive. Magic-bytes fallback should not guess between ambiguous formats (ZIP containers: DOCX, EPUB, ODT, XLSX, etc.). When ambiguous, return unknown and let the user specify.

## Phase 0-i: Venv Dependency Chain Incomplete (2026-05-31)

**Symptom**: After installing `ebooklib` in the isolated venv, EPUB extraction still failed with `ModuleNotFoundError: No module named 'bs4'`.

**Root Cause**: The EPUB extractor uses `BeautifulSoup` to parse XHTML chapters. `ebooklib` alone is insufficient; `beautifulsoup4` is also required. The dependency audit only checked `ebooklib`.

**Fix**: Install both dependencies together:
```bash
~/.hermes/venvs/book-to-hermes-skill/bin/python -m pip install ebooklib beautifulsoup4
```

**Lesson**: When adding format support, trace the complete dependency chain. The primary library (ebooklib) often has secondary dependencies (bs4 for HTML parsing) that are not automatically installed if the primary library doesn't declare them as required.

**Pre-flight checklist for new format support**:
1. Identify primary extractor library
2. Identify all imports in the extractor code path
3. Check each import in the target venv BEFORE writing extractor code
4. Install missing dependencies before first test
5. Document complete dependency list in `references/supported_formats.md`
