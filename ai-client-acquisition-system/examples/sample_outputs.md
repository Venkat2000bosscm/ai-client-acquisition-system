# Sample Outputs

Real example outputs from each skill in the pipeline.

---

## Step 1 — Lead Generation Output

**Skill:** `ai-lead-generator`
**Input:** niche=`AI consulting`, location=`US`

```json
{
  "company_name": "NexGen AI Solutions",
  "website": "https://nexgenai.com",
  "contact_email": "hello@nexgenai.com",
  "linkedin_url": "https://www.linkedin.com/company/nexgen-ai",
  "location": "US",
  "niche": "AI consulting",
  "relevance_score": 9,
  "status": "active",
  "source": "search",
  "scraped_at": "2026-03-30T12:00:00+00:00"
}
```

---

## Step 2 — Cold Email Output

**Skill:** `ai-cold-email`
**Input:** company=`NexGen AI Solutions`, cta=`free demo`, urgency=`soft`

### Variation 1 — Pain-Point Hook

**Subject:** `NexGen's lead pipeline — quick thought`

> Hey James,
>
> Running an AI consulting firm is ironic in one way — you're selling automation to clients, but your own lead gen is probably still manual.
>
> I've talked to a dozen AI consultants this month. Almost all get 80% of business from referrals and feel stuck when that dries up.
>
> At LeadFlow AI, we built a system that automatically identifies, qualifies, and delivers warm leads for consulting firms like NexGen — so you're pitching, not prospecting.
>
> Would a quick 20-minute demo make sense? No pitch, just show you what's possible.
>
> — Sarah
>
> P.S. We set one client up last month — they booked 3 discovery calls in the first week.

---

### Variation 2 — Social Proof Hook

**Subject:** `40 leads/month for an AI consultancy`

> Hey James,
>
> A few months ago, a small AI consulting firm (2 partners, no SDR) was getting 4–5 inbound inquiries a month.
>
> We plugged in our lead automation. Within 6 weeks they were seeing 40+ qualified leads per month — companies actively looking for AI consulting help.
>
> No cold calls. No LinkedIn spam. Just automated, targeted outreach that sounds human.
>
> I think NexGen could see similar results. Mind if I show you how it works — 20 minutes, free?
>
> — Sarah
>
> P.S. Happy to share the exact breakdown of what we built for them.

---

### Variation 3 — Curiosity Hook

**Subject:** `Where do NexGen's best clients come from?`

> Hey James,
>
> Quick question — if you had to guess, what's the #1 source of your best clients right now?
>
> For most AI consultancies, the honest answer is "someone I already knew" or "a random referral."
>
> That's great until it isn't.
>
> We built LeadFlow AI so firms like NexGen don't have to rely on luck. It automates the prospecting layer — finding companies already looking for AI help.
>
> Worth a 20-minute look?
>
> — Sarah
>
> P.S. No deck, no pitch — just the live system.

---

### Built-in Follow-up (from ai-cold-email)

**Subject:** `Re: quick thought for NexGen`
**Send:** Day 4

> Hey James,
>
> Sent you a note a few days ago — not sure if it got buried.
>
> One thing I forgot to mention: we only work with 3–4 new clients per month to keep quality high. Two spots are open right now.
>
> Still happy to show you the demo if the timing's right — totally understand if it's not.
>
> — Sarah
>
> P.S. Takes 20 minutes. You'd know by the end if it's a fit.

---

## Step 3 — Follow-Up Output

**Skill:** `ai-followup`
**Input:** lead=`James @ NexGen`, urgency=`soft`, days_since=`4`

### Variation A — Soft Urgency

**Subject:** `Re: NexGen's lead pipeline — quick thought`

> Hey James,
>
> Sent you a note a few days ago — not sure if it got buried.
>
> Worth mentioning: we're only onboarding 3 new clients this month to keep quality high. Two spots still open.
>
> Worth a 20-minute look before they're gone?
>
> — Sarah

*Word count: 51*

---

### Variation B — Question Reframe

**Subject:** `Quick question for you, James`

> Hey James,
>
> Completely understand if the timing's off — no pressure at all.
>
> One honest question: is lead gen actually a priority for NexGen right now, or is capacity the bigger constraint?
>
> Either way, happy to share what's working for firms like yours.
>
> — Sarah

*Word count: 46*

---

## Pipeline Summary

```
ai-lead-generator  →  leads.json         (qualified companies + contacts)
       ↓
ai-cold-email      →  cold_emails.json   (3 variations + 1 follow-up)
       ↓
ai-followup        →  followup_emails.json  (2 variations, day 4+)
```

**Total emails per lead:** 5 (3 cold + 1 built-in follow-up + 2 standalone follow-ups)
