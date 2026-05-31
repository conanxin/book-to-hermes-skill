# GitHub-Ready Export Pattern

Session: Phase 1-c (2026-05-31)

## Purpose

Structured workflow for creating a clean, scannable, git-initialized local export of a Hermes skill tool, ready for private GitHub backup or public release.

## When to Use

- Skill tool has reached a stable checkpoint (all phases PASS)
- User wants offline backup or version-controlled history
- Preparing for public release (needs license selection, manifest, security scan)

## Export Directory Structure

```
exports/<skill-name>/
├── <skill-name>/              # Tool本体 (copied from ~/.hermes/skills/knowledge/)
│   ├── SKILL.md
│   ├── README.md
│   ├── scripts/
│   ├── templates/
│   ├── references/
│   └── examples/
├── README_EXPORT.md           # Export metadata: version, supported formats, install instructions
├── FILE_MANIFEST.md           # All files with path/size/purpose/publish-safety flag
├── RELEASE_SUMMARY.md         # Phase history, current functionality, known limitations
├── PUBLISHING_CHECKLIST.md    # Pre-publish verification checklist
├── LICENSE_PENDING.md         # License selection guidance (if not yet chosen)
└── .gitignore                 # Excludes secrets, source docs, caches, large binaries
```

## Step-by-Step Workflow

### 1. Create Clean Export Directory

```bash
EXPORT_DIR=~/.hermes/workspace/exports/<skill-name>
if [ -d "$EXPORT_DIR" ]; then
    TS=$(date +%Y%m%d-%H%M%S)
    mv "$EXPORT_DIR" "${EXPORT_DIR}.backup-phase<N>-${TS}"
fi
mkdir -p "$EXPORT_DIR"
```

### 2. Copy Tool本体 (Selective)

Copy from `~/.hermes/skills/knowledge/<skill-name>/`:
- SKILL.md, README.md, QUICKSTART.md, EXAMPLES.md, SECURITY.md, MAINTENANCE.md, TEST_MATRIX.md, RELEASE_NOTES.md, PHASE_INDEX.md
- scripts/*.py
- templates/*.md
- references/*.md
- examples/*.md

### 3. Exclude (Never Copy)

| Category | Examples |
|----------|----------|
| Backups | `.backup*`, `__pycache__/`, `.pytest_cache/` |
| Virtual envs | `.venv/`, `venv/`, `node_modules/` |
| Secrets | `.env`, `*.key`, `*.pem`, tokens, credentials |
| Generated skills | `~/.hermes/skills/books/` contents |
| Source documents | `*.pdf`, `*.epub`, `*.docx`, `*.html` originals |
| Logs | `*.log`, `logs/` |
| Personal data | memories, cron, Telegram/OAuth content |

### 4. Create Export-Level Files

**README_EXPORT.md**: version, supported formats, safety boundaries, install instructions, publishing warnings

**FILE_MANIFEST.md**: table with columns path | size | purpose | safe_to_publish

**RELEASE_SUMMARY.md**: phase history, current functionality, supported formats, known limitations, recommended next steps

**PUBLISHING_CHECKLIST.md**: pre-publish verification items (secrets, source docs, API keys, logs, large binaries, license, repo visibility)

**LICENSE_PENDING.md**: if no license selected, explain options (MIT/Apache-2.0/GPL) and how to add

**.gitignore**: `.env`, `__pycache__/`, `.venv/`, `*.pdf`, `*.epub`, `*.docx`, `*.mobi`, `*.azw*`, `*.log`, `logs/`, `.backup*`, `.hermes/`

### 5. Security Scan

Run these checks and document results:

```bash
# Secret patterns
grep -riE 'API key|api_key|token|secret|credential|password|oauth|bearer|OPENAI|ANTHROPIC|OLLAMA|LITELLM' "$EXPORT_DIR" --include="*.py" --include="*.md"

# .env files
find "$EXPORT_DIR" -name ".env*" -o -name "*.env"

# Source documents
find "$EXPORT_DIR" -type f \( -name "*.pdf" -o -name "*.epub" -o -name "*.docx" \)

# Large files
find "$EXPORT_DIR" -type f -size +1M

# High-entropy strings (potential API keys)
grep -roiE '[a-zA-Z0-9_-]{32,}' "$EXPORT_DIR" --include="*.py" --include="*.md"
```

### 6. Initialize Local Git (Optional)

```bash
cd "$EXPORT_DIR"
git init
git add .
git commit -m "Initial local export of <skill-name> vX.Y.Z"
```

**Constraints**:
- No remote added
- No push
- If git user not configured, set local config (not global) or document failure reason

### 7. Functionality Check

Verify these files exist:
- README.md, SKILL.md
- scripts/extract_text.py, scripts/build_book_skill.py, scripts/validate_book_skill.py
- references/supported_formats.md
- SECURITY.md, TEST_MATRIX.md, RELEASE_NOTES.md

## Publishing Decision Matrix

| State | Private Repo | Public Repo |
|-------|-------------|-------------|
| No license selected | ✓ Ready | ✗ Needs LICENSE file |
| Contains personal examples | ✓ Ready | ⚠ Review for PII |
| Contains source document excerpts | ✓ Ready | ✗ Remove copyrighted material |
| All scans clean | ✓ Ready | ✓ Ready (with license) |

## Common Pitfalls

1. **Forgetting to exclude `.backup*` directories** — export bloats with old versions
2. **Copying generated book skills** — user's personal knowledge bases should not be published
3. **Missing `.gitignore`** — accidental commit of `.env` or source documents
4. **False positives in secret scan** — words like "secret" in documentation trigger grep; verify context before alarming
5. **License ambiguity** — default "all rights reserved" blocks forks; explicitly choose license for public repos
