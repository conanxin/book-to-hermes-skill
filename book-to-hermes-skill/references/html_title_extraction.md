# HTML Title / Chapter Title Extraction (Phase 1-b)

## Problem

HTML documents converted from PDF often have the original filename in the `<title>` tag (e.g., `art_history.pdf`). The extractor produces `# art_history.pdf` as the first heading, which becomes the chapter title.

## Solution: `_looks_like_filename()`

Three detection patterns:

1. **File extension ending**: `\.(pdf|html|htm|docx|epub|txt|md)$` (case-insensitive)
2. **Filename character set**: `^[A-Za-z0-9_\-\.]+$` — no spaces, only filename-safe chars
3. **Underscore-separated stem**: `_` present, no spaces, 2+ underscore-separated parts

## Integration Points

### `guess_title()` (extract_text.py)

Priority order for title detection:
1. First `# ` heading that does NOT look like filename
2. If first heading IS filename-like, try second heading
3. First non-empty line that doesn't look like filename
4. Filename stem (last resort)

### `split_into_chapters()` (build_book_skill.py)

Tracks `seen_real_title` flag. For first `h1` heading:
- If filename-like: set as `current_title` but don't flush chapter, keep `seen_real_title = False`
- If not filename-like: set as `current_title`, mark `seen_real_title = True`

This prevents filename-like titles from creating spurious ch01 entries.

## Verification

After generation, always check:
```bash
head -1 ~/.hermes/skills/books/<slug>/chapters/ch01-*.md
# Should NOT end with .pdf, .html, etc.
# Should NOT be underscore-separated like "art_history"
```

## Edge Cases

1. **Document with no real title**: If ALL headings look like filenames, falls back to filename stem. Acceptable — indicates poor source document.
2. **Mixed filename + real title**: HTML has both `# art_history.pdf` and `# Art as an End in Itself`. Solution skips filename, uses real title.
3. **Legitimate title with underscore**: Rare for document titles. If encountered, pass `--title` explicitly.
