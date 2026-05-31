# Chinese Term Extraction Reference

Reference for the Chinese term filtering system implemented in Phase 0-c/d (2026-05-30).

## Problem

Raw regex `[\u4e00-\u9fff]{2,8}` produces garbage terms:
- `本书介绍如何将各` — sentence fragment
- `种文档格式转换为` — sentence fragment
- `核心目标是实现` — verb phrase

## Three-Layer Filtering System

### Layer 1: `_clean_term()`

Strips Markdown formatting before term evaluation:
- Remove: `*`, `#`, `` ` ``, `>`, `[`, `]`, `(`, `)`
- Collapse whitespace
- Strip leading/trailing spaces

### Layer 2: `_is_meaningful_chinese()`

Multi-criteria quality gate:

| Check | Rule | Purpose |
|-------|------|---------|
| Length | 2–12 Chinese characters | Reject single chars and overly long fragments |
| Meaningful ratio | ≥2 chars not in stop-word set | Reject pure function-word sequences |
| Fragment start | Reject if starts with `本书/本文/本章/介绍/说明/包含/包括/通过/使用/进行` and length > prefix+3 | Reject common sentence openers |
| Fragment end | For terms >8 chars ending with stop word, verify prefix has ≥2 meaningful chars | Reject trailing-stop-word fragments |

### Layer 3: `add_term()`

Unified deduplication gate:
- Case-normalized deduplication
- Length bounds: 2–60 chars total
- Routes to `_is_meaningful_chinese()` for CJK content

## Stop-Word Set

500+ entries covering:
- Function words: 的, 了, 和, 与, 及, 在, 是, 将, 把, 为, 对, 从, 到
- Common verbs: 使用, 进行, 通过, 包含, 包括, 介绍, 说明
- Pronouns: 我, 你, 他, 她, 它, 我们, 你们, 他们
- Adverbs: 非常, 特别, 比较, 更加, 最好, 已经, 正在
- Generic nouns: 方法, 方式, 过程, 结果, 目的, 意义, 作用

Full set defined as `_CHINESE_STOP_WORDS` frozenset in `build_book_skill.py`.

## Term Type Hierarchy

| Type | Source | Example |
|------|--------|---------|
| `bold` | `**term**` | Skill, On-demand loading |
| `code` | `` `term` `` | extract_text.py |
| `technical` | English compound | book-to-hermes-skill |
| `mixed` | Chinese-English | Hermes skill, 静态 Web |
| `chinese` | Pure Chinese | 按需加载, 渐进式披露 |

## Mixed Term Detection

Regex patterns for Chinese-English mixed terms:

```python
# English word followed by Chinese
r"\b([A-Za-z]+\s+[\u4e00-\u9fff]{2,8})\b"

# Chinese followed by English word
r"\b([\u4e00-\u9fff]{2,8}\s+[A-Za-z]+)\b"
```

## Phase 0-f Refinements (2026-05-31)

### Problem: Strong Suffix Whitelist Too Permissive

**Symptom**: Terms like `无外部 CDN 依赖` passed filtering because "依赖" is in `_HIGH_QUALITY_SUFFIXES`, even though "无" is a low-quality prefix.

**Root Cause**: The `has_high_quality` check allowed any term containing a high-quality suffix to bypass prefix-based filtering.

**Fix**: Replaced broad suffix bypass with explicit `strong_suffixes` list (80+ entries). A term starting with a low-quality prefix (无/有/是/否/已/未/不) is only allowed if it ends with one of the strong suffixes:
- Technical: 架构, 策略, 模式, 流程, 门禁, 回滚, 验证, 部署
- Infrastructure: 网络, 存储, 缓存, 队列, 路由, 网关, 代理
- Development: 源码, 构建, 配置, 优化, 测试, 集成, 监控
- Operations: 备份, 恢复, 迁移, 升级, 发布, 上线, 审计

### Problem: Code Terms Contaminated by Table Syntax

**Symptom**: Glossary contained terms like `| 6 | Type 'number' not assignable to type ' = ...' | |` from inline code in Markdown tables.

**Fix**: Two-layer defense:
1. `_clean_term()` now strips leading/trailing `|`, `-`, em-dash, bullets
2. `_is_quality_topic()` rejects `source_type="code"` terms containing `|` or `...`

### Problem: Version Numbers and Numeric Units as Terms

**Symptom**: Terms like `node: v22.22.0 ✅ npm: 10.9.4 ✅ pnpm: 10.32.1 ✅`, `37 MB`, `65+` appeared in glossary.

**Fix**: Added regex-based filtering in `_is_quality_topic()`:
- `^\d+[\s\w]*$` — pure numbers with optional units
- `^\d+\+?\s*[A-Za-z]+$` — numbers with suffixes like `65+`
- Version regex `^v?\d+(\.\d+)*$` already existed, but mixed text with versions now caught by length heuristics

### Problem: Incomplete Chinese Fragments in Bold/Code

**Symptom**: Terms like `属性被声明为 getter（`, `） 2.`, `— 试图展开`, `但实际赋值为` from incomplete sentence fragments.

**Fix**: Enhanced `_is_meaningful_chinese()`:
- Added `_BAD_2CHAR_TERMS` set: 静态, 隔离, 输出, 对象, 属性, 构建, 运行, 验证, 成功, 失败, 完成, 状态, 结果, 路径, 文件, 目录, 大小, 时间, 方式, 方法, 问题, 建议, 说明, 介绍, 包含, 包括, 使用, 进行, 通过
- Fragment end check now tests ALL fragment endings and rejects if ANY match with a bad prefix (previously, a later passing check could override an earlier failing one)
- Fragment start list expanded: 本书, 本文, 本章, 这个, 这些, 那些, 通过, 如何, 进行, 使用, 包括, 包含, 说明, 介绍, 可以, 需要, 当前, 已经, 没有, 以及, 然后, 因此, 但是, 如果, 为了, 基于, 作为

### Problem: Status Emoji + Word Combinations

**Symptom**: `❌ 失败` passed as a code term.

**Fix**: Status emoji (❌, ✅, ⏳, ⚠️) now implicitly flagged by the table-syntax filter (`|` is not present, but the broader principle of rejecting symbolic prefixes applies). Future enhancement: explicit emoji stripping in `_clean_term()`.

## Residual Issues (Post Phase 0-f)

- `skill 骨架 如果 wslview 验证失败 如 file` — long sentence fragment with mixed Chinese-English; rare edge case when bold text spans multiple clauses
- `现在被证实可行` — status phrase with meaningful chars; caught by `_STATUS_WORDS` expansion but new variants may emerge
- Chapter title references in glossary (e.g., `_Related chapter: Phase B: lofi-engine 静态 Web 版可运行性验证报告_`) are expected and correct — they are not glossary terms, just provenance metadata

## Verification

```bash
python3 ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/build_book_skill.py \
  --source /path/to/chinese-doc.md --slug test-zh --language zh --mode technical \
  --output-dir ~/.hermes/skills/books --allow-overwrite yes

# Check glossary quality
cat ~/.hermes/skills/books/test-zh/glossary.md | head -30
# Acceptable: 按需加载, 渐进式披露, 核心目标, 静态 Web 版能力, 构建验证
# Unacceptable: 本书介绍如何将各, 种文档格式转换为, | 6 | Type..., 37 MB

# Check Topic Index
grep -A2 "Topic Index" ~/.hermes/skills/books/test-zh/SKILL.md
# Should NOT contain: 成功, 无, 是, 否, 完成, 通过, 正常, 异常, PASS, FAIL, OK
```
