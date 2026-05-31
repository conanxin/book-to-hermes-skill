# Examples

## 1. Technical Book

**Source:** `~/books/designing-data-intensive-apps.pdf`

**Command:**
```bash
python3 ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/build_book_skill.py \
  --source ~/books/designing-data-intensive-apps.pdf \
  --slug ddia \
  --title "Designing Data-Intensive Applications" \
  --language en \
  --mode technical \
  --output-dir ~/.hermes/skills/books \
  --allow-overwrite yes
```

**After conversion:**
> "Load the ddia skill. What are the trade-offs between consistency and availability?"

## 2. Long Article

**Source:** `~/articles/raft-paper.md`

**Command:**
```bash
python3 ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/build_book_skill.py \
  --source ~/articles/raft-paper.md \
  --slug raft \
  --title "In Search of an Understandable Consensus Algorithm" \
  --language en \
  --mode article \
  --output-dir ~/.hermes/skills/books \
  --allow-overwrite yes
```

**After conversion:**
> "Load the raft skill. How does leader election work?"

## 3. Project Report

**Source:** `~/projects/q3-report.docx`

**Command:**
```bash
python3 ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/build_book_skill.py \
  --source ~/projects/q3-report.docx \
  --slug q3-report \
  --title "Q3 Project Report" \
  --language zh-en \
  --mode project-docs \
  --output-dir ~/.hermes/skills/books \
  --allow-overwrite yes
```

**After conversion:**
> "Load the q3-report skill. What are the blockers and next steps?"

## 4. API Documentation

**Source:** `~/docs/api-reference.html`

**Command:**
```bash
python3 ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/build_book_skill.py \
  --source ~/docs/api-reference.html \
  --slug api-ref \
  --title "API Reference" \
  --language en \
  --mode api-docs \
  --output-dir ~/.hermes/skills/books \
  --allow-overwrite yes
```

**After conversion:**
> "Load the api-ref skill. How do I authenticate requests?"

## 5. Chinese-English Mixed Document

**Source:** `~/books/csapp-zh.epub`

**Command:**
```bash
python3 ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/build_book_skill.py \
  --source ~/books/csapp-zh.epub \
  --slug csapp-zh \
  --title "深入理解计算机系统" \
  --language zh-en \
  --mode technical \
  --output-dir ~/.hermes/skills/books \
  --allow-overwrite yes
```

**After conversion:**
> "Load the csapp-zh skill. 解释虚拟内存的工作原理。"

## Naming Conventions

| Element | Rule | Example |
|---------|------|---------|
| slug | lowercase, hyphens, no spaces | `ddia`, `raft-paper` |
| title | original document title | "Designing Data-Intensive Applications" |
| language | `zh` / `en` / `zh-en` / `auto` | `en` for English, `zh-en` for mixed |
| mode | see below | `technical` for tech books |

## Mode Selection

| Mode | Use For | Output Style |
|------|---------|--------------|
| `technical` | Technical books, system design docs | Extractive summaries with code, architecture, patterns |
| `narrative` | Novels, essays, stories | Chapter summaries with themes, characters, plot |
| `article` | Blog posts, papers, long reads | Argument summaries with evidence and conclusions |
| `api-docs` | API references, SDK docs | Endpoint summaries with parameters and examples |
| `project-docs` | Reports, plans, retrospectives | Action items, blockers, decisions, next steps |
