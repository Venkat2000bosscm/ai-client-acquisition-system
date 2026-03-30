# Skill: ai-cold-email

**Version:** 1.0.0
**Purpose:** Generate 3 high-converting cold email variations + 1 follow-up for AI consultants and IT agencies, personalized to a target company's niche and pain points.

## Quick Start

```bash
pip install anthropic
export ANTHROPIC_API_KEY=your_key_here

python ../../.skills/ai_cold_email/scripts/generate_emails.py \
  --company-name "NexGen AI Solutions" \
  --website "https://nexgenai.com" \
  --niche "AI consulting" \
  --sender-name "Sarah" \
  --sender-company "LeadFlow AI" \
  --offer "AI-powered lead generation automation" \
  --cta-type "free demo" \
  --output "./output/cold_emails.json"
```

## Inputs

| Parameter          | Required | Default                           | Description                               |
|--------------------|----------|-----------------------------------|-------------------------------------------|
| `--company-name`   | ✅       | —                                 | Target company name                       |
| `--website`        | ✅       | —                                 | Target company website URL                |
| `--niche`          | ✅       | —                                 | Target company's industry                 |
| `--sender-name`    | ❌       | `[Your Name]`                     | Your first name                           |
| `--sender-company` | ❌       | `[Your Company]`                  | Your company name                         |
| `--offer`          | ❌       | `AI-powered lead generation`      | What you're offering                      |
| `--cta-type`       | ❌       | `free demo`                       | `free demo`, `free audit`, `sample leads`, `15-min call`, `case study` |

## Output

3 email variations with unique hooks:

| Hook Type     | Opens With                                      |
|---------------|-------------------------------------------------|
| `pain-point`  | A specific frustration the prospect likely has  |
| `social-proof`| A concrete client result / outcome              |
| `curiosity`   | A thought-provoking question                    |

Plus 1 follow-up email (send day 4).

Each email includes: subject line · body (80–120 words) · P.S. line

## Full Skill Definition

→ See [`.skills/ai_cold_email/SKILL.md`](../../.skills/ai_cold_email/SKILL.md)
