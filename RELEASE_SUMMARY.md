# Release Summary

## book-to-hermes-skill v0.1.0-local

### Development Phases Completed

| Phase | Focus | Status |
|-------|-------|--------|
| 0-a | Skeleton + text extraction | PASS |
| 0-b | Markdown/TXT smoke test | PASS |
| 0-c | PDF support + validate | PASS |
| 0-d | Real HTML test (lofi-engine) | PASS |
| 0-e | DOCX/EPUB support | PASS |
| 0-f | Glossary/Topic refinement | PASS |
| 0-g | Format expansion precheck | PASS |
| 1-a | First daily use (art-as-end-in-itself) | PASS |
| 1-b | English glossary + title fix + manifest | PASS |
| 1-c | GitHub-ready export | PASS |

### Current Functionality

- Extract text from 6 formats: Markdown, TXT, PDF, HTML, DOCX, EPUB
- Generate Hermes-native skills with:
  - Progressive disclosure (SKILL.md + chapter files)
  - Extractive summaries (no LLM, no synthetic content)
  - Glossary with term extraction (Chinese + English academic concepts)
  - Topic index
  - Patterns & techniques
  - Cheatsheet
  - Source manifest with safety notes
- Validate generated skills for structure and safety
- HTML title extraction with filename-like title filtering
- Table normalization (Markdown tables → field: value format)
- Chinese term quality filtering
- English academic concept extraction (Title Case, hyphenated, frequent concepts)

### Supported Formats

- Markdown (.md, .markdown)
- Plain text (.txt)
- Text PDF (.pdf)
- HTML (.html, .htm)
- DOCX (.docx)
- EPUB (.epub)

### Known Limitations

- No OCR PDF support
- No DRM EPUB support
- No RTF support
- No MOBI/AZW/AZW3 support
- No LLM enrichment (extractive only)
- Glossary definitions are extractive, may need manual refinement
- Patterns are template-heavy with extractive evidence

### Recommended Next Steps

1. **Daily use**: Continue generating book skills from your reading
2. **Manual enrichment**: Refine glossary definitions for important skills
3. **LLM enrichment design**: Design post-processing pipeline for glossary/patterns refinement
4. **RTF/MOBI support**: Add if needed (lower priority)
5. **Public release**: Choose license and publish (optional)

### Safety Guarantees

- No auto-install of dependencies
- No network requests during generation
- No LLM API calls during generation
- No script execution (HTML/EPUB)
- No macro execution (DOCX)
- Extractive summaries only
