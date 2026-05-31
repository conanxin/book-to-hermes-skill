# Private GitHub Push from Local Export

Session: Phase 1-d (2026-05-31)

## Purpose

One-step workflow for creating a private GitHub repository from a local export directory and pushing the existing git history.

## When to Use

- Export directory has been prepared (Phase 1-c complete)
- User wants private GitHub backup
- User explicitly requests private visibility (never public unless confirmed)

## Pre-Flight Checks

```bash
# 1. Verify gh is installed
gh --version

# 2. Verify gh is logged in (do NOT output token)
gh auth status

# 3. Verify working tree is clean
git status

# 4. Verify no existing remotes
git remote -v   # should be empty

# 5. Verify no uncommitted changes
git diff --stat   # should be empty
```

If any check fails, stop and report. Do not proceed without user confirmation.

## One-Step Creation and Push

```bash
cd /path/to/export-directory

# Optional: rename branch to main
# git branch -M main

# Create private repo, add remote, push
gh repo create owner/repo-name \
  --private \
  --source . \
  --remote origin \
  --description "Description here" \
  --push
```

## Post-Push Verification

```bash
# Verify repo visibility is PRIVATE
gh repo view owner/repo-name --json name,visibility,url,defaultBranchRef

# Verify remote configured
git remote -v

# Verify branch tracking
git branch -vv

# Verify working tree still clean
git status
```

Expected output for visibility: `"visibility": "PRIVATE"`

## Security Constraints

- **Never create public repo** unless user explicitly says "make it public"
- **Never output token** in any log or report
- **Never add remote manually** with token in URL
- **Verify visibility** before reporting success
- If repo already exists and is public, **stop** — do not push

## Handling Existing Repo

```bash
# Check if repo exists
gh repo view owner/repo-name 2>&1

# If exists and is private → use it
# If exists and is public → stop, report to user
# If does not exist → create new private repo
```

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `gh auth status` fails | Not logged in | User must run `gh auth login` manually |
| `git status` shows changes | Uncommitted files | `git add . && git commit` first |
| `git remote -v` shows remotes | Already has origin | Report to user, do not overwrite |
| Push rejected | Repo exists with different history | Force push is dangerous — ask user |
| Visibility is PUBLIC | Repo was already public | Stop immediately, report to user |

## Complete Workflow Example

```bash
EXPORT_DIR=~/.hermes/workspace/exports/my-tool
cd "$EXPORT_DIR"

# Pre-flight
git status --short || echo "Clean"
git remote -v || echo "No remotes"

# Create and push
gh repo create conanxin/my-tool \
  --private \
  --source . \
  --remote origin \
  --description "My Hermes tool" \
  --push

# Verify
gh repo view conanxin/my-tool --json name,visibility,url
```

## Related

- `references/github_ready_export.md` — Phase 1-c export preparation
- `github-repo-management` skill — General GitHub repo operations
