# Test Matrix

## Phase 0-b: Markdown Smoke Test

| Field | Value |
|-------|-------|
| Source | `~/.hermes/workspace/book_to_skill/smoke_test/sample_book.md` |
| Output skill | `~/.hermes/skills/books/book-to-skill-smoke-test/` |
| Validate | PASS |
| Errors | 0 |
| Warnings | 0 |
| Chapters | 4 |
| Known issue | None |
| Status | PASS |

## Phase 0-d: Real Markdown / Report Test

| Field | Value |
|-------|-------|
| Source | `~/.hermes/workspace/reports/lofi-engine/HERMES_LOFI_ENGINE_STATIC_BUILD_REPORT.md` |
| Output skill | `~/.hermes/skills/books/phase0d-lofi-engine-static-build-report/` |
| Validate | PASS |
| Errors | 0 |
| Warnings | 0 |
| Chapters | 19 |
| Known issue | None |
| Status | PASS |

## Phase 0-h: HTML Smoke Test

| Field | Value |
|-------|-------|
| Source | `~/.hermes/workspace/book_to_skill/smoke_test/phase0h_html_smoke_test.html` |
| Output skill | `~/.hermes/skills/books/phase0h-html-test/` |
| Validate | PASS |
| Errors | 0 |
| Warnings | 0 |
| Chapters | 4 |
| Known issue | None |
| Status | PASS |

## Phase 0-h: DOCX Smoke Test

| Field | Value |
|-------|-------|
| Source | `~/.hermes/workspace/book_to_skill/smoke_test/phase0h_docx_smoke_test.docx` |
| Output skill | `~/.hermes/skills/books/phase0h-docx-test/` |
| Validate | PASS |
| Errors | 0 |
| Warnings | 0 |
| Chapters | 4 |
| Known issue | None |
| Status | PASS |

## Phase 0-h-real: Real HTML Test

| Field | Value |
|-------|-------|
| Source | `~/.hermes/workspace/integrations/opendataloader-sandbox/phase1b_output/The_Artist_Is_Dead.html` |
| Output skill | `~/.hermes/skills/books/phase0h-real-html-test/` |
| Validate | PASS |
| Errors | 0 |
| Warnings | 0 |
| Chapters | 8 |
| Known issue | Title guess from filename, not HTML `<title>` |
| Status | PASS |

## Phase 0-i: EPUB Smoke Test

| Field | Value |
|-------|-------|
| Source | `~/.hermes/workspace/book_to_skill/smoke_test/phase0i_epub_smoke_test.epub` |
| Output skill | `~/.hermes/skills/books/phase0i-epub-smoke-test/` |
| Validate | PASS |
| Errors | 0 |
| Warnings | 0 |
| Chapters | 4 |
| Known issue | None |
| Status | PASS |

## Phase 0-j: Complex EPUB Stress Test

| Field | Value |
|-------|-------|
| Source | `~/.hermes/workspace/book_to_skill/smoke_test/phase0j_complex_epub_stress_test.epub` |
| Output skill | `~/.hermes/skills/books/phase0j-complex-epub-stress-test/` |
| Validate | PASS |
| Errors | 0 |
| Warnings | 0 |
| Chapters | 13 |
| Known issue | Chinese text stored as Unicode escapes (creation script issue); blockquote paragraphs merged; Topic Index has table cell values |
| Status | PASS |

## Summary

| Phase | Format | Status |
|-------|--------|--------|
| 0-b | Markdown | PASS |
| 0-d | Markdown (real) | PASS |
| 0-h | HTML | PASS |
| 0-h | DOCX | PASS |
| 0-h-real | HTML (real) | PASS |
| 0-i | EPUB | PASS |
| 0-j | EPUB (complex) | PASS |

**Total: 7/7 PASS**

## Phase 1-g: Bilingual Glossary v1

| Field | Value |
|-------|-------|
| English skill | `~/.hermes/skills/books/the-artist-is-dead-en/` |
| Chinese skill | `~/.hermes/skills/books/the-artist-is-dead-zh/` |
| Output glossary | `~/.hermes/workspace/reports/book_to_skill/THE_ARTIST_IS_DEAD_BILINGUAL_GLOSSARY.md` |
| High confidence | 40 |
| Medium confidence | 18 |
| Low confidence | 20 |
| Missing | 16 |
| Method | Rule-based local extraction, no LLM |
| Status | PASS |

## Phase 1-h: Source Diagnostics

| Field | Value |
|-------|-------|
| Source | `~/.hermes/workspace/integrations/opendataloader-sandbox/phase1c_compare/opendataloader/artist_is_dead_zh/艺术家已死_中文.html` |
| Finding | Content complete; structure incomplete (1.3 chapter embedded in 1.2) |
| Alternative source | None found with correct `<h2>` structure |
| Decision | No rebuild from alternative source |
| Status | PARTIAL |

## Phase 1-i: Source Patch and Rebuild

| Field | Value |
|-------|-------|
| Patched source | `艺术家已死_中文.phase1i_patched.html` |
| Fix | `<li>` containing 1.3 title + body → split to `<h2>` + `<p>` |
| Rebuilt skill | `~/.hermes/skills/books/the-artist-is-dead-zh/` |
| Validate | PASS |
| Errors | 0 |
| Warnings | 0 |
| Chapters | 8 (was 7) |
| Status | PASS |

## Phase 1-j: Bilingual Glossary v2

| Field | Value |
|-------|-------|
| Output glossary | `THE_ARTIST_IS_DEAD_BILINGUAL_GLOSSARY_V2.md` |
| High confidence | 47 (+7) |
| Medium confidence | 24 (+6) |
| Low confidence | 14 (-6) |
| Missing | 14 (-2) |
| Upgraded terms | salons, patronage, master-apprentice, gallery, impressionist, cubist, surrealist |
| Status | PASS |

## Phase 1-k: Review Packet

| Field | Value |
|-------|-------|
| Output packet | `THE_ARTIST_IS_DEAD_BILINGUAL_GLOSSARY_REVIEW_PACKET.md` |
| Terms reviewed | 12 |
| Suggested accept | 3 |
| Needs review | 3 |
| Missing / do not write back | 6 |
| Method | Rule-based local extraction, no LLM |
| Status | PASS |

## Phase 1-l: User Decisions and v3

| Field | Value |
|-------|-------|
| Output glossary | `THE_ARTIST_IS_DEAD_BILINGUAL_GLOSSARY_V3.md` |
| Output decisions | `THE_ARTIST_IS_DEAD_BILINGUAL_GLOSSARY_USER_DECISIONS.md` |
| User accepted | 3 (AI art, Wabi-sabi, Ulay) |
| User revised | 1 (Artistic autonomy) |
| Reject write back | 2 (Artist as brand, Post-internet art) |
| Do not write back | 6 (Auction, Museum, Cultural capital, Financialization, Institutional critique, Contemporary art) |
| Status | PASS |

## Phase 1-m: Safe Write-Back

| Field | Value |
|-------|-------|
| Terms written back | 4 |
| English skill validate | PASS (0 errors, 0 warnings) |
| Chinese skill validate | PASS (0 errors, 0 warnings) |
| Files modified | glossary.md only |
| Files NOT modified | SKILL.md, chapters/, metadata.json, source docs |
| Backups created | Yes (timestamped) |
| Status | PASS |

## Phase 1-n: Workflow Template

| Field | Value |
|-------|-------|
| Workflow doc | `references/bilingual_glossary_workflow.md` |
| Review packet template | `templates/bilingual_glossary_review_packet_template.md` |
| Write-back template | `templates/bilingual_glossary_writeback_template.md` |
| MAINTENANCE.md updated | Yes |
| TEST_MATRIX.md updated | Yes |
| Status | PASS |

## Bilingual Glossary Summary

| Version | High | Medium | Low | Missing | Total |
|---------|------|--------|-----|---------|-------|
| v1 (1-g) | 40 | 18 | 20 | 16 | 94 |
| v2 (1-j) | 47 | 24 | 14 | 14 | 99 |
| v3 (1-l) | 50 | 25 | 14 | 14 | 103 |
| After write-back (1-m) | 50 | 25 | 14 | 14 | 103 |

**Net change: +6 high-confidence terms, +7 medium-confidence terms, -6 low-confidence terms, -2 missing terms**

## Total Phase 1 Summary

| Phase | Status | Key Output |
|-------|--------|------------|
| 1-a | PASS | English skill (8 chapters) |
| 1-b | PASS | Chinese skill (7 chapters) |
| 1-c | PASS | Bilingual skill pair report |
| 1-d | PASS | Candidate evaluation criteria |
| 1-e | PASS | Quality acceptance criteria |
| 1-f | PASS | Daily use workflow |
| 1-g | PASS | Bilingual glossary v1 |
| 1-h | PARTIAL | Source diagnostics (no alternative found) |
| 1-i | PASS | Source patched, skill rebuilt (8 chapters) |
| 1-j | PASS | Bilingual glossary v2 |
| 1-k | PASS | Review packet |
| 1-l | PASS | User decisions + v3 |
| 1-m | PASS | 4 terms written back to both skills |
| 1-n | PASS | Workflow templates |

**Phase 1 Overall: 13/14 PASS, 1 PARTIAL**
