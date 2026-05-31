# Source Document Structure Repair

## When to Use

When a source document (typically PDF-converted HTML) has chapter content embedded in non-heading elements (e.g., `<li>`, `<p>`) instead of proper `<h2>` headings, causing the chapter splitter to miss sections.

## Symptoms

- Skill has fewer chapters than expected
- "Missing chapter" reports from bilingual comparison
- Key terms present in source HTML but absent from skill chapters
- Source HTML has content like: `<li><p>1.3 Chapter Title ...</p></li>` instead of `<h2>1.3 Chapter Title</h2>`

## Diagnostic Checklist

1. **Check source h2 headings**: `grep -n "<h2" source.html`
2. **Search for "missing" content**: `grep -n "key_term" source.html`
3. **Check if content is embedded in list items**: `grep -n "<li.*1\.3\|<li.*chapter" source.html`
4. **Compare with alternative language source**: `grep -n "<h2" english_source.html`
5. **Check all alternative sources**: Search `~/.hermes/workspace/`, `~/Downloads/`, `~/Documents/`

## Repair Strategy

### Case A: `<li>` contains only title

```html
<!-- Before -->
<li><p>1.3 Chapter Title</p></li>

<!-- After -->
<h2>1.3 Chapter Title</h2>
```

### Case B: `<li>` contains title + body (most common)

```html
<!-- Before -->
<li><p>1.3 Chapter Title Body paragraph text...</p></li>

<!-- After -->
<h2>1.3 Chapter Title</h2>
<p>Body paragraph text...</p>
```

### Case C: Structure uncertain

Do not auto-fix. Report PARTIAL and request manual review.

## Repair Procedure

1. **Create patched copy** (never modify original):
   ```bash
   cp source.html source.phase1i_patched.html
   ```

2. **Apply sed replacement**:
   ```bash
   sed -i 's|<li><p>1\.3 Chapter Title Body text...</p></li>|<h2>1.3 Chapter Title</h2>\n<p>Body text...</p>|' source.phase1i_patched.html
   ```

3. **Verify patched file**:
   ```bash
   grep -n "<h2" source.phase1i_patched.html  # Should show new h2
   grep -n "key_term" source.phase1i_patched.html  # Content preserved
   ```

4. **Regenerate skill from patched source**:
   ```bash
   python build_book_skill.py --source source.phase1i_patched.html --slug ... --allow-overwrite yes
   ```

5. **Clean up duplicate chapters**: The new chapter may shift numbering, creating duplicate filenames. Remove duplicates manually:
   ```bash
   # Keep only the chapters referenced in SKILL.md
   rm chapters/ch05-14-duplicate.md  # etc.
   ```

6. **Re-run validate**:
   ```bash
   python validate_book_skill.py --skill-dir ~/.hermes/skills/books/<slug>
   ```

## Verification

- New chapter appears in SKILL.md chapter index
- New chapter file exists in `chapters/`
- Key terms from the "missing" section are now in the skill
- Validate PASS
- No duplicate chapter files

## Example: The Artist Is Dead Chinese 1.3

**Original structure**:
```html
<ul>
<li><p>1.3 三、单向度的代价：关系层的消失 三种制度消灭余项是前台的暴力。关系层的消失是后台的塌方。</p></li>
</ul>
```

**Patched structure**:
```html
<ul>
<h2>1.3 三、单向度的代价：关系层的消失</h2>
<p>三种制度消灭余项是前台的暴力。关系层的消失是后台的塌方。</p>
</ul>
```

**Result**: 7 previously "missing" terms (沙龙, 赞助, 师徒, 画廊, 印象派, 立体主义, 超现实主义) became alignable.

## Safety Rules

- Never modify original source files
- Always create timestamped backups of existing skills before rebuild
- Verify original file is unchanged after patching
- Clean up duplicate chapter files after regeneration
- Document the fix in the Phase report
