#!/usr/bin/env python3
"""
AI Lead Generator — Scrape and structure business leads for AI/IT companies.

Usage:
    python lead_generator.py --niche "AI consulting" --locations "US, UK, India"
    python lead_generator.py --niche "software agency" --locations "Germany" --max-results 20
    python lead_generator.py --validate-only --niche "AI consulting" --locations "US"
    python lead_generator.py --verify "./output/leads"
"""

import argparse
import csv
import json
import os
import re
import sys
import time
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, urljoin, quote_plus

try:
    import requests
    from bs4 import BeautifulSoup
    from tqdm import tqdm
except ImportError:
    print("❌ Missing dependencies. Run:")
    print("   pip install -r .skills/ai_lead_generator/scripts/requirements.txt")
    sys.exit(1)


# ─── Constants ────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
RESOURCES_DIR = SKILL_DIR / "resources"
DEFAULT_OUTPUT_DIR = Path("./output")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
]

REQUEST_TIMEOUT = 20
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 2

# Known email patterns on websites
EMAIL_PATTERNS = [
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
]

# Domains to exclude from lead results
EXCLUDED_DOMAINS = {
    "google.com", "facebook.com", "twitter.com", "youtube.com",
    "wikipedia.org", "yelp.com", "bbb.org", "indeed.com",
    "glassdoor.com", "reddit.com", "amazon.com", "pinterest.com",
    "instagram.com", "tiktok.com", "crunchbase.com", "zoominfo.com",
    "bloomberg.com", "forbes.com", "techcrunch.com", "medium.com",
}

# Email addresses to exclude (generic/spam)
EXCLUDED_EMAIL_PATTERNS = [
    r".*@example\.com",
    r".*@test\.com",
    r"noreply@.*",
    r"no-reply@.*",
    r"mailer-daemon@.*",
    r".*@sentry\.io",
    r".*@wixpress\.com",
    r".*@googleapis\.com",
]


# ─── Utilities ────────────────────────────────────────────────────────────────

def load_niches_config():
    """Load the niches configuration file."""
    config_path = RESOURCES_DIR / "niches.json"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"niches": {}, "locations": {}}


def get_session():
    """Create a requests session with retry logic and rotating user agents."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENTS[0],
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    })
    return session


def safe_request(session, url, retries=MAX_RETRIES):
    """Make an HTTP request with retries and exponential backoff."""
    for attempt in range(retries):
        try:
            # Rotate user agent on retries
            session.headers["User-Agent"] = USER_AGENTS[attempt % len(USER_AGENTS)]
            response = session.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)

            if response.status_code == 429:
                wait = RETRY_BACKOFF_BASE ** (attempt + 1)
                print(f"  ⏳ Rate limited. Waiting {wait}s before retry {attempt + 1}/{retries}...")
                time.sleep(wait)
                continue

            if response.status_code == 200:
                return response

            print(f"  ⚠️  HTTP {response.status_code} for {url}")
            return None

        except requests.exceptions.Timeout:
            wait = RETRY_BACKOFF_BASE ** attempt
            print(f"  ⏳ Timeout. Retrying in {wait}s ({attempt + 1}/{retries})...")
            time.sleep(wait)
        except requests.exceptions.ConnectionError:
            print(f"  ⚠️  Connection error for {url}")
            return None
        except Exception as e:
            print(f"  ⚠️  Unexpected error: {e}")
            return None

    return None


def normalize_url(url):
    """Normalize a URL to a canonical form."""
    if not url:
        return ""
    url = url.strip().rstrip("/")
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def extract_domain(url):
    """Extract the base domain from a URL."""
    try:
        parsed = urlparse(normalize_url(url))
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return ""


def is_valid_lead_domain(domain):
    """Check if a domain should be included as a lead."""
    if not domain:
        return False
    if domain in EXCLUDED_DOMAINS:
        return False
    # Filter out social/directory sites
    for excluded in EXCLUDED_DOMAINS:
        if excluded in domain:
            return False
    return True


def is_valid_email(email):
    """Check if an email address is valid and not a generic/spam address."""
    if not email:
        return False
    email = email.lower().strip()
    for pattern in EXCLUDED_EMAIL_PATTERNS:
        if re.match(pattern, email):
            return False
    # Basic format check
    if not re.match(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$", email):
        return False
    return True


def generate_lead_id(company_name, website):
    """Generate a deterministic unique ID for deduplication."""
    key = f"{company_name.lower().strip()}|{extract_domain(website)}"
    return hashlib.md5(key.encode()).hexdigest()[:12]


# ─── Search Engines ──────────────────────────────────────────────────────────

def search_google(session, query, num_results=10):
    """
    Search Google and extract result URLs and snippets.
    Returns a list of dicts: {url, title, snippet}
    """
    results = []
    encoded_query = quote_plus(query)
    search_url = f"https://www.google.com/search?q={encoded_query}&num={num_results}&hl=en"

    response = safe_request(session, search_url)
    if not response:
        return results

    soup = BeautifulSoup(response.text, "lxml")

    # Parse standard Google result blocks
    for g_div in soup.select("div.g, div[data-hveid]"):
        link_tag = g_div.select_one("a[href^='http']")
        title_tag = g_div.select_one("h3")
        snippet_tag = g_div.select_one("div.VwiC3b, span.aCOpRe, div[data-sncf]")

        if link_tag and title_tag:
            url = link_tag.get("href", "")
            title = title_tag.get_text(strip=True)
            snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""

            if url and not url.startswith("/"):
                results.append({
                    "url": url,
                    "title": title,
                    "snippet": snippet,
                })

    return results


def search_bing(session, query, num_results=10):
    """
    Search Bing and extract result URLs and snippets.
    Fallback search engine.
    """
    results = []
    encoded_query = quote_plus(query)
    search_url = f"https://www.bing.com/search?q={encoded_query}&count={num_results}"

    response = safe_request(session, search_url)
    if not response:
        return results

    soup = BeautifulSoup(response.text, "lxml")

    for li in soup.select("li.b_algo"):
        link_tag = li.select_one("h2 a")
        snippet_tag = li.select_one("p, div.b_caption p")

        if link_tag:
            url = link_tag.get("href", "")
            title = link_tag.get_text(strip=True)
            snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""

            if url:
                results.append({
                    "url": url,
                    "title": title,
                    "snippet": snippet,
                })

    return results


def search_combined(session, query, num_results=10):
    """Search multiple engines and deduplicate results."""
    all_results = []
    seen_domains = set()

    # Try Google first, fall back to Bing
    for search_fn in [search_google, search_bing]:
        results = search_fn(session, query, num_results)
        for r in results:
            domain = extract_domain(r["url"])
            if domain and domain not in seen_domains:
                seen_domains.add(domain)
                all_results.append(r)

        if len(all_results) >= num_results:
            break

        # Throttle between search engines
        time.sleep(1.5)

    return all_results[:num_results]


# ─── Lead Extraction ─────────────────────────────────────────────────────────

def extract_emails_from_page(session, url):
    """Visit a webpage and extract email addresses."""
    emails = set()

    response = safe_request(session, url, retries=1)
    if not response:
        return list(emails)

    text = response.text

    # Extract emails from page source
    for pattern in EMAIL_PATTERNS:
        found = re.findall(pattern, text)
        for email in found:
            if is_valid_email(email):
                emails.add(email.lower())

    # Check common contact page URLs
    contact_paths = ["/contact", "/contact-us", "/about", "/about-us", "/team"]
    base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"

    for path in contact_paths:
        if len(emails) >= 3:
            break

        contact_url = base_url + path
        time.sleep(0.5)
        resp = safe_request(session, contact_url, retries=1)
        if resp:
            for pattern in EMAIL_PATTERNS:
                found = re.findall(pattern, resp.text)
                for email in found:
                    if is_valid_email(email):
                        emails.add(email.lower())

    return sorted(list(emails))[:3]  # Return max 3 emails


def find_linkedin_url(session, company_name):
    """Search for a company's LinkedIn page."""
    query = f"{company_name} site:linkedin.com/company"
    results = search_combined(session, query, num_results=3)

    for r in results:
        url = r["url"]
        if "linkedin.com/company" in url:
            return url

    return ""


def compute_relevance_score(lead, niche_keywords):
    """
    Score a lead 1-10 based on how well it matches the target niche.
    """
    score = 5  # Base score

    text = f"{lead.get('company_name', '')} {lead.get('snippet', '')}".lower()

    # Keyword matches
    keyword_matches = sum(1 for kw in niche_keywords if kw.lower() in text)
    score += min(keyword_matches * 1.5, 3)

    # Has website = +0.5
    if lead.get("website"):
        score += 0.5

    # Has email = +1
    if lead.get("contact_email"):
        score += 1

    # Has LinkedIn = +0.5
    if lead.get("linkedin_url"):
        score += 0.5

    return min(round(score), 10)


def determine_status(lead, session):
    """Check if a business appears to be active."""
    website = lead.get("website", "")
    if not website:
        return "unverified"

    try:
        resp = session.head(
            normalize_url(website),
            timeout=10,
            allow_redirects=True,
        )
        if resp.status_code < 400:
            return "active"
        else:
            return "inactive"
    except Exception:
        return "unverified"


# ─── Lead Generation Pipeline ────────────────────────────────────────────────

def build_search_queries(niche, location, config):
    """Build a list of search queries for a given niche and location."""
    queries = []

    # Check if niche matches a predefined category
    niche_lower = niche.lower().replace(" ", "_").replace("-", "_")
    niche_config = config.get("niches", {})

    matched_queries = None
    for key, val in niche_config.items():
        if key == niche_lower or niche.lower() in val.get("label", "").lower():
            matched_queries = val.get("queries", [])
            break

    if matched_queries:
        for q in matched_queries[:3]:
            queries.append(f"{q} in {location}")
    else:
        # Build generic queries
        queries.append(f"{niche} companies in {location}")
        queries.append(f"best {niche} firms in {location}")
        queries.append(f"top {niche} agencies {location}")

    return queries


def generate_leads(niche, locations, max_results, session, config):
    """
    Main lead generation pipeline.
    Returns a list of lead dicts.
    """
    all_leads = []
    seen_ids = set()
    niche_keywords = [w.strip() for w in niche.replace(",", " ").split() if len(w.strip()) > 2]

    location_list = [loc.strip() for loc in locations.split(",") if loc.strip()]
    results_per_location = max(max_results // len(location_list), 5)

    print(f"\n🔍 Searching for \"{niche}\" leads in: {', '.join(location_list)}")
    print(f"   Target: ~{results_per_location} leads per location\n")

    for location in location_list:
        print(f"📍 Location: {location}")
        queries = build_search_queries(niche, location, config)
        location_leads = []

        for query in tqdm(queries, desc=f"   Searching", unit="query"):
            search_results = search_combined(session, query, num_results=results_per_location)

            for result in search_results:
                domain = extract_domain(result["url"])

                if not is_valid_lead_domain(domain):
                    continue

                lead_id = generate_lead_id(result["title"], result["url"])
                if lead_id in seen_ids:
                    continue
                seen_ids.add(lead_id)

                lead = {
                    "id": lead_id,
                    "company_name": result["title"],
                    "website": normalize_url(result["url"]),
                    "contact_email": "",
                    "linkedin_url": "",
                    "location": location,
                    "niche": niche,
                    "relevance_score": 0,
                    "status": "unverified",
                    "source": "search",
                    "snippet": result.get("snippet", ""),
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                }

                location_leads.append(lead)

            # Throttle between queries
            time.sleep(2)

        # Enrich leads (emails, LinkedIn, scoring) — with progress bar
        if location_leads:
            print(f"   📧 Enriching {len(location_leads)} leads...")
            for lead in tqdm(location_leads[:results_per_location], desc="   Enriching", unit="lead"):
                # Extract emails
                try:
                    emails = extract_emails_from_page(session, lead["website"])
                    if emails:
                        lead["contact_email"] = emails[0]
                except Exception:
                    pass

                # Find LinkedIn
                try:
                    linkedin = find_linkedin_url(session, lead["company_name"])
                    if linkedin:
                        lead["linkedin_url"] = linkedin
                except Exception:
                    pass

                # Compute relevance
                lead["relevance_score"] = compute_relevance_score(lead, niche_keywords)

                # Check status
                lead["status"] = determine_status(lead, session)

                time.sleep(1)

        # Filter: only active/unverified leads with relevance >= 4
        qualified = [
            l for l in location_leads
            if l["relevance_score"] >= 4 and l["status"] != "inactive"
        ]

        print(f"   ✅ {len(qualified)} qualified leads from {location}\n")
        all_leads.extend(qualified[:results_per_location])

    return all_leads


# ─── Output ──────────────────────────────────────────────────────────────────

def clean_lead_for_output(lead):
    """Remove internal fields before output."""
    output = {k: v for k, v in lead.items() if k not in ("snippet", "id")}
    return output


def save_json(leads, output_path):
    """Save leads as a JSON file."""
    path = Path(output_path).with_suffix(".json")
    path.parent.mkdir(parents=True, exist_ok=True)

    clean_leads = [clean_lead_for_output(l) for l in leads]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(clean_leads, f, indent=2, ensure_ascii=False)

    print(f"💾 Saved JSON: {path}")
    return str(path)


def save_csv(leads, output_path):
    """Save leads as a CSV file."""
    path = Path(output_path).with_suffix(".csv")
    path.parent.mkdir(parents=True, exist_ok=True)

    clean_leads = [clean_lead_for_output(l) for l in leads]
    if not clean_leads:
        print("⚠️  No leads to save.")
        return str(path)

    fieldnames = list(clean_leads[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(clean_leads)

    print(f"💾 Saved CSV: {path}")
    return str(path)


def print_summary_table(leads):
    """Print a formatted summary table of results."""
    if not leads:
        print("\n📊 No leads found.")
        return

    print(f"\n{'═' * 90}")
    print(f"  📊 LEAD GENERATION SUMMARY")
    print(f"{'═' * 90}")
    print(f"  Total Leads: {len(leads)}")

    # By location
    locations = {}
    for l in leads:
        loc = l.get("location", "Unknown")
        locations[loc] = locations.get(loc, 0) + 1

    print(f"\n  By Location:")
    for loc, count in sorted(locations.items()):
        bar = "█" * min(count, 30)
        print(f"    {loc:<20} {count:>4}  {bar}")

    # Completeness
    with_email = sum(1 for l in leads if l.get("contact_email"))
    with_linkedin = sum(1 for l in leads if l.get("linkedin_url"))
    active = sum(1 for l in leads if l.get("status") == "active")
    avg_score = sum(l.get("relevance_score", 0) for l in leads) / len(leads)

    print(f"\n  Completeness:")
    print(f"    With Email:     {with_email:>4} / {len(leads)}  ({with_email/len(leads)*100:.0f}%)")
    print(f"    With LinkedIn:  {with_linkedin:>4} / {len(leads)}  ({with_linkedin/len(leads)*100:.0f}%)")
    print(f"    Active Status:  {active:>4} / {len(leads)}  ({active/len(leads)*100:.0f}%)")
    print(f"    Avg Relevance:  {avg_score:.1f} / 10")

    # Top leads preview
    top_leads = sorted(leads, key=lambda x: x.get("relevance_score", 0), reverse=True)[:10]
    print(f"\n  Top {len(top_leads)} Leads:")
    print(f"  {'Company':<35} {'Location':<15} {'Score':<7} {'Email':<8} {'LinkedIn':<8}")
    print(f"  {'─' * 73}")
    for l in top_leads:
        has_email = "✅" if l.get("contact_email") else "—"
        has_linkedin = "✅" if l.get("linkedin_url") else "—"
        name = l.get("company_name", "")[:33]
        print(f"  {name:<35} {l.get('location', ''):<15} {l.get('relevance_score', 0):<7} {has_email:<8} {has_linkedin:<8}")

    print(f"{'═' * 90}\n")


# ─── Verification ────────────────────────────────────────────────────────────

def verify_output(output_path):
    """Verify a previously generated output file."""
    json_path = Path(output_path).with_suffix(".json")
    csv_path = Path(output_path).with_suffix(".csv")

    leads = None

    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            leads = json.load(f)
        print(f"✅ Valid JSON file: {json_path} ({len(leads)} leads)")
    elif csv_path.exists():
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            leads = list(reader)
        print(f"✅ Valid CSV file: {csv_path} ({len(leads)} leads)")
    else:
        print(f"❌ No output file found at {output_path} (.json or .csv)")
        sys.exit(1)

    if leads:
        print_summary_table(leads)
        print("✅ Output verification passed.")
    else:
        print("⚠️  Output file is empty.")
        sys.exit(1)


# ─── CLI ──────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="AI Lead Generator — Generate business leads for AI/IT companies",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --niche "AI consulting" --locations "US, UK, India"
  %(prog)s --niche "software agency" --locations "Germany" --max-results 20
  %(prog)s --validate-only --niche "AI consulting" --locations "US"
  %(prog)s --verify "./output/leads"
        """,
    )

    parser.add_argument(
        "--niche", type=str,
        help="Business niche to search for (e.g., 'AI consulting', 'software agency')",
    )
    parser.add_argument(
        "--locations", type=str, default="US, UK, India",
        help="Comma-separated locations (default: 'US, UK, India')",
    )
    parser.add_argument(
        "--max-results", type=int, default=50,
        help="Max leads to generate per location (default: 50)",
    )
    parser.add_argument(
        "--output-format", type=str, default="json",
        choices=["json", "csv", "both"],
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--output-path", type=str, default="./output/leads",
        help="Base output path without extension (default: ./output/leads)",
    )
    parser.add_argument(
        "--validate-only", action="store_true",
        help="Only validate inputs, don't run generation",
    )
    parser.add_argument(
        "--verify", type=str, metavar="PATH",
        help="Verify a previously generated output file",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    # ── Verify mode ──
    if args.verify:
        verify_output(args.verify)
        return

    # ── Validate inputs ──
    if not args.niche:
        print("❌ --niche is required. Example: --niche \"AI consulting\"")
        sys.exit(1)

    if not args.locations or not args.locations.strip():
        print("❌ --locations must be non-empty. Example: --locations \"US, UK, India\"")
        sys.exit(1)

    if args.max_results < 1 or args.max_results > 500:
        print("❌ --max-results must be between 1 and 500")
        sys.exit(1)

    config = load_niches_config()

    if args.validate_only:
        print(f"✅ Inputs validated successfully")
        print(f"   Niche:       {args.niche}")
        print(f"   Locations:   {args.locations}")
        print(f"   Max Results: {args.max_results}")
        print(f"   Format:      {args.output_format}")
        print(f"   Output Path: {args.output_path}")

        # Check if niche matches predefined
        niche_lower = args.niche.lower().replace(" ", "_").replace("-", "_")
        for key, val in config.get("niches", {}).items():
            if key == niche_lower or args.niche.lower() in val.get("label", "").lower():
                print(f"   Matched Config: {val['label']} ({len(val.get('queries', []))} query variations)")
                break
        else:
            print(f"   Matched Config: Custom (generic queries will be used)")
        return

    # ── Run generation ──
    print("🚀 AI Lead Generator v1.0.0")
    print(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    session = get_session()
    leads = generate_leads(
        niche=args.niche,
        locations=args.locations,
        max_results=args.max_results,
        session=session,
        config=config,
    )

    # ── Sort by relevance ──
    leads.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

    # ── Save output ──
    if args.output_format in ("json", "both"):
        save_json(leads, args.output_path)

    if args.output_format in ("csv", "both"):
        save_csv(leads, args.output_path)

    # ── Print summary ──
    print_summary_table(leads)

    print(f"🏁 Done! Generated {len(leads)} leads.")
    print(f"   Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
