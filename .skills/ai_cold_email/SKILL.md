---
name: ai-cold-email
description: >
  Generate 3 high-converting cold email variations + 1 follow-up for AI consultants and IT agencies, personalized to a target company's pain points.
version: "1.0.0"
tools:
  - claude-api
inputs:
  - name: company_name
    type: string
    required: true
    description: Name of the target company to email
  - name: website
    type: url
    required: true
    description: Target company's website URL (used to infer context and pain points)
  - name: niche
    type: string
    required: true
    description: >
      The target company's industry or niche (e.g., "AI consulting", "IT staffing",
      "SaaS", "digital marketing agency", "e-commerce")
  - name: sender_name
    type: string
    required: false
    default: "[Your Name]"
    description: The sender's name to sign the emails with
  - name: sender_company
    type: string
    required: false
    default: "[Your Company]"
    description: The sender's company name
  - name: offer
    type: string
    required: false
    default: "AI-powered lead generation automation"
    description: The specific product or service being offered
  - name: cta_type
    type: string
    required: false
    default: "free demo"
    description: >
      Type of call-to-action: "free demo", "free audit", "sample leads",
      "15-min call", or "case study"
  - name: output_path
    type: file_path
    required: false
    default: "./output/cold_emails.json"
    description: Where to save the generated emails
outputs:
  - name: emails_file
    type: file_path
    description: JSON file containing 3 email variations and 1 follow-up
  - name: email_count
    type: number
    description: Total emails generated (always 4 — 3 variations + 1 follow-up)
tags:
  - email
  - outreach
  - cold-email
  - ai-consulting
  - lead-generation
  - copywriting
dependencies: []
---

## Prerequisites

- Python 3.10+
- `anthropic` package: `pip install anthropic`
- `ANTHROPIC_API_KEY` environment variable set

## Overview

This skill uses Claude to generate personalized, high-converting cold emails
for AI consultants and IT agencies. It produces **3 email variations** with
different hooks/angles plus **1 follow-up email**, all tailored to the target
company's likely pain points based on their niche.

### Pain Point Mapping by Niche

| Niche                  | Common Pain Points                                              |
|------------------------|-----------------------------------------------------------------|
| AI consulting          | Client acquisition, differentiating from competitors, scaling  |
| IT staffing            | Finding qualified candidates, client churn, slow pipelines     |
| Digital marketing      | Demonstrating ROI, retaining clients, scaling outreach         |
| SaaS                   | Churn reduction, onboarding, trial-to-paid conversion          |
| E-commerce             | Cart abandonment, repeat purchases, customer LTV               |
| General IT agency      | Lead flow, proposal-to-close rate, recurring revenue           |

---

## Steps

### Step 1: Validate Inputs

Confirm that required inputs are present and `{{website}}` appears to be a valid URL.

```bash
python -c "
from urllib.parse import urlparse
url = '{{website}}'
result = urlparse(url)
assert result.scheme in ('http', 'https') and result.netloc, 'Invalid URL'
print('✅ Inputs valid')
"
```

If the URL is invalid, abort with: `"Invalid website URL. Provide a full URL including https://"`

### Step 2: Generate Emails via Claude API

Run the generation script:

```bash
python .skills/ai_cold_email/scripts/generate_emails.py \
  --company-name "{{company_name}}" \
  --website "{{website}}" \
  --niche "{{niche}}" \
  --sender-name "{{sender_name}}" \
  --sender-company "{{sender_company}}" \
  --offer "{{offer}}" \
  --cta-type "{{cta_type}}" \
  --output "{{output_path}}"
```

The script instructs Claude to:
1. Identify 2–3 likely pain points for a company in `{{niche}}`
2. Write **Email Variation 1** — Pain-point hook (leads with a specific problem)
3. Write **Email Variation 2** — Social proof / results hook (leads with an outcome)
4. Write **Email Variation 3** — Curiosity / question hook (opens with a provocative question)
5. Write **Follow-up Email** — Sends 3–5 days after the first email, references the prior outreach, adds new value

### Email Writing Rules (enforced in prompt)

- **Tone**: Friendly, conversational, peer-to-peer — never robotic or corporate
- **Length**: 80–120 words per email body (short enough to read on mobile)
- **Personalization**: Reference `{{company_name}}` and `{{niche}}` naturally
- **No spam triggers**: Avoid "synergy", "leverage", "circle back", "touch base"
- **One CTA only**: Every email ends with exactly one clear `{{cta_type}}` ask
- **Subject line**: Each variation gets a unique, curiosity-driven subject line (< 50 chars)
- **P.S. line**: Each variation includes an optional P.S. that reinforces the value prop

### Step 3: Validate Output

```bash
python -c "
import json
data = json.load(open('{{output_path}}'))
assert 'variations' in data and len(data['variations']) == 3, 'Expected 3 variations'
assert 'follow_up' in data, 'Missing follow-up email'
for i, v in enumerate(data['variations']):
    assert all(k in v for k in ['subject', 'body', 'ps']), f'Variation {i+1} missing fields'
print(f'✅ Generated {len(data[\"variations\"])} variations + 1 follow-up')
"
```

### Step 4: Report Results

Return:
- `emails_file`: `{{output_path}}`
- `email_count`: `4`
- Preview the subject lines of all 4 emails in the response

---

## Output Schema

```json
{
  "company_name": "{{company_name}}",
  "website": "{{website}}",
  "niche": "{{niche}}",
  "identified_pain_points": ["pain point 1", "pain point 2", "pain point 3"],
  "offer": "{{offer}}",
  "cta_type": "{{cta_type}}",
  "generated_at": "ISO-8601 timestamp",
  "variations": [
    {
      "id": 1,
      "hook_type": "pain-point",
      "subject": "Email subject line",
      "body": "Full email body text",
      "ps": "P.S. line"
    },
    {
      "id": 2,
      "hook_type": "social-proof",
      "subject": "Email subject line",
      "body": "Full email body text",
      "ps": "P.S. line"
    },
    {
      "id": 3,
      "hook_type": "curiosity",
      "subject": "Email subject line",
      "body": "Full email body text",
      "ps": "P.S. line"
    }
  ],
  "follow_up": {
    "send_after_days": 4,
    "subject": "Follow-up subject line",
    "body": "Full follow-up email body",
    "ps": "P.S. line"
  }
}
```

---

## Error Handling

| Error                        | Action                                                    |
|------------------------------|-----------------------------------------------------------|
| Missing `ANTHROPIC_API_KEY`  | Abort, print: `export ANTHROPIC_API_KEY=your_key_here`   |
| Invalid URL format           | Abort with validation message, ask user to fix URL        |
| Claude API rate limit        | Wait 10s, retry up to 3 times with exponential backoff    |
| Output directory missing     | Auto-create `./output/` directory before writing          |
| JSON parse error             | Log raw Claude response, retry once with stricter prompt  |

---

## Example Usage

```
Run the `ai-cold-email` skill with:
- company_name: "NexGen AI Solutions"
- website: https://nexgenai.com
- niche: "AI consulting"
- sender_name: "Sarah"
- sender_company: "LeadFlow AI"
- offer: "AI-powered lead generation automation"
- cta_type: "free demo"
```

---

## Changelog

### 1.0.0 — 2026-03-30
- Initial release
- Supports 3 email variation hooks: pain-point, social-proof, curiosity
- Includes follow-up email generation
- Pain point auto-detection by niche
