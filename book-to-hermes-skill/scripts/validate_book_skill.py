#!/usr/bin/env python3
"""
Validate a generated Hermes book skill directory.

Checks:
  - Required files exist and are non-empty
  - metadata.json is valid JSON
  - chapters/ exists with at least 1 file
  - SKILL.md does not contain full source text
  - SKILL.md character count is under budget
  - Tool script safety (no dangerous calls in scripts/)
  - Content notices for source-derived dangerous strings

Output: JSON to stdout.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

MAX_SKILL_MD_CHARS = 15000
REQUIRED_FILES = ["SKILL.md", "metadata.json", "source_manifest.md", "glossary.md", "patterns.md", "cheatsheet.md"]

# Strings that indicate actual dangerous behavior when found in executable scripts
TOOL_DANGEROUS_STRINGS = [
    "pip install", "apt install", "npm install", "install_missing", "--install-missing",
    "curl", "wget", "requests.get", "urllib.request.urlopen",
    "openai.ChatCompletion", "anthropic.Anthropic", "ollama.chat", "litellm.completion",
]

# Strings that may appear in source-derived content (not script execution)
CONTENT_NOTICE_STRINGS = [
    "pip install", "apt install", "npm install", "install_missing", "--install-missing",
    "curl", "wget",
]


def validate(skill_dir: str) -> dict:
    path = Path(skill_dir)
    errors = []
    warnings = []
    content_notices = []
    files_found = []

    if not path.exists():
        return {"ok": False, "checked_path": str(path), "errors": [f"Directory does not exist: {skill_dir}"]}
    if not path.is_dir():
        return {"ok": False, "checked_path": str(path), "errors": [f"Not a directory: {skill_dir}"]}

    # Check required files
    for fname in REQUIRED_FILES:
        fpath = path / fname
        if not fpath.exists():
            errors.append(f"Missing required file: {fname}")
        elif not fpath.is_file():
            errors.append(f"Not a file: {fname}")
        elif fpath.stat().st_size == 0:
            errors.append(f"Empty file: {fname}")
        else:
            files_found.append(fname)

    # Check chapters directory
    chapters_dir = path / "chapters"
    if not chapters_dir.exists():
        errors.append("Missing chapters/ directory")
    elif not chapters_dir.is_dir():
        errors.append("chapters/ is not a directory")
    else:
        chapter_files = sorted(chapters_dir.glob("ch*.md"))
        if not chapter_files:
            errors.append("No chapter files found in chapters/")
        else:
            files_found.append(f"chapters/ ({len(chapter_files)} files)")

    # Validate metadata.json
    meta_path = path / "metadata.json"
    if meta_path.exists():
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            required_keys = ["title", "slug", "language", "mode", "source_path", "created_at", "char_count", "chapter_count", "generator", "phase"]
            for key in required_keys:
                if key not in meta:
                    warnings.append(f"metadata.json missing key: {key}")
        except json.JSONDecodeError as e:
            errors.append(f"metadata.json is invalid JSON: {e}")

    # Validate SKILL.md
    skill_md_path = path / "SKILL.md"
    if skill_md_path.exists():
        text = skill_md_path.read_text(encoding="utf-8")
        if len(text) > MAX_SKILL_MD_CHARS:
            warnings.append(f"SKILL.md exceeds char budget: {len(text)} > {MAX_SKILL_MD_CHARS}")
        lines = text.splitlines()
        if len(lines) > 300:
            warnings.append(f"SKILL.md has many lines ({len(lines)}), may contain full source text")
        if text.count("<") > 50:
            warnings.append("SKILL.md contains many placeholders, may need LLM filling")

    # Scan generated markdown files for content notices (source-derived strings)
    for md_file in path.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        for notice in CONTENT_NOTICE_STRINGS:
            if notice.lower() in content.lower():
                content_notices.append(f"Source-derived content contains '{notice}' in {md_file.name}")

    # Scan for scripts in the skill directory (should not exist in generated skills)
    scripts_dir = path / "scripts"
    if scripts_dir.exists():
        for script_file in scripts_dir.rglob("*.py"):
            content = script_file.read_text(encoding="utf-8")
            for danger in TOOL_DANGEROUS_STRINGS:
                if danger.lower() in content.lower():
                    errors.append(f"Dangerous string '{danger}' found in generated script: {script_file.name}")

    ok = len(errors) == 0
    safety_summary = "PASS" if ok else "FAIL"
    if content_notices and ok:
        safety_summary = "PASS_WITH_NOTICES"

    return {
        "ok": ok,
        "checked_path": str(path.resolve()),
        "errors": errors,
        "warnings": warnings,
        "content_notices": content_notices,
        "files": files_found,
        "safety_summary": safety_summary,
    }


def main():
    parser = argparse.ArgumentParser(description="Validate a Hermes book skill directory")
    parser.add_argument("--skill-dir", required=True, help="Path to skill directory")
    args = parser.parse_args()

    result = validate(args.skill_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
