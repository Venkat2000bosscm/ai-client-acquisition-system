---
name: ai-lead-generator
description: >
  Generate high-quality business leads for AI consultants, software agencies, and IT service companies
  across configurable niches and locations.
version: "1.0.0"
tools:
  - run_command
  - browser_subagent
  - search_web
inputs:
  - name: niche
    type: string
    required: true
    description: >
      The business niche to search for.
      Examples: "AI consulting", "software development agency", "IT managed services",
      "machine learning consulting", "data engineering services"
  - name: locations
    type: string
    required: false
    default: "US, UK, India"
    description: >
      Comma-separated list of target locations/countries.
      Examples: "US, UK, India" or "New York, London, Bangalore"
  - name: max_results
    type: number
    required: false
    default: 50
    description: Maximum number of leads to generate per location
  - name: output_format
    type: string
    required: false
    default: "json"
    description: Output format — "json", "csv", or "both"
  - name: output_path
    type: file_path
    required: false
    default: "./output/leads"
    description: Base path for output files (extension added automatically)
outputs:
  - name: leads_file
    type: file_path
    description: Path to the generated leads file (JSON and/or CSV)
  - name: lead_count
    type: number
    description: Total number of qualified leads found
  - name: summary
    type: string
    description: Breakdown of leads by location and quality score
tags:
  - leads
  - scraping
  - ai-consulting
  - business-development
  - data-collection
---

## Prerequisites

- Python 3.10+
- Install dependencies:

```bash
pip install requests beautifulsoup4 lxml tqdm
```

## Steps

### Step 1: Install Dependencies

```bash
pip install -r .skills/ai_lead_generator/scripts/requirements.txt
```

### Step 2: Validate Inputs

Confirm that `{{niche}}` is a non-empty string and `{{locations}}` contains valid location names.

```bash
python .skills/ai_lead_generator/scripts/lead_generator.py --validate-only --niche "{{niche}}" --locations "{{locations}}"
```

Expected: `✅ Inputs validated successfully`. If validation fails, stop and fix inputs.

### Step 3: Run Lead Generation

Execute the lead generator with the configured parameters:

```bash
python .skills/ai_lead_generator/scripts/lead_generator.py \
  --niche "{{niche}}" \
  --locations "{{locations}}" \
  --max-results {{max_results}} \
  --output-format "{{output_format}}" \
  --output-path "{{output_path}}"
```

This will:
1. Search for businesses matching `{{niche}}` in each location
2. Extract company name, website, contact email, and LinkedIn profile
3. Score and filter leads by relevance and activity
4. Save results to the specified output path

### Step 4: Validate Output

```bash
python .skills/ai_lead_generator/scripts/lead_generator.py --verify "{{output_path}}"
```

Expected: Summary table with lead count, completeness scores, and location breakdown.

### Step 5: Review Results

Open the output file and review the structured table:

| Field            | Description                                  |
|------------------|----------------------------------------------|
| company_name     | Full registered company name                 |
| website          | Company website URL                          |
| contact_email    | Primary contact or info email (if found)     |
| linkedin_url     | Company LinkedIn profile URL (if found)      |
| location         | Country or city of the business              |
| niche            | The matched niche/industry                   |
| relevance_score  | 1–10 score based on niche match              |
| status           | "active" / "inactive" / "unverified"         |
| source           | Where the lead was found                     |
| scraped_at       | ISO timestamp of when the lead was generated |

## Error Handling

| Error                         | Recovery                                              |
|-------------------------------|-------------------------------------------------------|
| Rate limited (HTTP 429)       | Exponential backoff, retry up to 3 times              |
| No results for a location     | Log warning, continue with other locations             |
| Email not found               | Mark as empty, do not fabricate                        |
| Invalid niche keyword         | Suggest similar niches from predefined list            |
| Network timeout               | Retry with 30s timeout, abort after 3 failures        |
| Output directory not writable | Create directory or prompt for alternative path        |

## Usage Examples

### Example 1: Default (AI Consulting in US, UK, India)

```bash
python .skills/ai_lead_generator/scripts/lead_generator.py \
  --niche "AI consulting" \
  --locations "US, UK, India"
```

### Example 2: Custom Niche and Locations

```bash
python .skills/ai_lead_generator/scripts/lead_generator.py \
  --niche "cloud migration services" \
  --locations "Germany, Canada, Australia" \
  --max-results 30 \
  --output-format both
```

### Example 3: Narrow Location Focus

```bash
python .skills/ai_lead_generator/scripts/lead_generator.py \
  --niche "data engineering agency" \
  --locations "San Francisco, London, Hyderabad" \
  --max-results 20 \
  --output-format csv
```

## Changelog

### 1.0.0 — 2026-03-30
- Initial release
- Multi-niche, multi-location lead generation
- JSON and CSV output support
- Relevance scoring and activity filtering
