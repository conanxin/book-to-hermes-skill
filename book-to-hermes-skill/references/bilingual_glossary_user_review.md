# Bilingual Glossary User Review Workflow

## When to Use

After generating an initial bilingual glossary (Phase 1-g), when low-confidence terms need human judgment before being written back into skill glossaries.

## Prerequisites

- Bilingual glossary v1 or v2 exists
- User has reviewed the glossary and identified terms needing decision
- No LLM or network access needed

## Workflow

### Step 1: Identify Terms Needing Review

From the bilingual glossary, extract terms marked as:
- `low confidence`
- `missing_in_zh` (or equivalent)
- `needs_review`

Target: 10-20 terms maximum per review session.

### Step 2: Generate Review Packet

Create a review packet with one entry per term:

| Field | Description |
|-------|-------------|
| English term | The source term |
| Current Chinese candidate | What's currently proposed (may be empty) |
| Suggested preferred Chinese | Agent's recommendation |
| Confidence before review | low / medium / high |
| English evidence | Max 30 words from source |
| Chinese evidence | Max 30 characters from source |
| Issue type | direct_match / indirect_match / missing_in_skill / source_html_only / translation_not_explicit / person_name / concept_normalization / needs_user_decision |
| Risk level | low / medium / high |
| Recommendation | accept / accept_with_note / revise_translation / keep_english / mark_missing / needs_manual_review |

### Step 3: User Decides

For each term, user selects one of:

| Decision | Meaning | Write Back? |
|----------|---------|-------------|
| `user_accepted` | Accept suggested translation as-is | Yes |
| `user_revised` | Accept but with modified translation | Yes, with user's version |
| `reject_write_back` | Term is not relevant to source; do not add | No |
| `do_not_write_back` | Insufficient evidence; defer | No |

### Step 4: Apply Decisions to Glossary v3

For each term:
- `user_accepted` → Move to High Confidence section, mark `user_accepted`
- `user_revised` → Move to appropriate section, mark `user_revised`, use user's preferred translation
- `reject_write_back` → Keep in Low Confidence with `do_not_write_back` note; do not upgrade
- `do_not_write_back` → Keep in Low Confidence with `do_not_write_back` note

### Step 5: Generate Decision Log

Create `BILINGUAL_GLOSSARY_USER_DECISIONS.md` documenting:
- Each term's decision
- Preferred Chinese (final)
- Whether to write back
- Reason

### Step 6: Update Main Glossary

- Backup old main glossary with timestamp
- Copy v3 to main glossary file
- Preserve versioned file (`BILINGUAL_GLOSSARY_V3.md`)

## Decision Patterns from The Artist Is Dead

### user_accepted (3 terms)

| Term | Chinese | Rationale |
|------|---------|-----------|
| AI art | AI 艺术 | Standard translation; low risk |
| Wabi-sabi | 侘寂 | Source HTML has it; extraction issue only |
| Ulay | Ulay（乌雷） | Keep original, add annotation |

### user_revised (1 term)

| Term | Standard | Source Context | Final |
|------|----------|----------------|-------|
| Artistic autonomy | 艺术自主性 | 自定方向 (self-direction) | 艺术自主性（文中语境：自定方向） |

Rationale: Standard translation differs from source wording. Use standard term in glossary but annotate with source context.

### reject_write_back (2 terms)

| Term | Reason |
|------|--------|
| Artist as brand | Not clearly present in source |
| Post-internet art | Not clearly present in source |

### do_not_write_back (6 terms)

| Term | Reason |
|------|--------|
| Auction | Insufficient evidence |
| Museum | Insufficient evidence / context-dependent |
| Cultural capital | Bourdieu concept; not in this paper |
| Financialization | Broader concept; not explicit |
| Institutional critique | Specific movement; not discussed |
| Contemporary art | Too broad / insufficient source-specific evidence |

## Key Rules

1. **Never claim a suggested translation is "the original"** if it's not in the source skill.
2. **Person names**: Keep original as primary. Add Chinese annotation in parentheses if available.
3. **Standard vs source wording**: When they differ, use standard term in glossary with source context note.
4. **Write-back scope**: Only write back terms that are explicitly in the source OR are standard translations of concepts clearly discussed.
5. **Future-proofing**: For rejected terms, record "preferred if future evidence appears" so they can be re-evaluated.

## Output Files

| File | Purpose |
|------|---------|
| `BILINGUAL_GLOSSARY_REVIEW_PACKET.md` | Terms presented to user for decision |
| `BILINGUAL_GLOSSARY_USER_DECISIONS.md` | Log of user decisions |
| `BILINGUAL_GLOSSARY_V3.md` | Versioned glossary after decisions applied |
| `BILINGUAL_GLOSSARY.md` | Main glossary (always latest version) |
| `.backup-phase1l-*.md` | Timestamped backup of previous main glossary |

## Safety

- Do not modify original skill files during review
- Do not modify bilingual glossary v2 file (preserve as archive)
- Only create new files (v3, decisions, packet)
