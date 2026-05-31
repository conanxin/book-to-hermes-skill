# Layered Safety Validation

Distinguish tool-script behavior risks from source-document content risks when validating generated book skills.

## Problem

`validate_book_skill.py` originally treated `npm install` / `apt install` / `curl` / `wget` found anywhere in generated files as **errors**. This caused false failures when the source document legitimately mentioned these commands (e.g., a build report describing `pnpm install` results).

## Solution: Two-Layer Checking

Introduced in Phase 0-e.

### Layer A — Tool Script Safety (errors)

Check `scripts/*.py` inside the generated skill for actual dangerous calls.

```python
TOOL_DANGEROUS_STRINGS = [
    "pip install", "apt install", "npm install", "install_missing", "--install-missing",
    "curl", "wget", "requests.get", "urllib.request.urlopen",
    "openai.ChatCompletion", "anthropic.Anthropic", "ollama.chat", "litellm.completion",
]
```

If found in executable scripts → **error** (script may auto-install or call APIs).

Generated book skills should never contain `scripts/*.py`; if they do, this is already suspicious.

### Layer B — Content Notices (informational)

Check all `.md` files in the generated skill for strings that may indicate the source document described installation or network operations.

```python
CONTENT_NOTICE_STRINGS = [
    "pip install", "apt install", "npm install", "install_missing", "--install-missing",
    "curl", "wget",
]
```

If found → **content_notice** (not error). The generated skill contains source-derived content mentioning these commands. No script is executing them.

### Output Schema

```json
{
  "ok": true,
  "checked_path": "/path/to/skill",
  "errors": [],
  "warnings": [],
  "content_notices": [
    "Source-derived content contains 'npm install' in ch08-install-result.md"
  ],
  "files": ["SKILL.md", "metadata.json", ...],
  "safety_summary": "PASS_WITH_NOTICES"
}
```

| `safety_summary` | Meaning |
|------------------|---------|
| `PASS` | No errors, no notices |
| `PASS_WITH_NOTICES` | No errors, but source content mentions install/network commands |
| `FAIL` | Errors present (script safety or missing files) |

## Rationale

This is **not** a relaxation of security. It is a correct classification:

- A document *describing* `npm install` is not the same as a script *running* `npm install`
- The former is content; the latter is behavior
- Content notices alert the user to review; behavior errors block the skill

## When to Escalate a Notice to an Error

If a content notice appears in an unexpected location:
- `metadata.json` contains install commands → possible injection
- `source_manifest.md` was tampered with → verify against original source
- Chapter content is clearly not from the source document → investigate provenance

## Verification

```bash
python3 ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/validate_book_skill.py \
  --skill-dir ~/.hermes/skills/books/phase0d-lofi-engine-static-build-report

# Expect: ok=true, errors=[], content_notices may contain entries
```
