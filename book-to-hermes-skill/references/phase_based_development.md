# Phase-Based Development with Strict Boundaries

This reference captures the execution pattern used across Phases 0-f through 0-h-real. It is the user's preferred mode for multi-session tool development.

---

## Phase Structure

Each phase has a single, narrowly scoped objective. Phases do not overlap in scope.

| Phase | Typical Scope | Deliverable |
|-------|---------------|-------------|
| 0-X | Feature implementation | Working code + smoke test |
| 0-X-real | Real document validation | End-to-end test with user data |
| 0-g | Precheck / audit | Design document, no install |
| 0-f-resume | Interrupted phase completion | Final report, quality gate |

---

## Strict Boundary Rules

These are non-negotiable for every phase unless explicitly approved:

| Boundary | Rule | Exception |
|----------|------|-----------|
| Install | No apt / pip / npm install | User must explicitly approve each package |
| Network | No HTTP requests, no downloads | Only pip install during approved window |
| LLM | No OpenAI / Anthropic / Ollama / LiteLLM | None |
| Config | No ~/.hermes/config.yaml changes | None |
| Gateway | No Hermes gateway restart | None |
| Systemd | No service modifications | None |
| Cloud | No writes to cloud Hermes | None |
| Secrets | No reading or outputting secret files | None |

---

## Checkpoint Pattern

Before any significant change:

1. **Backup** the tool directory with timestamp: `.backup-phase<name>-YYYYMMDD-HHMMSS`
2. **Report current state** — do not proceed without user confirmation if state is unclear
3. **Validate** after every change — `validate_book_skill.py` must PASS
4. **Commit** only after validation — user says "可以提交" before any git push

---

## Quality Gates

Every phase must pass these gates before reporting completion:

| Gate | Check | Tool |
|------|-------|------|
| Validate | 0 errors, 0 warnings | `validate_book_skill.py` |
| Size | SKILL.md < 15,000 chars | `wc -c` |
| Metadata | metadata.json valid JSON | `python3 -c "import json; json.load(...)` |
| Placeholders | No `<...>`, TODO, PLACEHOLDER, TBD | `grep` |
| Security | No pip/apt/curl/wget/requests in scripts | `grep` |
| Glossary | ≤30 terms (project-docs) or ≤40 (technical) | `wc -l glossary.md` |
| Topic Index | No status words (成功/无/是/否/PASS/FAIL/OK) | `grep` |
| Key Points | No raw Markdown table syntax (`|...|`) | `grep` |

---

## Resume Pattern

When a phase is interrupted (tool loop limit, context window, user break):

1. Read the phase report to understand what completed
2. Create a new `.backup-phase<name>-resume-YYYYMMDD-HHMMSS`
3. Identify the exact remaining tasks from the report
4. Do not restart the phase — resume from the interruption point
5. Final report should reference both the original and resume phases

---

## Report Template

Every phase produces a report at:
`~/.hermes/workspace/reports/book_to_skill/HERMES_BOOK_TO_SKILL_PHASE<NAME>_REPORT.md`

Required sections:
1. STATUS: PASS / PARTIAL / FAIL
2. Phase: name
3. Modified files list
4. Backup path
5. Implementation details
6. Validate results
7. Quality check results
8. Security scan results
9. Unmodified items confirmation
10. Known issues
11. Next phase suggestion

---

*Reference created: 2026-05-31*
*Applies to: book-to-hermes-skill and similar multi-phase tool development*
