# Known Pitfalls & Fixes

Session-tested bugs and their resolutions. Update this file when a new pitfall is discovered during conversion.

## Chapter Detection

### False Positive: Numbered Lists Detected as Chapters

**Symptom**: A line like `1. Reliability means making the system work...` is split into its own "chapter" instead of staying in the current section.

**Root Cause**: A regex pattern `^\d+\.\s+` was included in chapter detection, treating any numbered list item as a chapter boundary.

**Fix**: Remove the `^\d+\.\s+` pattern from `split_into_chapters()`. Rely on:
- Explicit chapter markers (`Chapter N`, `第N章`)
- Markdown H2 headers (`## Title`)
- Fixed-character chunking as final fallback

**Verification**: Run smoke test with a document containing numbered lists; verify they are NOT split into separate chapters.

### Missing H2 Auto-Trigger

**Symptom**: Documents with only `## Section` headers are not split into chapters.

**Root Cause**: Only explicit `Chapter N` / `第N章` patterns triggered splitting; H2 headers were ignored unless they followed an H1.

**Fix**: Always treat `## Heading` as a chapter boundary in `split_into_chapters()`, regardless of preceding content.

## Term Extraction

### Chinese Term Fragmentation

**Symptom**: Glossary contains garbage terms like `本书介绍如何将各`, `种文档格式转换为`, `核心目标是实现`.

**Root Cause**: The regex `[\u4e00-\u9fff]{2,8}` matches any sequence of 2-8 Chinese characters, crossing sentence and phrase boundaries.

**Fix Options** (in order of preference):
1. **Sentence-boundary extraction**: Only extract terms from within a single sentence (delimited by `。！？；`)
2. **Stop-word filtering**: Maintain a list of common Chinese function words (的, 了, 在, 是, 和, 将, 为, 以, 及, 或, 与, 对, 从, 到, 等) and filter out terms containing them
3. **POS-aware extraction**: Use jieba or similar for proper segmentation (requires dependency install)

**Current Implementation**: Option 1 + partial Option 2. Terms are extracted per sentence, and terms containing high-frequency function words are deprioritized.

**Verification**: After running `build_book_skill.py`, check `glossary.md` for fragmented terms. Acceptable: `按需加载`, `渐进式披露`. Unacceptable: `本书介绍如何将各`.

### Phase 0-f: Strong Suffix Whitelist Too Permissive (2026-05-31)

**Symptom**: Terms like `无外部 CDN 依赖` passed filtering because "依赖" is in `_HIGH_QUALITY_SUFFIXES`, even though "无" is a low-quality prefix. Similarly, `完全可行` (status phrase) passed because "可行" is a suffix.

**Root Cause**: The `has_high_quality` boolean check allowed any term containing a high-quality suffix to bypass ALL prefix-based and status-word filtering. This created a bypass tunnel for low-quality terms.

**Fix**: Replaced the broad `has_high_quality` bypass with an explicit `strong_suffixes` list (80+ entries). A term starting with a low-quality prefix (无/有/是/否/已/未/不) is ONLY allowed if it ends with one of the strong suffixes. Status phrases like `完全可行` are now explicitly listed in `_STATUS_WORDS`.

**Lesson**: Whitelist-based bypasses must be narrowly scoped. A suffix that makes `构建验证` valid should not also validate `无外部 CDN 依赖`.

### Phase 0-f: Code Terms Contaminated by Table Syntax (2026-05-31)

**Symptom**: Glossary contained terms like `| 6 | Type 'number' not assignable to type ' = ...' | |` from inline code in Markdown table cells.

**Root Cause**: `_clean_term()` stripped backticks but not pipe characters. The regex `` `([^`]+)` `` captured entire table cell contents including pipes.

**Fix**: Two-layer defense:
1. `_clean_term()` now strips leading/trailing `|`, `-`, em-dash, bullets
2. `_is_quality_topic()` rejects `source_type="code"` terms containing `|` or multiple `...` sequences

**Lesson**: Table syntax cleanup must happen in BOTH the cleaning layer and the quality gate. Relying on one layer alone leaves bypass paths.

### Phase 0-f: Version Numbers and Numeric Units as Terms (2026-05-31)

**Symptom**: `node: v22.22.0 ✅ npm: 10.9.4 ✅ pnpm: 10.32.1 ✅`, `37 MB`, `65+` appeared in glossary.

**Root Cause**: Length check was `len(t) > 60` — too permissive for 40-60 char code fragments. Version regex only matched PURE version numbers, not mixed text.

**Fix**: Added regex-based numeric filtering in `_is_quality_topic()`:
- `^\d+[\s\w]*$` — pure numbers with optional units
- `^\d+\+?\s*[A-Za-z]+$` — numbers with suffixes
- Code terms with version substrings are now caught by the `|` filter or by length heuristics

**Lesson**: Numeric content needs explicit rejection patterns, not just length bounds.

### Phase 0-f: Fragment End Check Override Bug (2026-05-31)

**Symptom**: `版可运行性验证报告` was not rejected even though it ends with `可运行性验证报告` (prefix "版" = 1 char, too short).

**Root Cause**: The fragment end loop checked multiple endings. `验证报告` (4 chars) was checked first and did NOT return False (prefix was long enough). Then `可运行性验证报告` (8 chars) WAS checked and SHOULD have returned False, but the term still appeared.

**Actual Root Cause**: The term was extracted from the title as a `chinese` type term, but `_is_quality_topic()` was not being called for glossary terms — only `_is_meaningful_chinese()` was. The Phase 0-e code path bypassed `_is_quality_topic()` for glossary generation.

**Fix**: Updated `extract_terms()` to apply `_is_quality_topic()` filtering universally, not just for Topic Index. Glossary and Topic Index now share the same quality gate.

**Lesson**: Multiple quality gates must ALL be applied to ALL output paths. A gate that only protects one output channel leaves others exposed.

**Problem**: Even after basic filtering, glossary contained low-quality Chinese terms: `版可运行性验证报告` (title fragment), `未启动或重启` (verb phrase), `静态资源源文件` (compound noun chain).

**Solution**: Implemented a three-layer filtering system in `build_book_skill.py`:

1. **`_clean_term()`** — strips Markdown symbols (`*`, `#`, `` ` ``, `>`, `[]()`, extra whitespace)
2. **`_is_meaningful_chinese()`** — multi-criteria filter:
   - Length: 2–12 Chinese characters
   - Meaningful ratio: at least 2 characters not in stop-word set
   - Fragment start filter: reject terms starting with `本书/本文/本章/介绍/说明/包含/包括/通过/使用/进行` if longer than the prefix + 3 chars
   - Fragment end filter: for terms > 8 chars ending with a single stop word, verify the prefix has meaningful content
3. **`add_term()`** — unified deduplication gate with length bounds and Chinese filtering

**Stop-word set size**: 500+ entries covering function words, common verbs, adverbs, pronouns, and generic nouns.

**New term types added**:
- `mixed` — Chinese-English mixed terms like `Hermes skill`, `静态 Web`, `progressive disclosure`
- Detected via regex: `\b([A-Za-z]+\s+[\u4e00-\u9fff]{2,8})\b` and reverse

**Verification command**:
```bash
python3 ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/build_book_skill.py \
  --source /path/to/chinese-doc.md --slug test-zh --language zh --mode technical \
  --output-dir ~/.hermes/skills/books --allow-overwrite yes

grep -c "appears in source" ~/.hermes/skills/books/test-zh/glossary.md
# Should show terms, not fragments
```

**Residual issues** (acceptable for Phase 0-d):
- `版可运行性验证报告` — title fragment when heading contains mixed content; rare edge case
- Table content sometimes leaks into summary when tables lack blank-line separation

### English Compound Word Over-Extraction

**Symptom**: Glossary contains terms like `book-to-hermes-skill` which is actually the project name, not a domain concept.

**Mitigation**: Terms matching the project slug or filename are deprioritized. Domain-specific terms (e.g., `extractive-summary`, `token-budget`) are preferred.

## Summary Generation

### Run-On Sentences in Extractive Summary

**Symptom**: Summary reads as a wall of text with no separation between sentences.

**Root Cause**: Sentences from different paragraphs are concatenated with spaces, losing paragraph structure.

**Fix**: Preserve paragraph boundaries in summary output. Separate paragraph groups with blank lines.

### Missing Context for Key Points

**Symptom**: Key points list is empty for chapters without explicit bullet lists.

**Fallback**: When no list items are found, use the first 3-5 sentences of the extractive summary as key points.

## File Naming

### Slug Collision with Chinese Titles

**Symptom**: Two different Chinese titles produce the same slugified filename.

**Root Cause**: `slugify()` strips all non-ASCII characters, so `第一章` and `第二章` both become empty strings.

**Fix**: `slugify()` preserves Chinese characters by converting them to pinyin or keeping them as-is. Current implementation keeps Chinese characters in filenames (e.g., `ch02-第一章项目概述.md`).

## Source Structure

### PDF-to-HTML Conversion Loses Heading Structure (Phase 1-h, 2026-05-31)

**Symptom**: Chinese skill has 7 chapters while English skill has 8. Chapter 1.3 ("The Cost of One-Dimensionality: The Disappearance of the Relational Layer") appears to be "missing" from the Chinese version.

**Root Cause**: The Chinese source HTML was converted from PDF. During conversion, the `<h2>` heading for 1.3 was lost and replaced with a `<li>` list item inside the preceding 1.2 section:

```html
<!-- English source (correct) -->
<h2>1.3 3. The Cost of One-Dimensionality...</h2>

<!-- Chinese source (broken) -->
<li><p>1.3 三、单向度的代价：关系层的消失 ...</p></li>
```

The chapter splitter splits on `<h2>` elements only, so the 1.3 content is absorbed into the 1.2 chapter.

**Content check**: The 1.3 content IS present in the Chinese source HTML (salons, patronage, master-apprentice, impressionist, cubist, surrealist, gallery, café, tea ceremony all appear). It is simply not extracted as a separate chapter.

**Fix Options** (in order of preference):
1. **Manual source fix** (fastest): Edit the source HTML to wrap the 1.3 content in `<h2>1.3 ...</h2>` instead of `<li>`, then regenerate the skill.
2. **Enhanced splitter**: Modify `split_into_chapters()` to recognize `<li>` elements containing chapter-like markers (e.g., `<li>1.3 三、...`) as chapter boundaries. Risk: false positives from regular list items.
3. **Full-text extraction**: Change the skill to include full text instead of extractive summaries. This preserves all content regardless of chapter boundaries, but increases skill size significantly.

**Diagnostic checklist for "missing chapter" reports**:
1. Check source HTML h2 headings: `grep -n "<h2" source.html`
2. Check if "missing" content exists in source: `grep -n "keyword" source.html`
3. Check if content is embedded in another chapter: `grep -n "keyword" source.html | head -5`
4. Check source structure around suspected gap: `sed -n 'start,endp' source.html | grep "<h2\|<li\|<p"`
5. If content exists but not as h2 → source structure issue, not missing content

**Lesson**: "Missing chapter" does not always mean "missing content". Always verify the source HTML structure before concluding content is absent. PDF-to-HTML conversion is a common source of heading structure loss.

## Validation

### False Positive Secret Detection

**Symptom**: `validate_book_skill.py` flags legitimate content as containing secrets.

**Known Cases**:
- `sk-` prefix in text about "skill files" triggers OpenAI key pattern
- `ghp_` in GitHub Pages URLs triggers GitHub token pattern

**Mitigation**: The secret scanner is conservative. Manual review is required when warnings appear. The scanner does not block generation; it only emits warnings.

### Phase 0-f-resume: Tool Loop Warning During Validation (2026-05-31)

**Symptom**: Agent repeatedly called `grep` with identical arguments, triggering `repeated_exact_failure_warning` after 3+ identical failures with exit code 1 (no matches found).

**Root Cause**: The agent interpreted `grep` exit code 1 (no matches = success for negative checks) as a failure and retried the same command. The tool loop warning then blocked further progress.

**Fix**: Agent behavior — not a code fix. For negative checks ("confirm X does NOT exist"), exit code 1 is the expected success state. The agent should:
1. Treat exit code 1 from `grep -E 'pattern' file` as PASS when the goal is absence
2. Not retry identical commands after exit code 1
3. Use `|| true` or `; echo "done"` to force exit code 0 if the tool framework requires it

**Lesson**: Negative verification commands need explicit handling. Either wrap with `|| echo "PASS: no matches"` or use `grep -c` and check count == 0.
