---
name: {{slug}}
description: "Knowledge base from \"{{title}}\". Use when applying its frameworks, studying its concepts, or referencing its techniques."
argument-hint: [topic, framework name, or chapter number]
---

# {{title}}
**Generated**: {{date}} | **Chapters**: {{chapter_count}} | **Mode**: {{mode}} | **Language**: {{language}}

## Purpose

This skill provides structured access to the knowledge in *{{title}}*. It is designed for on-demand loading: only the core map and requested chapter are loaded into context.

## How to Use This Skill

- **Without arguments** — load the core map and chapter index for reference
- **With a topic** — ask about a concept; the relevant chapter loads on demand
- **With a chapter** — ask for `ch05` to load that specific chapter
- **Browse** — ask "what chapters do you have?" to see the full index

## Core Map

<!-- Key mental models and principles extracted from the source -->

## Chapter Index

| # | Title | Key Frameworks |
|---|-------|----------------|
{{chapter_table}}

## Topic Index

{{topic_index}}

## Loading Policy

- SKILL.md (this file) is always loaded first (~400-4,000 tokens)
- Individual chapter files are loaded only when referenced (~800-1,200 tokens each)
- Glossary, patterns, and cheatsheet are loaded on explicit request
- The full source text is never loaded into context

## Safety / Limitations

- This skill covers the source document only.
- For hands-on implementation, combine with project-specific tools.
- Generated content may contain placeholders (`<...>`) that require manual review or LLM filling in later phases.

## Supporting Files

- [glossary.md](glossary.md) — key terms and definitions
- [patterns.md](patterns.md) — techniques and design patterns
- [cheatsheet.md](cheatsheet.md) — quick reference and decision tables
