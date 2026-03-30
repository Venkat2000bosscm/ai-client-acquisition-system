# Skill: ai-followup

**Version:** 1.0.0
**Depends on:** `ai-cold-email`
**Purpose:** Generate 2 short, natural follow-up emails for leads who didn't reply to the original cold email. Max 60 words each. Never pushy.

## Quick Start

```bash
pip install anthropic
export ANTHROPIC_API_KEY=your_key_here

python ../../.skills/ai_followup/scripts/generate_followup.py \
  --lead-name "James" \
  --company-name "NexGen AI Solutions" \
  --original-subject "NexGen's lead pipeline — quick thought" \
  --original-body "Hey James, running an AI consulting firm is ironic..." \
  --days-since 4 \
  --sender-name "Sarah" \
  --urgency-type "soft" \
  --output "./output/followup_emails.json"
```

## Inputs

| Parameter            | Required | Default                      | Description                                       |
|----------------------|----------|------------------------------|---------------------------------------------------|
| `--lead-name`        | ❌       | `[First Name]`               | Lead's first name                                 |
| `--company-name`     | ✅       | —                            | Lead's company name                               |
| `--original-subject` | ✅       | —                            | Subject line of the original cold email           |
| `--original-body`    | ✅       | —                            | Body of the original cold email                   |
| `--days-since`       | ❌       | `4`                          | Days elapsed since original email                 |
| `--sender-name`      | ❌       | `[Your Name]`                | Your first name                                   |
| `--urgency-type`     | ❌       | `soft`                       | `soft`, `value`, or `question`                    |

## Output

2 follow-up variations (≤60 words each):

| Variation | Angle    | Description                                         |
|-----------|----------|-----------------------------------------------------|
| A         | Urgency  | Matches `--urgency-type` (soft / value / question)  |
| B         | Reframe  | Empathy or completely different angle from A        |

## Full Skill Definition

→ See [`.skills/ai_followup/SKILL.md`](../../.skills/ai_followup/SKILL.md)
