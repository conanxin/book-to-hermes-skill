# Output Schema

## Directory Structure

```
<output_dir>/<slug>/
├── SKILL.md              # Core skill definition
├── metadata.json         # Machine-readable metadata
├── source_manifest.md    # Source file provenance
├── chapters/             # Per-chapter summaries
│   ├── ch01-<slug>.md
│   ├── ch02-<slug>.md
│   └── ...
├── glossary.md           # Alphabetical term definitions
├── patterns.md           # Techniques and design patterns
└── cheatsheet.md         # Quick reference tables
```

## File Specifications

### SKILL.md

- YAML frontmatter with `name`, `description`, `argument-hint`
- Max 15,000 characters body
- Contains: Purpose, How to use, Core map, Chapter index, Topic index, Loading policy, Safety/limitations
- Does NOT contain: full chapter text, raw source content

### chapters/chNN-<slug>.md

- One file per chapter or major section
- Contains: Core Idea, Key Concepts, Key Takeaways, Connects To
- Technical mode adds: Code Examples

### glossary.md

- Alphabetical list of key terms
- Format: `**Term** — definition`

### patterns.md

- Techniques, algorithms, design patterns
- Format: `## Pattern Name\n**When to use**: ...\n**How**: ...`

### cheatsheet.md

- Decision tables, comparison matrices
- Single-page reference format

### metadata.json

```json
{
  "title": "string",
  "slug": "string",
  "language": "string",
  "mode": "string",
  "source_path": "string",
  "created_at": "ISO-8601 timestamp",
  "char_count": 0,
  "chapter_count": 0,
  "generator": "book-to-hermes-skill",
  "phase": "0-b"
}
```

### source_manifest.md

- Source file path and format
- Extraction method used
- Generation timestamp
- Known limitations
- Verification instructions (checksum)
