# Markdown Table Normalization

Convert Markdown tables into readable bullets for extractive summaries and key points.

## Problem

Raw Markdown tables pasted into summaries produce unreadable walls of `|` characters. Key Points derived from tables inherit the same noise.

## Solution: `table_to_bullets()`

Implemented in `build_book_skill.py` (Phase 0-e).

### Detection

A table block must satisfy:
1. At least 2 consecutive lines containing `|`
2. Second line matches separator pattern: `^\s*\|?[\s\-:]+\|`
3. Header line yields at least 1 non-empty column name

### Conversion Rules

1. **Header → field names**: split on `|`, strip whitespace, drop empties
2. **Row → bullet**: for each non-empty cell, emit `field: value`
3. **Skip sparse rows**: if a row has fewer than 2 non-empty cells, skip it
4. **Truncate long cells**: max 80 chars per cell value; append `...` if truncated
5. **Skip separator lines**: do not emit bullets for `|---|---|` lines

### Example

**Input table**:
```markdown
| 检查项 | 状态 | 说明 |
|--------|------|------|
| pnpm install | ✅ 成功 | ~21.6s |
| apt install | 未执行 | 零修改系统 |
```

**Output bullets**:
```
- 检查项: pnpm install; 状态: ✅ 成功; 说明: ~21.6s
- 检查项: apt install; 状态: 未执行; 说明: 零修改系统
```

### Integration Points

- `extract_summary()`: detects tables in first 3 paragraphs, converts top 3 rows to bullets, prepends notice: "This section includes a Markdown table. Key rows were normalized into readable bullets."
- `extract_key_points()`: calls `table_to_bullets()` first, falls back to list items / sentences

### Known Limitations

- Tables without blank-line separation from preceding text may be missed
- Nested tables (tables inside table cells) are not supported
- Multi-line cell content is truncated at first newline

## Verification

```bash
python3 ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/build_book_skill.py \
  --source /path/to/doc-with-tables.md --slug table-test --mode technical \
  --output-dir ~/.hermes/skills/books --allow-overwrite yes

grep -A2 "Markdown table" ~/.hermes/skills/books/table-test/chapters/ch*.md
```
