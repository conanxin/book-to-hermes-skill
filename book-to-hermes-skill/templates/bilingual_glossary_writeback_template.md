# Bilingual Glossary Write-Back Template

## Pre-Write-Back Checklist

- [ ] User decisions finalized and logged
- [ ] Accepted terms list confirmed (max 4-6 terms per batch)
- [ ] Rejected terms list confirmed
- [ ] Both skills backed up with timestamp
- [ ] Validate scripts ready

## Backup Requirements

```bash
TS=$(date +%Y%m%d-%H%M%S)
cp -r ~/.hermes/skills/books/{slug}-en ~/.hermes/skills/books/{slug}-en.backup-phase1m-${TS}
cp -r ~/.hermes/skills/books/{slug}-zh ~/.hermes/skills/books/{slug}-zh.backup-phase1m-${TS}
```

## Allowed Modifications

| File | Action |
|------|--------|
| `{en-skill}/glossary.md` | Append user-reviewed terms section |
| `{zh-skill}/glossary.md` | Append user-reviewed terms section |

## Forbidden Modifications

| File | Action |
|------|--------|
| `{skill}/SKILL.md` | DO NOT MODIFY |
| `{skill}/chapters/*.md` | DO NOT MODIFY |
| `{skill}/metadata.json` | DO NOT MODIFY |
| `{skill}/patterns.md` | DO NOT MODIFY |
| `{skill}/cheatsheet.md` | DO NOT MODIFY |
| `{skill}/source_manifest.md` | DO NOT MODIFY |
| Source documents | DO NOT MODIFY |

## Write-Back Section Template (English)

```markdown
## User-Reviewed Bilingual Terms

- **{English term}** → {Chinese} — {decision status}. {reason}.
  _Related: {chapter references}_
  _Note: {optional note}_
```

## Write-Back Section Template (Chinese)

```markdown
## 用户审校通过的双语术语

- **{中文术语}** → {English} — {decision status}。{reason}。
  _Related: {章节引用}_
  _Note: {optional note}_
```

## Validate After Write-Back

```bash
source ~/.hermes/venvs/book-to-hermes-skill/bin/activate
python ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/validate_book_skill.py \
  --skill-dir ~/.hermes/skills/books/{slug}-en
python ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/validate_book_skill.py \
  --skill-dir ~/.hermes/skills/books/{slug}-zh
```

## Forbidden Terms Check

Verify these terms were NOT added as new entries:

- Artist as brand / 艺术家品牌
- Post-internet art / 后互联网艺术
- Auction / 拍卖
- Museum / 美术馆
- Cultural capital / 文化资本
- Financialization / 金融化
- Institutional critique / 制度批判
- Contemporary art / 当代艺术

## Post-Write-Back Checklist

- [ ] Both skills validate PASS
- [ ] 0 errors, 0 warnings
- [ ] Only glossary.md differs from backup
- [ ] All accepted terms found in glossary
- [ ] All rejected terms absent from glossary
- [ ] Artistic autonomy has note about source wording
- [ ] Ulay keeps original name with Chinese annotation
- [ ] Report generated
