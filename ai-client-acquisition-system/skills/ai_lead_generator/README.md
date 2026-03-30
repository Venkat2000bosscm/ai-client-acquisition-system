# Skill: ai-lead-generator

**Version:** 1.0.0
**Purpose:** Generate qualified business leads (company name, website, email, LinkedIn) for AI consultants and IT agencies across configurable niches and locations.

## Quick Start

```bash
pip install requests beautifulsoup4 lxml tqdm

python ../../.skills/ai_lead_generator/scripts/lead_generator.py \
  --niche "AI consulting" \
  --locations "US, UK, India" \
  --max-results 50 \
  --output-format both \
  --output "./output/leads"
```

## Inputs

| Parameter       | Required | Default          | Description                         |
|-----------------|----------|------------------|-------------------------------------|
| `--niche`       | ✅       | —                | Target industry (e.g. "AI consulting") |
| `--locations`   | ❌       | `US, UK, India`  | Comma-separated countries/cities    |
| `--max-results` | ❌       | `50`             | Max leads per location              |
| `--output-format` | ❌     | `json`           | `json`, `csv`, or `both`            |
| `--output-path` | ❌       | `./output/leads` | Base output path (no extension)     |

## Output Fields

`company_name` · `website` · `contact_email` · `linkedin_url` · `location` · `niche` · `relevance_score` (1–10) · `status` · `source` · `scraped_at`

## Full Skill Definition

→ See [`.skills/ai_lead_generator/SKILL.md`](../../.skills/ai_lead_generator/SKILL.md)
