# English Academic Term Extraction (Phase 1-b)

## Problem

English academic papers (especially humanities/philosophy) use italics and Title Case for key concepts, not `**bold**` or `` `code` `` markers. The original Chinese-focused term extractor produced empty glossaries for English documents.

## Solution Architecture

### 1. `_is_quality_english_term(t, source_type, freq)`

Multi-layer quality gate for English terms:

| Check | Rule |
|-------|------|
| Length | 3-60 chars |
| Word count | 1-4 words |
| Single word | >= 5 letters, alphabetic only, not in stop list |
| Multi-word | each word >= 2 chars (except articles/prepositions) |
| Version numbers | reject `v?\d+(\.\d+)*` |
| Pure numbers | reject `^\d+$` |
| Pure symbols | reject `^[^\w\-]+$` |
| Shell commands | reject via `_is_shell_command_term()` |
| Status symbols | reject via `_has_status_symbol()` |
| URLs | reject if contains `http`, `www.`, `.com` |
| File extensions | reject if ends with `.pdf`, `.html`, `.docx`, etc. |

### 2. Academic Concept Hardcoded List

```python
_ENGLISH_ACADEMIC_CONCEPTS = frozenset([
    "integrity", "generativity", "colonization", "cultivation",
    "autonomy", "instrumentalization", "non-instrumentality",
    "aesthetics", "agency", "practice", "form", "meaning",
    "value", "tradition", "medium", "subject", "object",
    "relation", "axis", "structure", "self", "world",
])
```

These get priority 0 in glossary sorting and bypass frequency checks.

### 3. Title Case Detection

Regex: `\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b`

**Context filtering** (critical for avoiding false positives):
- Skip if preceded by lowercase letter (mid-sentence)
- Skip if followed by lowercase letter (mid-sentence)
- Skip if starts with common sentence starter: The, This, That, These, Those, There, Their, They, Then, Than
- Skip if all words are function words

### 4. Hyphenated Concepts

Regex: `\b([a-z]+-[a-z]+(?:-[a-z]+)*)\b` (case-insensitive)

Catches: `non-instrumentality`, `self-as-an-end`, `cross-layer`

### 5. Extractive Explanations

For each glossary term, search chapter text for sentences containing the term. Use the first sentence >20 chars as the explanation. Truncate to 200 chars. Fallback: "Appears in source; definition requires manual enrichment."

### 6. Stop Words

```python
_ENGLISH_STOP_WORDS = frozenset([
    "the", "and", "or", "but", "with", "without", "from", "into",
    "about", "for", "chapter", "section", "page", "figure", "table",
    "pdf", "html", "file", "document", "text", "source", "output",
    "result", "status",
])
```

## Glossary Sorting Priority

| Priority | Source |
|----------|--------|
| 0 | Academic concept list |
| 1 | Title Case phrase |
| 2 | Bold/code term |
| 3 | Everything else |

## Known Limitations

1. **"Autonomy" not extracted**: Appears in source but frequency < 2 and not in Title Case. Would need manual addition or LLM enrichment.
2. **"Art as End in Itself" not extracted**: 5-word phrase exceeds 4-word limit. Would need special handling for book titles.
3. **Generic terms included**: "history", "model", "theory" appear because they're frequent academic words. Acceptable noise level for extractive generation.
4. **Title Case false positives**: "Han Qin Self" from author line appears in ch01. Minor issue — only affects first chapter.

## Testing

Verify glossary quality:
```bash
grep -c "^- \*\*" ~/.hermes/skills/books/<slug>/glossary.md
# Should be 10-40 for English academic papers

# Check for core concepts
for term in "Integrity" "Generativity" "Colonization" "Cultivation" "Non-instrumentality"; do
  grep -i "$term" ~/.hermes/skills/books/<slug>/glossary.md && echo "  ✓ $term" || echo "  ✗ $term"
done
```
