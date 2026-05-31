# Source Structure Diagnostics — Case Study: The Artist Is Dead Chinese Chapter Gap

**Phase**: 1-h
**Date**: 2026-05-31
**Skill**: book-to-hermes-skill
**Document**: The Artist Is Dead (Chinese version)

---

## Problem Statement

The Chinese skill (`the-artist-is-dead-zh`) appeared to be missing chapter 1.3 ("The Cost of One-Dimensionality: The Disappearance of the Relational Layer"). The English skill had 8 chapters; the Chinese skill had 7. This caused 12+ terms to be marked as "missing in Chinese" in the bilingual glossary.

## Diagnostic Steps

### Step 1: Check Current Skill Structure

```bash
ls ~/.hermes/skills/books/the-artist-is-dead-zh/chapters/
# Output: 7 files (ch01 through ch07)
# Missing: ch04-equivalent (1.3)
```

### Step 2: Check Source HTML h2 Headings

```bash
grep -n "<h2" ~/.hermes/workspace/.../artist_is_dead_zh/艺术家已死_中文.html
```

**Result**: Only 6 h2 headings found:
```
1.1 一、单向度的文明
1.2 二、单向度在市场、学院、算法中的投射
1.4 四、AI：一体两面
1.5 五、死亡报告
1.7 七、非平凡预测
1.8 八、结语
```

No `<h2>` for 1.3.

### Step 3: Search for "Missing" Content in Source

```bash
grep -n "沙龙\|赞助\|师徒\|侘寂\|Ulay\|画廊\|印象派\|立体主义\|超现实" source.html
```

**Result**: ALL terms found in source HTML:
- 沙龙: 4 occurrences
- 赞助: 4 occurrences
- 师徒: 4 occurrences
- 侘寂: 1 occurrence
- Ulay: 1 occurrence
- 画廊: 5 occurrences
- 印象派: 2 occurrences
- 立体主义: 1 occurrence
- 超现实主义: 1 occurrence

### Step 4: Locate the Content Structure

```bash
sed -n '38,100p' source.html | grep -n "<h2\|<li\|1.3\|沙龙\|师徒"
```

**Result**: The 1.3 content is embedded as a `<li>` inside the 1.2 section:
```html
<li><p>1.3 三、单向度的代价：关系层的消失 ...</p></li>
```

### Step 5: Compare with English Source

```bash
grep -n "<h2" english_source.html
```

**Result**: English source has proper `<h2>` for 1.3:
```html
<h2>1.3 3. The Cost of One-Dimensionality...</h2>
```

### Step 6: Check Alternative Sources

Searched `~/.hermes/workspace/`, `~/Downloads/`, `~/Documents/` for alternative Chinese sources with proper h2 structure.

**Result**: No alternative source found with `<h2>` for 1.3. All versions (pdf-to-markdown output, staging, publish-candidate) had the same structure.

## Root Cause

The Chinese source HTML was converted from PDF. During conversion, the heading structure was lost:
- English source: `<h2>1.3 ...</h2>` (preserved)
- Chinese source: `<li><p>1.3 ...</p></li>` (heading degraded to list item)

The chapter splitter (`split_into_chapters()`) only splits on `<h2>` elements. Since 1.3 is not an `<h2>`, it becomes part of the 1.2 chapter (ch03 in the skill).

The extractive summary for ch03 includes a single key point about 1.3 but does not extract all the detailed content (salons, patronage, master-apprentice, etc.) into the skill chapter file.

## Impact Assessment

| Term | Source HTML | Skill Chapter | Bilingual Status |
|------|-------------|---------------|------------------|
| 沙龙 (salons) | ✓ | Key point only | now_alignable |
| 赞助 (patronage) | ✓ | ch02 only | now_alignable |
| 师徒 (master-apprentice) | ✓ | ✗ | still_missing |
| 侘寂 (wabi-sabi) | ✓ | ✗ | still_missing |
| Ulay | ✓ | ✗ | still_missing |
| 画廊 (gallery) | ✓ | ✗ | still_missing |
| 印象派 (impressionist) | ✓ | ✗ | still_missing |
| 立体主义 (cubist) | ✓ | ✗ | still_missing |
| 超现实主义 (surrealist) | ✓ | ✗ | still_missing |

## Resolution Options

### Option A: Manual Source Fix (Recommended)

Edit the source HTML to add `<h2>` for 1.3:

```bash
# Before:
<li><p>1.3 三、单向度的代价：关系层的消失 ...</p></li>

# After:
<h2>1.3 三、单向度的代价：关系层的消失</h2>
<p>三种制度消灭余项是前台的暴力。关系层的消失是后台的塌方。</p>
```

Then regenerate the skill.

### Option B: Enhanced Chapter Splitter

Modify `split_into_chapters()` to recognize `<li>` elements containing chapter-like markers:

```python
# Pseudocode:
for li in soup.find_all('li'):
    text = li.get_text(strip=True)
    if re.match(r'^\d+\.\d+\s+[一二三四五六七八九十]+、', text):
        # Treat as chapter boundary
```

**Risk**: False positives from regular list items.

### Option C: Accept Current State

Document the limitation. The content is present in the source HTML; the skill is a reference, not a full copy. Users can load the source document directly if they need the full 1.3 content.

## Decision

**No rebuild performed.** The current source is the most complete version available. Rebuilding from the same source would produce the same result. The issue is source structure, not missing content.

## Lessons Learned

1. **"Missing chapter" ≠ "missing content"**: Always verify source HTML structure before concluding content is absent.
2. **PDF-to-HTML conversion loses headings**: This is a common source of chapter misalignment in bilingual skill pairs.
3. **Diagnostic checklist**: For any "missing chapter" report, always:
   - Check source h2 headings
   - Search for "missing" content in source
   - Check if content is embedded in another section
   - Compare with alternative language source
4. **Extractive summary limitation**: Even when content is in the source, the extractive summary may not capture all terms if the section is not properly bounded.

## Files

- Report: `~/.hermes/workspace/reports/book_to_skill/HERMES_BOOK_TO_SKILL_PHASE1H_REBUILD_ZH_SOURCE_REPORT.md`
- Backup: `~/.hermes/skills/books/the-artist-is-dead-zh.backup-phase1h-20260531-135837`
