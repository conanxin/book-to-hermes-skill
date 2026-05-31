# Bilingual Glossary Review Packet Template

## Summary

- **Source glossary**: `{path_to_bilingual_glossary_v2}`
- **English skill**: `{path_to_en_skill}`
- **Chinese skill**: `{path_to_zh_skill}`
- **Generated at**: `{timestamp}`
- **Scope**: {N} low-confidence terms flagged for review

---

## Review Table

| # | English Term | Current Chinese Candidate | Suggested Preferred Chinese | Confidence Before Review | Issue Type | Risk | Recommendation | Evidence Summary | User Decision | Write Back | Notes |
|---|--------------|--------------------------|----------------------------|--------------------------|------------|------|----------------|------------------|---------------|------------|-------|
| 1 | | | | | | | | | | | |
| 2 | | | | | | | | | | | |
| 3 | | | | | | | | | | | |

---

## Issue Types

- **direct_match**: Exact translation found in both skills
- **indirect_match**: Related concept but not exact match
- **missing_in_skill**: Not found in target skill
- **source_html_only**: In source HTML but not extracted to skill
- **translation_not_explicit**: Concept exists but translation not explicit
- **person_name**: Proper name; may keep original
- **concept_normalization**: Multiple variants found; needs preferred form
- **needs_user_decision**: Requires human judgment

## Risk Levels

- **low**: Minor impact; standard translation exists
- **medium**: May affect understanding; needs context check
- **high**: Core concept; wrong translation changes meaning

## Recommendations

- **accept**: Use suggested translation
- **accept_with_note**: Use suggested translation but add note
- **revise_translation**: Use user-specified translation
- **keep_english**: Keep English term, add Chinese annotation
- **mark_missing**: Leave as missing
- **do_not_write_back**: Reject; do not add
- **needs_manual_review**: Defer to later

---

## User Decision Checklist

- [ ] Term 1 → Accept / Revise / Reject / Defer
- [ ] Term 2 → Accept / Revise / Reject / Defer
- [ ] Term 3 → Accept / Revise / Reject / Defer

---

## Decision Rules

1. Do not fabricate translations not in source
2. If Chinese skill has no explicit equivalent, mark as missing or suggested only
3. Person names: keep original English unless Chinese skill has established phonetic translation
4. Standard art terms: use established Chinese translations
5. Source-specific terms: follow source wording even if non-standard
6. When in doubt: mark as needs_manual_review

---

## Post-Review Actions

1. Log all decisions in user decision log
2. Update bilingual glossary v3 with decisions
3. Separate accepted/revised terms from rejected/missing terms
4. Prepare write-back list (only accepted + revised)
5. Generate write-back report
