#!/usr/bin/env python3
"""
generate_emails.py — AI Cold Email Generator
Uses Claude to produce 3 cold email variations + 1 follow-up for AI consultants.
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
# Pain point library — used as seed context for Claude
# ---------------------------------------------------------------------------
PAIN_POINTS_BY_NICHE = {
    "ai consulting": [
        "struggling to consistently fill their pipeline with qualified leads",
        "spending too much time on manual outreach instead of delivering client work",
        "losing deals to larger firms that appear more established online",
    ],
    "it staffing": [
        "spending weeks sourcing candidates only to lose them to faster competitors",
        "client churn from inconsistent delivery timelines",
        "relying on referrals with no predictable inbound lead flow",
    ],
    "digital marketing": [
        "clients questioning ROI and churning after 3–6 months",
        "burning hours on manual prospecting instead of creative work",
        "difficulty scaling outreach without hiring more SDRs",
    ],
    "saas": [
        "high trial-to-paid drop-off with no automated nurture sequences",
        "churn from users who never fully activate the product",
        "slow sales cycles because demos are hard to schedule",
    ],
    "e-commerce": [
        "cart abandonment eating into revenue with no recovery automation",
        "low repeat-purchase rates despite a solid first order experience",
        "paid ad costs rising while conversion rates stay flat",
    ],
}

DEFAULT_PAIN_POINTS = [
    "spending too much time on manual outreach with inconsistent results",
    "struggling to scale client acquisition beyond their current network",
    "losing deals because follow-up isn't fast or personalized enough",
]


def get_pain_points(niche: str) -> list[str]:
    niche_lower = niche.lower().strip()
    for key, points in PAIN_POINTS_BY_NICHE.items():
        if key in niche_lower or niche_lower in key:
            return points
    return DEFAULT_PAIN_POINTS


# ---------------------------------------------------------------------------
# Claude prompt builder
# ---------------------------------------------------------------------------
def build_prompt(
    company_name: str,
    website: str,
    niche: str,
    sender_name: str,
    sender_company: str,
    offer: str,
    cta_type: str,
    pain_points: list[str],
) -> str:
    pain_points_str = "\n".join(f"- {p}" for p in pain_points)
    cta_map = {
        "free demo": f"ask if they'd be open to a free 20-minute demo — no pitch, just show them what's possible",
        "free audit": f"offer a free lead generation audit specific to their business",
        "sample leads": f"offer to send 10 free sample leads for their niche as proof of value",
        "15-min call": f"ask for a quick 15-minute call — no deck, just a conversation",
        "case study": f"offer to send a relevant case study showing results for a similar company",
    }
    cta_instruction = cta_map.get(cta_type.lower(), f"offer a {cta_type} as the call-to-action")

    return f"""You are an expert cold email copywriter specializing in B2B outreach for AI and tech companies.

Your task: Write cold emails from {sender_name} at {sender_company} to {company_name} ({website}), a company in the {niche} space.

WHAT WE'RE OFFERING: {offer}

LIKELY PAIN POINTS FOR {company_name}:
{pain_points_str}

CALL TO ACTION: {cta_instruction}

WRITING RULES — follow these strictly:
- Tone: Friendly, casual, peer-to-peer. Write like a human, not a marketer.
- Length: 80–120 words per email body (not counting subject/PS). Mobile-friendly.
- Personalization: Mention {company_name} and their niche naturally — not forced.
- Forbidden words/phrases: "synergy", "leverage", "circle back", "touch base", "hope this finds you well", "I wanted to reach out", "per my last email", "thought leader"
- One CTA only: End every email with exactly one clear ask.
- Subject lines: Under 50 characters. Curiosity-driven or specific — no clickbait.
- P.S. line: One sentence that reinforces the value prop or adds social proof.

GENERATE EXACTLY THIS OUTPUT as valid JSON (no markdown fences, no explanation):

{{
  "identified_pain_points": ["pain point 1", "pain point 2", "pain point 3"],
  "variations": [
    {{
      "id": 1,
      "hook_type": "pain-point",
      "subject": "...",
      "body": "...",
      "ps": "..."
    }},
    {{
      "id": 2,
      "hook_type": "social-proof",
      "subject": "...",
      "body": "...",
      "ps": "..."
    }},
    {{
      "id": 3,
      "hook_type": "curiosity",
      "subject": "...",
      "body": "...",
      "ps": "..."
    }}
  ],
  "follow_up": {{
    "send_after_days": 4,
    "subject": "...",
    "body": "...",
    "ps": "..."
  }}
}}

Email variation guidance:
1. PAIN-POINT hook: Open by naming a specific frustration {company_name} likely faces. Empathize briefly, then pivot to how {offer} solves it.
2. SOCIAL-PROOF hook: Open with a concrete outcome/result (e.g., "One of our clients in {niche} added 40 leads/month in 6 weeks..."). Then make it relevant to {company_name}.
3. CURIOSITY hook: Open with a thought-provoking question about their business or niche. Make them want to reply just to answer it.
4. FOLLOW-UP: Reference the previous email briefly ("Sent you a note last week — not sure if it landed..."). Add one new piece of value (a stat, a question, or a different angle). Keep it under 60 words. Lighthearted, not pushy."""


# ---------------------------------------------------------------------------
# Main generation function
# ---------------------------------------------------------------------------
def generate_emails(args: argparse.Namespace) -> dict:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set. Run: export ANTHROPIC_API_KEY=your_key_here")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    pain_points = get_pain_points(args.niche)
    prompt = build_prompt(
        company_name=args.company_name,
        website=args.website,
        niche=args.niche,
        sender_name=args.sender_name,
        sender_company=args.sender_company,
        offer=args.offer,
        cta_type=args.cta_type,
        pain_points=pain_points,
    )

    last_error = None
    for attempt in range(1, 4):
        try:
            print(f"  Calling Claude API (attempt {attempt}/3)...")
            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = message.content[0].text.strip()

            # Strip accidental markdown fences
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]

            result = json.loads(raw)
            return result

        except json.JSONDecodeError as e:
            last_error = e
            print(f"  ⚠️  JSON parse error on attempt {attempt}: {e}")
            if attempt < 3:
                time.sleep(2 ** attempt)
        except anthropic.RateLimitError:
            print(f"  ⚠️  Rate limited on attempt {attempt}, waiting {10 * attempt}s...")
            time.sleep(10 * attempt)

    print(f"❌ Failed after 3 attempts. Last error: {last_error}")
    sys.exit(1)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate AI cold emails using Claude")
    parser.add_argument("--company-name", required=True)
    parser.add_argument("--website", required=True)
    parser.add_argument("--niche", required=True)
    parser.add_argument("--sender-name", default="[Your Name]")
    parser.add_argument("--sender-company", default="[Your Company]")
    parser.add_argument("--offer", default="AI-powered lead generation automation")
    parser.add_argument("--cta-type", default="free demo")
    parser.add_argument("--output", default="./output/cold_emails.json")
    return parser.parse_args()


def main():
    args = parse_args()

    print(f"\n🎯 Generating cold emails for: {args.company_name} ({args.niche})")
    print(f"   Offer : {args.offer}")
    print(f"   CTA   : {args.cta_type}")
    print(f"   From  : {args.sender_name} @ {args.sender_company}\n")

    emails = generate_emails(args)

    # Enrich with metadata
    output = {
        "company_name": args.company_name,
        "website": args.website,
        "niche": args.niche,
        "offer": args.offer,
        "cta_type": args.cta_type,
        "sender_name": args.sender_name,
        "sender_company": args.sender_company,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        **emails,
    }

    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✅ Generated {len(output['variations'])} variations + 1 follow-up")
    print(f"📁 Saved to: {output_path}\n")

    print("📬 Subject lines:")
    for v in output["variations"]:
        print(f"   [{v['hook_type'].upper()}] {v['subject']}")
    print(f"   [FOLLOW-UP]  {output['follow_up']['subject']}")
    print()


if __name__ == "__main__":
    main()
