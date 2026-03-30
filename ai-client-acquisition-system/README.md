# AI Client Acquisition System

An automated pipeline for AI consultants and IT agencies to find prospects, write personalized cold emails, and follow up with leads who haven't replied — all powered by Claude.

```
ai-lead-generator  →  ai-cold-email  →  ai-followup
   (find leads)       (write emails)    (no-reply nudge)
```

---

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                    PIPELINE OVERVIEW                            │
│                                                                 │
│  STEP 1            STEP 2               STEP 3                  │
│                                                                 │
│  ai-lead-generator → ai-cold-email  →  ai-followup             │
│                                                                 │
│  • Search for       • 3 email            • 2 follow-up          │
│    companies by       variations           variations           │
│    niche + location   (pain-point,         (≤60 words)          │
│  • Extract website    social-proof,      • Soft urgency,        │
│    & email            curiosity)           value add, or        │
│  • Score 1–10       • 1 built-in           question angle       │
│  • Output JSON/CSV    follow-up          • Never pushy          │
│                     • 80–120 words                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Skills

| Skill | Purpose | Output |
|-------|---------|--------|
| [ai_lead_generator](skills/ai_lead_generator/README.md) | Find qualified leads by niche + location | `leads.json` / `leads.csv` |
| [ai_cold_email](skills/ai_cold_email/README.md) | Write 3 cold email variations + 1 follow-up | `cold_emails.json` |
| [ai_followup](skills/ai_followup/README.md) | Write 2 short follow-ups for no-reply leads | `followup_emails.json` |

---

## Quick Start

### Prerequisites

```bash
pip install requests beautifulsoup4 lxml tqdm anthropic
export ANTHROPIC_API_KEY=your_key_here
```

### Run the Full Pipeline

**Step 1 — Find leads**

```bash
python .skills/ai_lead_generator/scripts/lead_generator.py \
  --niche "AI consulting" \
  --locations "US" \
  --max-results 20 \
  --output-format both \
  --output-path ./output/leads
```

**Step 2 — Write cold emails** *(for each lead from Step 1)*

```bash
python .skills/ai_cold_email/scripts/generate_emails.py \
  --company-name "NexGen AI Solutions" \
  --website "https://nexgenai.com" \
  --niche "AI consulting" \
  --sender-name "Sarah" \
  --sender-company "LeadFlow AI" \
  --cta-type "free demo" \
  --output ./output/cold_emails.json
```

**Step 3 — Follow up** *(after 4 days with no reply)*

```bash
python .skills/ai_followup/scripts/generate_followup.py \
  --lead-name "James" \
  --company-name "NexGen AI Solutions" \
  --original-subject "NexGen's lead pipeline — quick thought" \
  --original-body "Hey James, running an AI consulting firm is ironic..." \
  --days-since 4 \
  --sender-name "Sarah" \
  --urgency-type "soft" \
  --output ./output/followup_emails.json
```

---

## Output Files

All outputs land in `./output/` (relative to project root):

| File | Created by | Contents |
|------|-----------|----------|
| `leads.json` | ai-lead-generator | Array of qualified lead objects |
| `leads.csv` | ai-lead-generator | Same data in spreadsheet format |
| `cold_emails.json` | ai-cold-email | 3 variations + 1 built-in follow-up |
| `followup_emails.json` | ai-followup | 2 short follow-up variations |

---

## Email Strategy

Each lead receives up to **5 touchpoints**:

```
Day 0  →  Cold Email (pick 1 of 3 variations)
Day 4  →  Built-in Follow-up (from ai-cold-email)
Day 8  →  Standalone Follow-up A (from ai-followup, urgency)
Day 12 →  Standalone Follow-up B (from ai-followup, reframe)
Day 16 →  Break-up email (manual — "closing your file")
```

---

## Prompt Templates

Ready-to-use Claude prompts for each skill and the full pipeline:

→ [`prompts/templates.txt`](prompts/templates.txt)

---

## Example Outputs

Real sample emails from the pipeline with NexGen AI Solutions as the target:

→ [`examples/sample_outputs.md`](examples/sample_outputs.md)

---

## Project Structure

```
ai-client-acquisition-system/
│
├── skills/
│   ├── ai_lead_generator/      # Skill overview + quick start
│   ├── ai_cold_email/          # Skill overview + quick start
│   └── ai_followup/            # Skill overview + quick start
│
├── prompts/
│   └── templates.txt           # Copy-paste Claude prompts for each step
│
├── examples/
│   └── sample_outputs.md       # Real email examples from the pipeline
│
└── README.md                   # This file
```

**Skill source code** lives in `.skills/` at the project root:

```
.skills/
├── ai_lead_generator/
│   ├── SKILL.md
│   └── scripts/lead_generator.py
├── ai_cold_email/
│   ├── SKILL.md
│   └── scripts/generate_emails.py
└── ai_followup/
    ├── SKILL.md
    └── scripts/generate_followup.py
```

---

## CTA Options

When running `ai-cold-email`, choose the CTA that fits your offer:

| CTA Type | Best For |
|----------|----------|
| `free demo` | SaaS tools, platforms, software |
| `free audit` | Agencies, consultants |
| `sample leads` | Lead gen services |
| `15-min call` | High-ticket consulting |
| `case study` | Skeptical / data-driven buyers |

---

## Urgency Types (ai-followup)

| Type | What It Adds | When To Use |
|------|--------------|-------------|
| `soft` | Limited spots / timing window | Day 4 follow-up |
| `value` | New stat or client result | Day 8 follow-up |
| `question` | Direct yes/no opener | Day 12 follow-up |
