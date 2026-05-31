# Bilingual Glossary Review and Write-Back Workflow

## Applicability

Use this workflow when:
- A single article/book exists in both English and Chinese
- Terminology alignment between the two languages is needed
- Translation quality needs human review
- Bilingual writing or cross-referencing is required

## Inputs

| Item | Path Pattern |
|------|-------------|
| English skill | `~/.hermes/skills/books/{slug}-en/` |
| Chinese skill | `~/.hermes/skills/books/{slug}-zh/` |
| English glossary | `{en-skill}/glossary.md` |
| Chinese glossary | `{zh-skill}/glossary.md` |
| Chapter files | `{skill}/chapters/*.md` |

## Outputs

| Artifact | Path Pattern |
|----------|-------------|
| Bilingual glossary v1 | `~/.hermes/workspace/reports/book_to_skill/{TITLE}_BILINGUAL_GLOSSARY.md` |
| Bilingual glossary v2 | `{TITLE}_BILINGUAL_GLOSSARY_V2.md` |
| Bilingual glossary v3 | `{TITLE}_BILINGUAL_GLOSSARY_V3.md` |
| Diff summary | `{TITLE}_BILINGUAL_GLOSSARY_V2_DIFF_SUMMARY.md` |
| Review packet | `{TITLE}_BILINGUAL_GLOSSARY_REVIEW_PACKET.md` |
| User decision log | `{TITLE}_BILINGUAL_GLOSSARY_USER_DECISIONS.md` |
| Write-back report | `HERMES_BOOK_TO_SKILL_PHASE1M_WRITE_BACK_REVIEWED_GLOSSARY_REPORT.md` |

## Workflow Phases

### Phase 1-g: Bilingual Glossary v1
- Extract terms from both skill glossaries and chapters
- Classify confidence: high / medium / low / missing
- Document chapter gaps
- Build preferred translation table
- Purely local rule-based; no LLM or network

### Phase 1-h: Source Diagnostics (if chapter gap found)
- Check if Chinese source is missing chapters
- Search for complete alternative sources
- If found: create patched copy, rebuild skill
- If not found: document gap, do not translate

### Phase 1-i: Source Patch and Rebuild (if applicable)
- Create patched copy of source HTML
- Fix structural issues (e.g., `<li>` → `<h2>` for chapter markers)
- Rebuild Chinese skill from patched source
- Validate rebuilt skill
- Re-evaluate bilingual glossary impact

### Phase 1-j: Bilingual Glossary v2
- Re-read both skills after any rebuild
- Re-evaluate terms previously marked as missing
- Upgrade confidence where evidence now exists
- Update statistics and diff summary

### Phase 1-k: Review Packet
- Generate review packet for low-confidence terms
- Each term gets: evidence, risk, recommendation
- User reviews and makes decisions
- Decisions logged for traceability

### Phase 1-l: User Decisions and v3
- Apply user decisions to glossary
- Accepted terms → upgrade to high/medium
- Revised terms → update with user-specified translation
- Rejected terms → mark do_not_write_back
- Generate v3 glossary and decision log

### Phase 1-m: Safe Write-Back
- Backup both skills
- Append user-reviewed terms to glossary.md only
- Do not modify SKILL.md, chapters/, or metadata
- Validate both skills after write-back
- Check forbidden terms were not added

### Phase 1-n: Workflow Template
- Document the complete workflow
- Create reusable templates
- Update MAINTENANCE.md and TEST_MATRIX.md
- Check GitHub export freshness

## Confidence Rules

| Level | Criteria |
|-------|----------|
| **high** | Exact translation in same context; chapter title match; named concept with evidence in both skills |
| **medium** | Semantic match but position/context differs; related concept; abbreviation match |
| **low** | Only implied; not explicit; source has it but skill extraction missed; needs user confirmation |
| **missing** | Not found in target skill; source may have it but not extracted |
| **do_not_write_back** | User rejected; insufficient evidence; not in source; external concept |

## Write-Back Principles

1. **Only write user-confirmed terms** — never write back terms the user has not explicitly approved
2. **Do not write back insufficient-evidence terms** — mark as missing or suggested only
3. **Do not overwrite original glossary** — append a new "User-Reviewed Bilingual Terms" section
4. **Only modify glossary.md** — never touch SKILL.md, chapters/, or metadata.json
5. **Always backup before write-back** — create timestamped backup of both skills
6. **Always validate after write-back** — run validate_book_skill.py on both skills
7. **Check forbidden terms** — verify rejected terms were not accidentally added

## Safety Boundaries

- No network access
- No LLM calls for translation or enrichment
- No automatic translation of missing chapters
- No modification of source documents
- No write-back of unreviewed terms
- No overwrite of original glossary content
- No modification of chapters or SKILL.md

## Decision Types

| Decision | Action | Write Back |
|----------|--------|------------|
| accept | Use suggested translation | yes |
| revise_translation | Use user-specified translation | yes |
| keep_english | Keep English term, add Chinese note | yes |
| mark_missing | Leave as missing | no |
| do_not_write_back | Reject; do not add to glossary | no |
| needs_more_context | Defer to later review | no |

## Related Files

- Review packet template: `../templates/bilingual_glossary_review_packet_template.md`
- Write-back template: `../templates/bilingual_glossary_writeback_template.md`
- User decision log template: see `../templates/`
