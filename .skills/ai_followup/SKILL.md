---
name: ai-followup
description: >
  Generate 2 short, natural follow-up email variations for leads who didn't reply to a previous outreach email.
version: "1.0.0"
tools:
  - claude-api
inputs:
  - name: lead_name
    type: string
    required: false
    default: "[First Name]"
    description: First name of the lead being followed up with
  - name: company_name
    type: string
    required: true
    description: Name of the lead's company
  - name: original_email_subject
    type: string
    required: true
    description: Subject line of the original cold email that went unanswered
  - name: original_email_body
    type: string
    required: true
    description: Body text of the original cold email (used to maintain context)
  - name: days_since_first_email
    type: number
    required: false
    default: 4
    description: How many days have passed since the original email was sent
  - name: sender_name
    type: string
    required: false
    default: "[Your Name]"
    description: Sender's first name
  - name: offer
    type: string
    required: false
    default: "AI-powered lead generation automation"
    description: The product or service originally offered
  - name: urgency_type
    type: string
    required: false
    default: "soft"
    description: >
      Type of urgency to add:
      "soft" (limited spots / timing),
      "value" (new proof point / stat),
      "question" (open a loop with a direct question)
  - name: output_path
    type: file_path
    required: false
    default: "./output/followup_emails.json"
    description: Where to save the generated follow-up emails
outputs:
  - name: emails_file
    type: file_path
    description: JSON file containing 2 follow-up email variations
  - name: email_count
    type: number
    description: Always 2
tags:
  - email
  - follow-up
  - outreach
  - lead-nurture
  - ai-consulting
dependencies:
  - ai-cold-email
---

## Prerequisites

- Python 3.10+
- `anthropic` package: `pip install anthropic`
- `ANTHROPIC_API_KEY` environment variable set
- A previous cold email that received no reply (use `ai-cold-email` skill first)

## Overview

This skill generates **2 follow-up email variations** for leads who haven't
responded to the original outreach. Each follow-up is:

- Under 60 words — short enough to feel like a quick ping, not a second pitch
- Aware of the original email context — references it without copy-pasting it
- Non-pushy — never guilts, never demands, never uses "just checking in"
- Ends with a single low-friction ask

### Urgency Type Guide

| Type       | What it does                                                        |
|------------|---------------------------------------------------------------------|
| `soft`     | Mentions limited availability or a time-sensitive angle             |
| `value`    | Adds a new stat, result, or insight not in the original email       |
| `question` | Opens a direct question to re-engage curiosity                      |

---

## Steps

### Step 1: Validate Inputs

Confirm `original_email_body` is non-empty and `days_since_first_email` is a positive number.

```bash
python -c "
body = '''{{original_email_body}}'''
days = {{days_since_first_email}}
assert body.strip(), 'original_email_body cannot be empty'
assert days > 0, 'days_since_first_email must be > 0'
print('✅ Inputs valid')
"
```

### Step 2: Generate Follow-ups via Claude API

```bash
python .skills/ai_followup/scripts/generate_followup.py \
  --lead-name "{{lead_name}}" \
  --company-name "{{company_name}}" \
  --original-subject "{{original_email_subject}}" \
  --original-body "{{original_email_body}}" \
  --days-since "{{days_since_first_email}}" \
  --sender-name "{{sender_name}}" \
  --offer "{{offer}}" \
  --urgency-type "{{urgency_type}}" \
  --output "{{output_path}}"
```

The script prompts Claude to produce exactly 2 follow-up variations:

- **Variation A** — Leads with the urgency type specified (`{{urgency_type}}`)
- **Variation B** — Uses a different angle from Variation A (always a question or empathy reframe)

### Follow-up Writing Rules (enforced in prompt)

- Max **60 words** per body
- Never start with: "Just checking in", "Following up", "I wanted to circle back", "Per my last email", "Did you get a chance"
- Acknowledge the silence naturally — don't guilt-trip
- Reference the original email briefly (one line max)
- One CTA: the lowest-friction version possible (a "yes/no", not a meeting request)
- Subject line: reply-thread style (`Re:`) or a fresh curiosity line — never clickbait

### Step 3: Validate Output

```bash
python -c "
import json
data = json.load(open('{{output_path}}'))
assert 'variations' in data and len(data['variations']) == 2, 'Expected 2 variations'
for v in data['variations']:
    assert all(k in v for k in ['id', 'subject', 'body']), f'Missing fields in variation'
    word_count = len(v['body'].split())
    assert word_count <= 80, f'Body too long: {word_count} words (max 80)'
print('✅ 2 follow-up variations generated and validated')
"
```

### Step 4: Report Results

Return:
- `emails_file`: `{{output_path}}`
- `email_count`: `2`
- Print both subject lines and word counts in the response

---

## Output Schema

```json
{
  "lead_name": "{{lead_name}}",
  "company_name": "{{company_name}}",
  "days_since_first_email": 4,
  "urgency_type": "{{urgency_type}}",
  "original_subject": "{{original_email_subject}}",
  "generated_at": "ISO-8601 timestamp",
  "variations": [
    {
      "id": "A",
      "angle": "urgency | value | question",
      "subject": "Email subject line",
      "body": "Short follow-up body (≤60 words)",
      "word_count": 48
    },
    {
      "id": "B",
      "angle": "empathy | reframe | question",
      "subject": "Email subject line",
      "body": "Short follow-up body (≤60 words)",
      "word_count": 52
    }
  ]
}
```

---

## Error Handling

| Error                        | Action                                                  |
|------------------------------|---------------------------------------------------------|
| Missing `ANTHROPIC_API_KEY`  | Abort, print: `export ANTHROPIC_API_KEY=your_key_here` |
| Empty `original_email_body`  | Abort with message: provide the original email body     |
| Response too long (>80 words)| Retry with stricter word-count instruction in prompt    |
| JSON parse error             | Strip markdown fences, retry once                       |
| Rate limit                   | Backoff 10s × attempt, retry up to 3 times              |

---

## Example Usage

```
Run the `ai-followup` skill with:
- lead_name: "James"
- company_name: "NexGen AI Solutions"
- original_email_subject: "NexGen's lead pipeline — quick thought"
- original_email_body: "Hey James, running an AI consulting firm is ironic..."
- days_since_first_email: 4
- sender_name: "Sarah"
- offer: "AI-powered lead generation automation"
- urgency_type: "soft"
```

---

## Changelog

### 1.0.0 — 2026-03-30
- Initial release
- Supports 3 urgency types: soft, value, question
- Enforces 60-word max per follow-up body
- Validates word count post-generation
