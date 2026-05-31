# Sample Command

## Smoke Test

```bash
python3 ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/build_book_skill.py \
  --source ~/.hermes/workspace/book_to_skill/smoke_test/sample_book.md \
  --slug _book_to_skill_smoke_test \
  --title "Book-to-Hermes Skill Smoke Test" \
  --language zh-en \
  --mode technical \
  --output-dir ~/.hermes/skills/books \
  --allow-overwrite yes
```

## Validate Result

```bash
python3 ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/validate_book_skill.py \
  --skill-dir ~/.hermes/skills/books/_book_to_skill_smoke_test
```
