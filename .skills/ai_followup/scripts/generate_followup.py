#!/usr/bin/env python3
"""
generate_followup.py — AI Follow-up Email Generator
Uses Claude to write 2 short, natural follow-ups for no-response leads.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import anthropic

# ---------------------------------------------------------------------------
# Urgency framing instructions per type
# ---------------------------------------------------------------------------
URGENCY_INSTRUCTIONS = {
    "soft": (
        "Variation A should add soft urgency — mention that you only take on a limited number of "
        "new clients per month, or that a relevant window is closing. Keep it honest, not fake-scarce."
    ),
    "value": (
        "Variation A should add new value not in the original email — a specific stat, a recent "
        "client result, or a relevant insight about their niche. One sentence of proof, then the ask."
    ),
    "question": (
        "Variation A should open with a single direct, low-pressure question that's easy to answer "
        "yes or no — something that re-opens the conversation without requiring a big commitment."
    ),
}

DEFAULT_URGENCY = URGENCY_INSTRUCTIONS["soft"]


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------
def build_prompt(
    lead_name: str,
    company_name: str,
    original_subject: str,
    original_body: str,
    days_since: int,
    sender_name: str,
    offer: str,
    urgency_type: str,
) -> str:
    urgency_instruction = URGENCY_INSTRUCTIONS.get(urgency_type.lower(), DEFAULT_URGENCY)

    return f"""You are an expert B2B email copywriter. Your specialty is writing follow-up emails that get replies without being annoying or pushy.

CONTEXT:
- Sender: {sender_name}
- Lead: {lead_name} at {company_name}
- Offer: {offer}
- Days since original email: {days_since}
- Original subject: "{original_subject}"
- Original email body:
---
{original_body}
---

TASK: Write 2 follow-up email variations for {lead_name} at {company_name} who hasn't replied.

URGENCY GUIDANCE:
{urgency_instruction}

Variation B should use a different angle: either empathy ("totally get it if timing's off...") or a reframe (approach the value prop from a completely different angle than both the original email and Variation A).

STRICT RULES:
- Max 60 words per body (count carefully)
- NEVER start with: "Just checking in", "Following up on my last email", "I wanted to circle back", "Per my last email", "Did you get a chance", "Hope you're doing well"
- Reference the original email in ONE line max — then move forward
- End with one low-friction CTA: a yes/no question or a single-sentence ask
- Subject line: use "Re: {original_subject}" OR a fresh 1–5 word curiosity line
- Tone: casual, warm, peer-to-peer — like a text from a colleague, not a salesperson

OUTPUT — return ONLY valid JSON, no markdown, no explanation:

{{
  "variations": [
    {{
      "id": "A",
      "angle": "<one word: urgency|value|question>",
      "subject": "<subject line>",
      "body": "<follow-up email body, max 60 words>",
      "word_count": <integer>
    }},
    {{
      "id": "B",
      "angle": "<one word: empathy|reframe|question>",
      "subject": "<subject line>",
      "body": "<follow-up email body, max 60 words>",
      "word_count": <integer>
    }}
  ]
}}"""


# ---------------------------------------------------------------------------
# Generation with retry
# ---------------------------------------------------------------------------
def generate_followup(args: argparse.Namespace) -> dict:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set. Run: export ANTHROPIC_API_KEY=your_key_here")
        sys.exit(1)

    if not args.original_body.strip():
        print("❌ original_email_body cannot be empty.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    prompt = build_prompt(
        lead_name=args.lead_name,
        company_name=args.company_name,
        original_subject=args.original_subject,
        original_body=args.original_body,
        days_since=args.days_since,
        sender_name=args.sender_name,
        offer=args.offer,
        urgency_type=args.urgency_type,
    )

    last_error = None
    for attempt in range(1, 4):
        try:
            print(f"  Calling Claude API (attempt {attempt}/3)...")
            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = message.content[0].text.strip()

            # Strip accidental markdown fences
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.rsplit("```", 1)[0]

            result = json.loads(raw)

            # Validate word counts — retry if any body is over 80 words
            for v in result.get("variations", []):
                actual = len(v["body"].split())
                v["word_count"] = actual  # overwrite with real count
                if actual > 80 and attempt < 3:
                    raise ValueError(f"Variation {v['id']} is {actual} words (max 80). Retrying...")

            return result

        except (json.JSONDecodeError, ValueError) as e:
            last_error = e
            print(f"  ⚠️  Attempt {attempt} failed: {e}")
            if attempt < 3:
                time.sleep(2 ** attempt)
        except anthropic.RateLimitError:
            print(f"  ⚠️  Rate limited, waiting {10 * attempt}s...")
            time.sleep(10 * attempt)

    print(f"❌ Failed after 3 attempts. Last error: {last_error}")
    sys.exit(1)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate follow-up emails using Claude")
    parser.add_argument("--lead-name", default="[First Name]")
    parser.add_argument("--company-name", required=True)
    parser.add_argument("--original-subject", required=True)
    parser.add_argument("--original-body", required=True)
    parser.add_argument("--days-since", type=int, default=4)
    parser.add_argument("--sender-name", default="[Your Name]")
    parser.add_argument("--offer", default="AI-powered lead generation automation")
    parser.add_argument("--urgency-type", default="soft", choices=["soft", "value", "question"])
    parser.add_argument("--output", default="./output/followup_emails.json")
    return parser.parse_args()


def main():
    args = parse_args()

    print(f"\n📬 Generating follow-ups for: {args.lead_name} @ {args.company_name}")
    print(f"   Original subject : {args.original_subject}")
    print(f"   Days since sent  : {args.days_since}")
    print(f"   Urgency type     : {args.urgency_type}\n")

    result = generate_followup(args)

    output = {
        "lead_name": args.lead_name,
        "company_name": args.company_name,
        "days_since_first_email": args.days_since,
        "urgency_type": args.urgency_type,
        "original_subject": args.original_subject,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        **result,
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✅ Generated {len(output['variations'])} follow-up variations")
    print(f"📁 Saved to: {output_path}\n")

    print("📬 Subject lines:")
    for v in output["variations"]:
        print(f"   [Variation {v['id']} — {v['angle'].upper()}]  {v['subject']}  ({v['word_count']} words)")
    print()


if __name__ == "__main__":
    main()
