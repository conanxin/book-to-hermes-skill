# Quick Start

Five copy-paste examples for converting documents into book skills.

## 1. Markdown

```bash
python3 ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/build_book_skill.py \
  --source ~/documents/my-article.md \
  --slug my-article \
  --title "My Article" \
  --language en \
  --mode article \
  --output-dir ~/.hermes/skills/books \
  --allow-overwrite yes

python3 ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/validate_book_skill.py \
  --skill-dir ~/.hermes/skills/books/my-article
```

**After conversion, ask Hermes:**
> "Load the my-article skill and tell me the main arguments."

## 2. TXT

```bash
python3 ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/build_book_skill.py \
  --source ~/documents/notes.txt \
  --slug my-notes \
  --title "My Notes" \
  --language en \
  --mode narrative \
  --output-dir ~/.hermes/skills/books \
  --allow-overwrite yes

python3 ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/validate_book_skill.py \
  --skill-dir ~/.hermes/skills/books/my-notes
```

**After conversion, ask Hermes:**
> "Load the my-notes skill. What are the key points from chapter 2?"

## 3. PDF

```bash
python3 ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/build_book_skill.py \
  --source ~/books/designing-data-intensive-apps.pdf \
  --slug ddia \
  --title "Designing Data-Intensive Applications" \
  --language en \
  --mode technical \
  --output-dir ~/.hermes/skills/books \
  --allow-overwrite yes

python3 ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/validate_book_skill.py \
  --skill-dir ~/.hermes/skills/books/ddia
```

**After conversion, ask Hermes:**
> "Load the ddia skill. Explain replication strategies."

## 4. HTML

```bash
python3 ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/build_book_skill.py \
  --source ~/downloads/article.html \
  --slug web-article \
  --title "Web Article" \
  --language en \
  --mode article \
  --output-dir ~/.hermes/skills/books \
  --allow-overwrite yes

python3 ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/validate_book_skill.py \
  --skill-dir ~/.hermes/skills/books/web-article
```

**After conversion, ask Hermes:**
> "Load the web-article skill. Summarize the findings."

## 5. DOCX / EPUB

**DOCX:**
```bash
python3 ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/build_book_skill.py \
  --source ~/documents/report.docx \
  --slug project-report \
  --title "Project Report" \
  --language en \
  --mode project-docs \
  --output-dir ~/.hermes/skills/books \
  --allow-overwrite yes

python3 ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/validate_book_skill.py \
  --skill-dir ~/.hermes/skills/books/project-report
```

**EPUB:**
```bash
python3 ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/build_book_skill.py \
  --source ~/books/my-book.epub \
  --slug my-epub-book \
  --title "My EPUB Book" \
  --language zh-en \
  --mode technical \
  --output-dir ~/.hermes/skills/books \
  --allow-overwrite yes

python3 ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/validate_book_skill.py \
  --skill-dir ~/.hermes/skills/books/my-epub-book
```

**After conversion, ask Hermes:**
> "Load the project-report skill. What are the action items?"
> "Load the my-epub-book skill. Explain the architecture in chapter 3."

## Common Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--source` | yes | — | Path to source document |
| `--slug` | no | filename | Skill directory name |
| `--title` | no | auto | Book title |
| `--language` | no | auto | `zh` / `en` / `zh-en` / `auto` |
| `--mode` | no | auto | `technical` / `narrative` / `article` / `api-docs` / `project-docs` |
| `--output-dir` | no | `~/.hermes/skills/books/` | Output root |
| `--allow-overwrite` | no | `no` | `yes` to overwrite existing |

## Troubleshooting

**"python-docx not installed"**
```bash
~/.hermes/venvs/book-to-hermes-skill/bin/python -m pip install python-docx
```

**"ebooklib not installed"**
```bash
~/.hermes/venvs/book-to-hermes-skill/bin/python -m pip install ebooklib beautifulsoup4
```

**"Unsupported format"**
Check `references/supported_formats.md` for current format support.
