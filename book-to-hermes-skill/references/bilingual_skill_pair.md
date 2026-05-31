# Bilingual Skill Pair Documentation

## When to Use

Generate bilingual skill pairs when the same document exists in multiple languages (e.g., English + Chinese versions of the same paper). This enables cross-language terminology lookup, translation quality review, and bilingual content generation.

## Workflow

1. Generate first language skill (e.g., English)
2. Generate second language skill (e.g., Chinese)
3. Compare chapter structures — note source-level differences (missing chapters are expected)
4. Create bilingual pair documentation file
5. Document terminology cross-reference

## Bilingual Pair Documentation Template

```markdown
# [Title] — Bilingual Skill Pair

## English Skill
- Path: ~/.hermes/skills/books/[slug-en]/
- Slug: [slug-en]
- Chapters: N

## Chinese Skill
- Path: ~/.hermes/skills/books/[slug-zh]/
- Slug: [slug-zh]
- Chapters: N

## Chapter Comparison
| # | English | Chinese | Match |

## Key Terminology
| English | Chinese | Source |

## Hermes Usage
- Load individually: @[slug-en] or @[slug-zh]
- Compare: @[slug-en] @[slug-zh]
- Extract terms: "What are the Chinese equivalents of X, Y, Z?"
```

## Known Source-Level Differences

- Missing chapters: one language version may omit a chapter present in the other
- Different heading numbering: e.g., "1.1" vs "一、"
- Different term density: English may produce more glossary terms due to Title Case detection

## Acceptance Criteria

- Both skills validate PASS independently
- Chapter alignment table documents all differences
- At least 5 key terminology pairs documented
- Hermes usage patterns documented
