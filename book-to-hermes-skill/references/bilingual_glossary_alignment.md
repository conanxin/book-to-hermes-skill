# Bilingual Glossary Alignment Methodology

## When to Use

When the same source document has been converted into Hermes skills in multiple languages (e.g., English + Chinese), and you need to align terminology, document translation fidelity, and identify structural gaps.

## Prerequisites

- Two or more skill directories for the same document in different languages
- Skills have been validated (PASS)
- You have read access to both skill directories
- No LLM or network access needed — this is a local, rule-based process

## Workflow

### Step 1: Inventory Both Skills

```bash
# List chapters
ls ~/.hermes/skills/books/<slug>-en/chapters/
ls ~/.hermes/skills/books/<slug>-zh/chapters/

# Count glossary terms
grep -c "^- \*\*" ~/.hermes/skills/books/<slug>-en/glossary.md
grep -c "^- \*\*" ~/.hermes/skills/books/<slug>-zh/glossary.md

# Compare chapter counts
ls ~/.hermes/skills/books/<slug>-en/chapters/ | wc -l
ls ~/.hermes/skills/books/<slug>-zh/chapters/ | wc -l
```

### Step 2: Extract Key Terms from English Glossary

Read `glossary.md` and identify:
- Named concepts (e.g., Zombie Formalism, Debt Aesthetics)
- Person names (e.g., Walter Robinson, Hito Steyerl)
- Core framework terms (e.g., remainder, relational layer, colonization)
- Academic concepts (e.g., optimizability, institutional critique)

### Step 3: Search for Chinese Equivalents

For each English term, search the Chinese skill:

```bash
# Search across all Chinese skill files
ZH_DIR=~/.hermes/skills/books/<slug>-zh
grep -rn "僵尸形式主义" "$ZH_DIR" || echo "NOT FOUND"
grep -rn "债务美学" "$ZH_DIR" || echo "NOT FOUND"
grep -rn "余项" "$ZH_DIR" | head -3
```

Search strategy:
1. Exact translation (e.g., Zombie Formalism → 僵尸形式主义)
2. Partial match (e.g., remainder → 余项位置 / 余项空间)
3. Context search (search the chapter that corresponds to the English chapter)
4. Character-level match (e.g., 单向度 for One-Dimensionality)

### Step 4: Classify Confidence

| Confidence | Criteria |
|------------|----------|
| **High** | Exact translation found in corresponding chapter/glossary; context matches |
| **Medium** | Semantic match with positional/contextual variation; root match |
| **Low** | Inferred or partial match; may need manual verification |
| **Missing** | Not found in Chinese skill at all |

### Step 5: Document Chapter Gaps

Compare chapter structures:

| # | English Chapter | Chinese Chapter | Match |
|---|-----------------|-----------------|-------|
| 1 | ch01-title-en | ch01-title-zh | ✓ / ✗ |

Note any missing chapters. For each missing chapter, list the terms that cannot be aligned.

### Step 6: Create Bilingual Glossary File

Output: `THE_ARTIST_IS_DEAD_BILINGUAL_GLOSSARY.md` (or similar)

Sections:
1. Summary (skill paths, generation method, known issues)
2. High Confidence Terms (table with English, Chinese, type, evidence)
3. Medium Confidence Terms
4. Low Confidence / Needs Review
5. Missing in Chinese Version
6. Inconsistent / Needs Normalization
7. Suggested Preferred Translation Table
8. Chapter Gap Impact

### Step 7: Create Pair Documentation

Output: `THE_ARTIST_IS_DEAD_BILINGUAL_SKILL_PAIR.md`

Sections:
1. English skill path
2. Chinese skill path
3. Source document paths
4. Chapter structure comparison table
5. Recommended Hermes usage patterns
6. Future enhancements

## Hermes Usage Patterns

### Load Individual Skills
```
@the-artist-is-dead-en
```

### Compare Structures
```
@the-artist-is-dead-en @the-artist-is-dead-zh
Which chapter is missing in the Chinese version?
```

### Extract Terminology
```
@the-artist-is-dead-en @the-artist-is-dead-zh
What are the Chinese equivalents of Zombie Formalism, Debt Aesthetics, Duty Free Art?
```

### Check Translation Fidelity
```
@the-artist-is-dead-en @the-artist-is-dead-zh
Compare the extractive summaries of chapter 5 in both versions. Are the key arguments preserved?
```

## Known Pitfalls

- **Chapter gaps**: Source documents may have structural differences (e.g., Chinese version missing a chapter). This is a source-level issue, not a generation error. Document it, don't try to fix by regenerating unless the user requests.
- **Glossary size asymmetry**: English skills often have more glossary terms than Chinese skills because English academic papers use Title Case for concepts. Chinese skills may only capture bold/code terms. This is expected.
- **Person name retention**: Chinese skills often keep English person names (Walter Robinson, Chris Wiley) rather than phonetic translation. This is correct — do not suggest "fixing" it.
- **Title Case false positives**: English glossary may contain false positives like "Killer Han Qin" or "End Applied Series This". These are extraction artifacts. Mark them as low-confidence, don't treat them as real terms.
- **Framework abbreviations**: SAE, DD-level, etc. are often kept as-is in both languages. Do not force translation.
- **Source HTML structure loss**: PDF-to-HTML conversion may lose heading structure, embedding chapter markers inside `<li>` elements instead of `<h2>`. This causes the chapter splitter to miss the chapter entirely. See "Source Structure Repair" below.
- **Glossary terms in list items**: Terms embedded in `<li>` elements within conclusions or appendices may not be extracted to skill chapters even though they exist in the source. These remain "missing" at the skill level but are present in the source HTML.

## Source Structure Repair (Phase 1-i)

When a chapter appears missing from one language version but the source HTML contains the content, the issue is often structural — not content loss.

### Diagnostic Checklist

1. Check source HTML for chapter content: `grep -n "1.3\|沙龙\|赞助" source.html`
2. Check if content is inside `<li>` instead of `<h2>`: `grep -n "<li>.*1\.3" source.html`
3. Check generated skill chapters: `ls chapters/ | grep "1.3"`
4. Compare with other language skill: `ls other-skill/chapters/ | grep "1.3"`

### Repair Procedure

**Step 1: Create patched copy** (never modify original)
```bash
ORIG=source.html
PATCHED="${ORIG}.phase1i_patched.html"
cp "$ORIG" "$PATCHED"
```

**Step 2: Classify the `<li>` structure**

| Case | Pattern | Fix |
|------|---------|-----|
| A | `<li>1.3 Title only</li>` | Replace with `<h2>1.3 Title</h2>` |
| B | `<li><p>1.3 Title + body text</p></li>` | Split: `<h2>1.3 Title</h2><p>body text</p>` |
| C | Complex nested structure | Manual edit or abort with PARTIAL |

**Step 3: Apply fix with sed**
```bash
# Case B example: title + body in same <li>
sed -i 's|<li><p>\(1\.3 [^<]*\)</p>|<h2>\1</h2>|' "$PATCHED"
```

**Step 4: Verify patched HTML**
```bash
grep -n "<h2>.*1\.3" "$PATCHED"          # Confirm h2 exists
grep -c "沙龙\|赞助\|师徒" "$PATCHED"   # Confirm content preserved
ls -la "$ORIG" "$PATCHED"               # Confirm original unchanged
```

**Step 5: Regenerate skill from patched source**
```bash
python build_book_skill.py \
  --source "$PATCHED" \
  --slug the-artist-is-dead-zh \
  --title "艺术家已死" \
  --language zh --mode article \
  --output-dir ~/.hermes/skills/books \
  --allow-overwrite yes
```

**Step 6: Clean duplicate chapter files**
Adding a new chapter may shift numbering and create duplicate filenames (e.g., `ch04-14` and `ch05-14` both for 1.4). Remove duplicates, keeping the file referenced in SKILL.md.

**Step 7: Validate and compare**
- Run `validate_book_skill.py`
- Compare old vs new: chapter count, SKILL.md size, glossary terms
- Check if previously missing terms are now in chapters

### Impact on Bilingual Glossary

After source structure repair:
- Re-run term searches against the regenerated skill
- Upgrade terms from "missing" to "high/medium" if now found in chapters
- Update the bilingual glossary with new confidence levels
- Document the repair in the glossary's "Chapter Gap Impact" section

## Statistics Template

| Category | Count | Description |
|----------|-------|-------------|
| High confidence | N | Exact or near-exact match |
| Medium confidence | N | Semantic match with variation |
| Low confidence | N | Inferred or partial match |
| Missing | N | Present in English, absent in Chinese |
| Inconsistent | N | Multiple variants found |
| **Total** | **N** | |

## Example: The Artist Is Dead

### Phase 1-g (Initial Alignment)

- High confidence: 40 terms (Zombie Formalism → 僵尸形式主义, Debt Aesthetics → 债务美学, etc.)
- Medium confidence: 18 terms (speculation → 投机, price signal → 价格信号, etc.)
- Low confidence: 20 terms (artist as brand, post-internet art, wabi-sabi, etc.)
- Missing: 16 terms (Ulay, wabi-sabi, gallery as institution, etc.)
- Chapter gap: Chinese version lacks chapter 1.3, affecting 12+ term alignments

### Phase 1-i (Source Structure Repair)

**Root cause**: Chinese source HTML had 1.3 content embedded in a `<li>` element inside 1.2, not as a separate `<h2>`.

**Fix**: Created `艺术家已死_中文.html.phase1i_patched.html`, converted `<li><p>1.3 Title + body</p></li>` to `<h2>1.3 Title</h2><p>body</p>`, regenerated skill.

**Result**: Chinese skill now has 8 chapters (was 7). 1.3 chapter present.

### Phase 1-j (Glossary Regeneration)

**Upgraded terms (7)**: salons → 沙龙, patronage → 赞助, master-apprentice → 师徒传承, gallery → 画廊, impressionist → 印象派, cubist → 立体主义, surrealist → 超现实主义 — all moved from "missing" to "high confidence".

**Still missing (2)**: Wabi-sabi → 侘寂, Ulay → Ulay/乌雷 — these are in source HTML conclusion list items but not extracted to skill chapters. Low impact.

**Statistics change**: High 40→47, Medium 18→24, Low 20→14, Missing 16→14.

### Key Lesson

A "missing chapter" report should trigger source structure diagnosis FIRST, not regeneration from the same source. The content was always there — only the heading structure was broken.
