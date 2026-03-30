# AI Leads Scraper

An automated AI-powered client acquisition pipeline for AI consultants, agencies, and IT companies. Finds qualified leads, writes personalized cold emails, and generates follow-ups — all powered by Claude.

```
ai-lead-generator  →  ai-cold-email  →  ai-followup
   (find leads)       (write emails)    (no-reply nudge)
```

---

## What It Does

| Step | Skill | What Happens |
|------|-------|-------------|
| 1 | `ai-lead-generator` | Searches for businesses by niche + location, scores them 1–10, exports to JSON/CSV |
| 2 | `ai-cold-email` | Writes 3 cold email variations + 1 built-in follow-up per lead |
| 3 | `ai-followup` | Generates 2 short follow-ups for leads who haven't replied |

---

## Project Structure

```
AI-LEADS-SCAPPER/
│
├── .skills/                        # Executable skill definitions + scripts
│   ├── SKILL_REGISTRY.md           # Index of all available skills
│   ├── ai_lead_generator/
│   │   ├── SKILL.md
│   │   └── scripts/lead_generator.py
│   ├── ai_cold_email/
│   │   ├── SKILL.md
│   │   └── scripts/generate_emails.py
│   └── ai_followup/
│       ├── SKILL.md
│       └── scripts/generate_followup.py
│
├── ai-client-acquisition-system/   # Full documentation, prompts & examples
│   ├── README.md                   # Detailed usage guide
│   ├── skills/                     # Per-skill quick-start guides
│   ├── prompts/templates.txt       # Copy-paste Claude prompts
│   └── examples/sample_outputs.md # Real email examples
│
├── output/                         # Generated leads and emails land here
│   ├── leads.json / leads.csv
│   └── ...
│
└── README.md                       # This file
```

---

## Prerequisites

```bash
pip install requests beautifulsoup4 lxml tqdm anthropic
export ANTHROPIC_API_KEY=your_key_here
```

---

## Quick Start

### Step 1 — Generate Leads

```bash
python .skills/ai_lead_generator/scripts/lead_generator.py \
  --niche "AI consulting" \
  --locations "US" \
  --max-results 20 \
  --output-format both \
  --output-path ./output/leads
```

Output: `./output/leads.json` and `./output/leads.csv`

### Step 2 — Write Cold Emails

```bash
python .skills/ai_cold_email/scripts/generate_emails.py \
  --company-name "Acme Corp" \
  --website "https://acmecorp.com" \
  --niche "AI consulting" \
  --sender-name "Sarah" \
  --sender-company "LeadFlow AI" \
  --cta-type "free audit" \
  --output ./output/cold_emails.json
```

Output: `./output/cold_emails.json` — 3 variations + 1 built-in follow-up

### Step 3 — Follow Up (after no reply)

```bash
python .skills/ai_followup/scripts/generate_followup.py \
  --lead-name "James" \
  --company-name "Acme Corp" \
  --original-subject "Quick thought for Acme" \
  --original-body "Hey James, ..." \
  --days-since 4 \
  --sender-name "Sarah" \
  --urgency-type "soft" \
  --output ./output/followup_emails.json
```

Output: `./output/followup_emails.json` — 2 follow-up variations

---

## Email Sequence Strategy

Each lead receives up to **5 touchpoints**:

```
Day 0  →  Cold Email        (1 of 3 variations from ai-cold-email)
Day 4  →  Built-in Follow-up (included in ai-cold-email output)
Day 8  →  Follow-up A        (ai-followup, urgency angle)
Day 12 →  Follow-up B        (ai-followup, reframe angle)
Day 16 →  Break-up email     (manual — "closing your file")
```

---

## CTA Options (ai-cold-email)

| CTA Type | Best For |
|----------|----------|
| `free demo` | SaaS tools, platforms |
| `free audit` | Agencies, consultants |
| `sample leads` | Lead gen services |
| `15-min call` | High-ticket consulting |
| `case study` | Data-driven buyers |

---

## Urgency Types (ai-followup)

| Type | What It Adds | When To Use |
|------|-------------|-------------|
| `soft` | Limited spots / timing window | Day 4 |
| `value` | New stat or client result | Day 8 |
| `question` | Direct yes/no opener | Day 12 |

---

## Available Skills

See [`.skills/SKILL_REGISTRY.md`](.skills/SKILL_REGISTRY.md) for the full skill index.

| Skill | Description | Version |
|-------|-------------|---------|
| `ai-lead-generator` | Find qualified leads by niche + location | 1.0.0 |
| `ai-cold-email` | Write 3 cold email variations + 1 follow-up | 1.0.0 |
| `ai-followup` | Write 2 short follow-ups for no-reply leads | 1.0.0 |

---

## Detailed Documentation

Full usage guides, prompt templates, and real email examples are in:

→ [`ai-client-acquisition-system/README.md`](ai-client-acquisition-system/README.md)
