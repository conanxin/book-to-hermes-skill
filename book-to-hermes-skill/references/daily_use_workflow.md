# Daily Use Workflow

## Complete End-to-End Workflow

### 1. Find Candidates

Search limited directories:
```bash
find ~/.hermes/workspace ~/Downloads ~/Documents \
  -type f \( -name '*.md' -o -name '*.pdf' -o -name '*.html' \
    -o -name '*.docx' -o -name '*.epub' \) \
  ! -path '*/smoke*' ! -path '*/test*' ! -path '*/phase*' \
  ! -path '*/secret*' ! -path '*/.env*' \
  -size +10k -size -30M
```

### 2. Evaluate Top 5

| Criterion | Weight | Check |
|-----------|--------|-------|
| Structure | High | Clear headings/chapters? |
| Content | High | Substantive, not test/smoke? |
| Size | Medium | >10KB, not overwhelming? |
| Privacy | High | Published content preferred |
| Recency | Low | Recently studied/relevant? |
| Format | Medium | HTML/Markdown/PDF/EPUB preferred |

### 3. Generate Skill

```bash
source ~/.hermes/venvs/book-to-hermes-skill/bin/activate
python ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/build_book_skill.py \
  --source /path/to/doc.html \
  --slug my-document \
  --title "My Document" \
  --language zh \
  --mode article \
  --output-dir ~/.hermes/skills/books \
  --allow-overwrite no
```

If target exists, auto-appends `-v2`.

### 4. Validate

```bash
python ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/validate_book_skill.py \
  --skill-dir ~/.hermes/skills/books/my-document
```

### 5. Quality Check

| Check | Command | Pass Criteria |
|-------|---------|---------------|
| SKILL.md size | `wc -c` | < 15,000 |
| Glossary quality | `head -50 glossary.md` | Real terms, no fragments |
| Chapter titles | `ls chapters/` | Meaningful, not filenames |
| Topic Index | `grep -i '成功\|无\|是\|否\|PASS\|FAIL'` | No status words |
| Placeholders | `grep -ri 'TODO\|PLACEHOLDER\|TBD'` | None |
| Table syntax | `grep -r '^|' chapters/` | None in Key Points |

### 6. Decide

- **Keep**: validate PASS, quality checks pass, content is unique
- **Discard**: validate FAIL, quality checks fail, content duplicates existing skill
- **Enrich**: validate PASS but glossary needs manual cleanup

### 7. Document

Generate Phase report with:
- Candidate list (top 5)
- Selection rationale
- Validate result
- Quality sampling
- Hermes usage method
- Recommendation

### 8. Use in Hermes

```
@my-document
```

Or with topic:
```
@my-document 关键概念
```

### 9. Periodic Maintenance

- Monthly: review generated skills, remove unused
- Quarterly: enrich glossary for top skills
- As needed: re-export tool to GitHub private repo

## Quality Acceptance Criteria

- Validate: 0 errors, warnings explained
- SKILL.md: <15K chars
- Glossary: no obvious fragments, real terms present
- Topic Index: no status words
- Key Points: no raw Markdown table syntax
- Placeholders: none
- Progressive disclosure: chapter index present
