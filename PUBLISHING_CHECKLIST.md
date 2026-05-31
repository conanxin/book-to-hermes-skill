# Publishing Checklist

## Current Status

- [x] Private GitHub repo created: https://github.com/conanxin/book-to-hermes-skill
- [x] Local export prepared
- [x] .gitignore configured
- [x] FILE_MANIFEST.md updated
- [x] RELEASE_SUMMARY.md updated
- [x] Bilingual glossary workflow templates added
- [ ] License selected and added
- [ ] Public release reviewed

## Private Repo (Current)

- [x] Repo is PRIVATE
- [x] No secrets in repo
- [x] No source documents in repo
- [x] No generated skills in repo
- [x] No .env or config files in repo
- [x] Scripts have no network/LLM calls
- [x] All tests pass

## Before Public Release

- [ ] Select license (MIT / GPL / Apache / etc.)
- [ ] Add LICENSE file
- [ ] Review SECURITY.md for public audience
- [ ] Review README.md for public audience
- [ ] Remove any personal references if needed
- [ ] Add CONTRIBUTING.md if accepting PRs
- [ ] Review all references/ for sensitive content
- [ ] Consider adding CI/CD (GitHub Actions)
- [ ] Tag initial release (v0.1.0)

## Not For Public Release

- Source documents (PDF, EPUB, DOCX, HTML originals)
- Generated book skills (contain extracted content)
- Personal workspace paths
- API keys or credentials
- Hermes config files

## Bilingual Glossary Workflow (Phase 1-n)

- [x] Workflow documented
- [x] Review packet template created
- [x] Write-back template created
- [x] MAINTENANCE.md updated
- [x] TEST_MATRIX.md updated
- [ ] Future: Consider automating glossary extraction (not write-back)
