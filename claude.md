# Claude Global Skills Guide

This document defines how to build, structure, and run reusable **skills** in this project. All contributors (human and AI) should follow these conventions.

---

## What is a Skill?

A skill is a **self-contained, reusable unit of work** defined as a Markdown file. Each skill encapsulates a specific capability — such as scraping a website, transforming data, or calling an API — and can be composed with other skills to build complex workflows.

---

## Directory Structure

```
.skills/
├── SKILL_REGISTRY.md          # Index of all available skills
├── scrape-leads/
│   ├── SKILL.md               # Main skill definition
│   ├── scripts/               # Helper scripts & utilities
│   │   └── scrape.py
│   ├── examples/              # Reference implementations
│   │   └── example_output.json
│   └── resources/             # Templates, configs, assets
│       └── selectors.json
├── enrich-data/
│   ├── SKILL.md
│   └── scripts/
│       └── enrich.py
└── export-csv/
    ├── SKILL.md
    └── scripts/
        └── export.py
```

---

## Skill File Format (`SKILL.md`)

Every skill **must** have a `SKILL.md` file with YAML front matter followed by step-by-step instructions in Markdown.

### Front Matter (Required)

```yaml
---
name: skill-name-in-kebab-case
description: >
  A concise one-liner explaining what this skill does.
version: "1.0.0"
tools:
  - tool_name_1       # Tools this skill requires (e.g., run_command, browser_subagent, grep_search)
  - tool_name_2
inputs:
  - name: input_name
    type: string | number | boolean | file_path | url
    required: true
    description: What this input is for
  - name: optional_input
    type: string
    required: false
    default: "fallback_value"
    description: An optional parameter with a default
outputs:
  - name: output_name
    type: string | file_path | json
    description: What this skill produces
tags:
  - category-tag       # e.g., scraping, data, export, api
  - another-tag
dependencies:
  - other-skill-name   # Skills that must run before this one (if any)
---
```

### Front Matter Fields Reference

| Field          | Required | Description                                                   |
|----------------|----------|---------------------------------------------------------------|
| `name`         | ✅       | Unique kebab-case identifier for the skill                    |
| `description`  | ✅       | One-line summary of the skill's purpose                       |
| `version`      | ✅       | Semantic version (`major.minor.patch`)                        |
| `tools`        | ✅       | List of tools the skill needs to execute                      |
| `inputs`       | ✅       | Typed parameters the skill accepts                            |
| `outputs`      | ✅       | What the skill produces upon completion                       |
| `tags`         | ❌       | Categorical labels for discovery and filtering                |
| `dependencies` | ❌       | Other skills that must complete before this one can run        |

---

## Writing Skill Steps

After the front matter, define the skill's execution steps using clear, numbered Markdown instructions.

### Rules for Steps

1. **Be explicit** — Each step should describe exactly one action. No ambiguity.
2. **Be idempotent** — Running the skill twice should not cause side effects.
3. **Reference inputs with `{{input_name}}`** — Use template placeholders for dynamic values.
4. **Include validation** — Add a verification step at the end confirming success.
5. **Handle errors** — Document what to do if a step fails.

### Example Skill Body

````markdown
## Prerequisites

- Python 3.10+ installed
- `requests` and `beautifulsoup4` packages available

## Steps

### Step 1: Validate Inputs

Confirm that `{{target_url}}` is a valid, reachable URL. If not, abort with a clear error message.

```bash
curl -s -o /dev/null -w "%{http_code}" "{{target_url}}"
```

Expected: HTTP status `200`. If not `200`, stop and report the error.

### Step 2: Run the Scraper

Execute the scraping script with the provided URL:

```bash
python .skills/scrape-leads/scripts/scrape.py --url "{{target_url}}" --output "{{output_path}}"
```

### Step 3: Validate Output

Verify the output file exists and contains valid JSON:

```bash
python -c "import json; json.load(open('{{output_path}}')); print('✅ Valid JSON')"
```

### Step 4: Report Results

Return a summary including:
- Number of records scraped
- Output file path
- Any warnings encountered

## Error Handling

| Error                     | Action                                      |
|---------------------------|---------------------------------------------|
| URL unreachable           | Abort and report connectivity issue          |
| Empty response            | Retry once, then abort with warning          |
| Invalid JSON output       | Log raw output for debugging, abort          |
| Missing dependencies      | List missing packages and install command     |
````

---

## Complete Skill Example

Here is a full, production-ready skill definition:

````markdown
---
name: scrape-leads
description: >
  Scrapes business leads (name, email, phone, website) from a target directory page.
version: "1.0.0"
tools:
  - run_command
  - browser_subagent
inputs:
  - name: target_url
    type: url
    required: true
    description: The URL of the directory page to scrape
  - name: output_path
    type: file_path
    required: false
    default: "./output/leads.json"
    description: Where to save the scraped leads
  - name: max_pages
    type: number
    required: false
    default: 5
    description: Maximum number of pages to paginate through
outputs:
  - name: leads_file
    type: file_path
    description: Path to the JSON file containing scraped leads
  - name: lead_count
    type: number
    description: Total number of leads scraped
tags:
  - scraping
  - leads
  - data-collection
---

## Prerequisites

- Python 3.10+
- Install dependencies: `pip install requests beautifulsoup4 lxml`

## Steps

### Step 1: Validate the Target URL

Confirm `{{target_url}}` returns HTTP 200.

```bash
curl -s -o /dev/null -w "%{http_code}" "{{target_url}}"
```

If status is not `200`, abort with: `"Target URL is unreachable or invalid."`

### Step 2: Execute the Scraper

```bash
python .skills/scrape-leads/scripts/scrape.py \
  --url "{{target_url}}" \
  --output "{{output_path}}" \
  --max-pages {{max_pages}}
```

### Step 3: Validate Output

```bash
python -c "
import json
data = json.load(open('{{output_path}}'))
print(f'✅ Scraped {len(data)} leads')
assert len(data) > 0, 'No leads found — check selectors'
"
```

### Step 4: Return Results

Report:
- `leads_file`: `{{output_path}}`
- `lead_count`: number of records in the JSON file

## Error Handling

| Error                  | Recovery                                         |
|------------------------|--------------------------------------------------|
| URL returns non-200    | Abort, suggest checking the URL manually          |
| Selector mismatch      | Log page HTML snippet, update selectors.json      |
| Rate limiting (429)    | Wait 30s, retry up to 3 times                     |
| Timeout                | Increase timeout to 60s, retry once               |
````

---

## Principles for Building Skills

### 1. Single Responsibility
Each skill does **one thing well**. If a skill is doing too much, split it into smaller skills and use `dependencies` to chain them.

### 2. Reusability
Design skills to work across different contexts. Avoid hardcoding values — use `inputs` for anything that might change.

### 3. Modularity
Skills should be **composable**. Skill A's output should be usable as Skill B's input:

```
scrape-leads → enrich-data → export-csv
```

### 4. Testability
Every skill **must** include a verification step. After creation, always test the skill with real or sample data.

### 5. Documentation
The `SKILL.md` file **is** the documentation. Write it so that someone (or an AI agent) can execute it without additional context.

---

## Skill Registry (`SKILL_REGISTRY.md`)

Maintain a central registry at `.skills/SKILL_REGISTRY.md` listing all available skills:

```markdown
# Skill Registry

| Skill Name      | Description                            | Version | Tags                    |
|-----------------|----------------------------------------|---------|-------------------------|
| scrape-leads    | Scrape business leads from directories | 1.0.0   | scraping, leads         |
| enrich-data     | Enrich leads with additional data      | 1.0.0   | enrichment, api         |
| export-csv      | Export JSON leads to CSV format        | 1.0.0   | export, csv             |
```

---

## Running a Skill

### Manual Execution

1. **Read** the skill: Open `.skills/<skill-name>/SKILL.md`
2. **Provide inputs**: Substitute all `{{input_name}}` placeholders with actual values
3. **Follow steps**: Execute each step in order
4. **Verify**: Confirm the output matches expectations

### AI-Assisted Execution

When asking an AI agent to run a skill:

```
Run the `scrape-leads` skill with:
- target_url: https://example.com/directory
- output_path: ./output/leads.json
- max_pages: 10
```

The agent should:
1. Read `.skills/scrape-leads/SKILL.md`
2. Parse front matter for tool requirements and input validation
3. Execute each step sequentially
4. Validate outputs before reporting results

---

## Testing Skills After Creation

> [!IMPORTANT]
> Every skill **must** be tested immediately after creation. Never ship an untested skill.

### Testing Checklist

- [ ] **Front matter validates** — All required fields present, types correct
- [ ] **Inputs are documented** — Every input has a name, type, and description
- [ ] **Steps execute cleanly** — Run through all steps with sample data
- [ ] **Output is correct** — Verify output format, content, and location
- [ ] **Error handling works** — Intentionally trigger each error case
- [ ] **Idempotency holds** — Run the skill twice; confirm no side effects
- [ ] **Dependencies resolve** — If skill depends on others, run the full chain

### Test Command Template

```bash
# Dry run — validate structure without executing
python -c "
import yaml
with open('.skills/<skill-name>/SKILL.md') as f:
    content = f.read()
    front_matter = content.split('---')[1]
    config = yaml.safe_load(front_matter)
    required = ['name', 'description', 'version', 'tools', 'inputs', 'outputs']
    missing = [f for f in required if f not in config]
    if missing:
        print(f'❌ Missing fields: {missing}')
    else:
        print(f'✅ Skill \"{config[\"name\"]}\" v{config[\"version\"]} is valid')
"
```

---

## Changelog Convention

When updating a skill, increment the version and add a note at the bottom of `SKILL.md`:

```markdown
## Changelog

### 1.1.0 — 2026-03-30
- Added retry logic for rate-limited responses
- Increased default timeout to 60s

### 1.0.0 — 2026-03-28
- Initial release
```
