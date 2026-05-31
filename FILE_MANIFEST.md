# File Manifest

## book-to-hermes-skill/ (Tool Directory)

### Core Documentation
- SKILL.md — Main skill definition and workflow
- README.md — Project overview (public-facing)
- QUICKSTART.md — Copy-paste examples
- EXAMPLES.md — Naming conventions and modes
- SECURITY.md — Safety boundaries
- MAINTENANCE.md — Maintenance guide including bilingual glossary workflow
- TEST_MATRIX.md — Test results (Phase 0 + Phase 1)
- RELEASE_NOTES.md — Changelog
- PHASE_INDEX.md — Phase history

### Scripts
- scripts/extract_text.py — Text extraction from documents
- scripts/build_book_skill.py — Skill generation
- scripts/validate_book_skill.py — Validation

### Templates
- templates/chapter.md — Chapter file template
- templates/cheatsheet.md — Cheatsheet template
- templates/glossary.md — Glossary template
- templates/patterns.md — Patterns template
- templates/generated_SKILL.md — SKILL.md generation template
- templates/bilingual_glossary_review_packet_template.md — Review packet template (Phase 1-n)
- templates/bilingual_glossary_writeback_template.md — Write-back template (Phase 1-n)

### References
- references/supported_formats.md — Format support matrix
- references/output_schema.md — Output structure
- references/safety_policy.md — Safety rules
- references/pitfalls.md — Known bugs and fixes
- references/english_term_extraction.md — English term extraction rules
- references/chinese_term_extraction.md — Chinese term extraction rules
- references/extractive_summary_rules.md — Summary generation rules
- references/table_normalization.md — Table normalization rules
- references/html_title_extraction.md — HTML title extraction
- references/format_detection_pitfalls.md — Format detection pitfalls
- references/format_expansion_precheck.md — Format expansion precheck (Phase 0-g)
- references/phase_based_development.md — Phase-based development guide
- references/release_freeze_pattern.md — Release freeze pattern
- references/bilingual_skill_pair.md — Bilingual skill pair pattern (Phase 1-c)
- references/bilingual_glossary_alignment.md — Bilingual glossary alignment (Phase 1-g)
- references/bilingual_glossary_user_review.md — User review documentation (Phase 1-k)
- references/bilingual_glossary_workflow.md — Complete bilingual workflow (Phase 1-n)
- references/github_ready_export.md — GitHub export guide (Phase 1-c)
- references/private_github_push.md — Private GitHub push guide (Phase 1-d)
- references/daily_use_workflow.md — Daily use workflow (Phase 1-f)
- references/daily_use_patterns.md — Daily use patterns
- references/source_structure_diagnostics.md — Source structure diagnostics (Phase 1-h)
- references/source_structure_repair.md — Source structure repair (Phase 1-i)
- references/validate_layered_safety.md — Validation safety layers

### Examples
- examples/sample_command.md — Sample command reference

## Export-Level Files

- README.md — Main project README (public-facing)
- ROADMAP.md — Future plans and roadmap
- LICENSE — MIT License
- README_EXPORT.md — Export README
- FILE_MANIFEST.md — This file
- RELEASE_SUMMARY.md — Release summary
- PUBLISHING_CHECKLIST.md — Publishing status
- .gitignore — Git ignore rules

## Exclusions

The following are NOT included in this export:
- Source documents (PDF, EPUB, DOCX, HTML originals)
- Generated book skills (stored in ~/.hermes/skills/books/)
- Backup directories
- Cache files (__pycache__, .pytest_cache)
- Environment files (.env)
- Log files
- Secret / credential files
