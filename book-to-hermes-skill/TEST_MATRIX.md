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
