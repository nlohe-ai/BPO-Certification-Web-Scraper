#!/usr/bin/env python3
"""Comprehensive diagnostic to trace exactly what's happening."""

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote, quote_plus, urlparse

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

def is_valid_bpo_url(url: str) -> bool:
    """Check if URL looks like a legitimate BPO company website."""
    parsed = urlparse(url)

    # Must have a valid domain
    if not parsed.netloc:
        return False

    # Exclude common non-company domains
    excluded_domains = [
        "google.com", "bing.com", "yahoo.com", "facebook.com", "twitter.com",
        "linkedin.com", "youtube.com", "wikipedia.org", "forbes.com",
        "indeed.com", "glassdoor.com", "clutch.co", "gartner.com",
        "duckduckgo.com", "netquote.com", "capterra.com", "trustpilot.com",
        "bbb.org", "reddit.com", "quora.com", "instagram.com",
        "goodfirms.co", "upwork.com", "fiverr.com", "pinterest.com",
    ]

    domain_lower = parsed.netloc.lower()
    for excluded in excluded_domains:
        if excluded in domain_lower:
            return False

    # Exclude obvious non-company paths
    excluded_paths = ["/search", "/maps", "/news", "/images"]
    for excluded in excluded_paths:
        if parsed.path.startswith(excluded):
            return False

    # Exclude ad tracking and affiliate URLs
    if any(word in url.lower() for word in ["aclick", "ad_provider", "click_metadata", "/aff/"]):
        return False

    return True

def extract_domain_from_url(url: str) -> str:
    """Extract clean domain from URL."""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]
    return f"https://{domain}"

query = "insurance BPO company"
search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"

print("=" * 80)
print("COMPREHENSIVE DISCOVERY DIAGNOSTIC")
print("=" * 80)
print(f"Query: {query}")
print(f"URL: {search_url}")
print()

# Step 1: Fetch
print("STEP 1: Fetching DuckDuckGo...")
response = requests.get(search_url, headers=HEADERS, timeout=15)
print(f"  Status: {response.status_code}")
print(f"  Response length: {len(response.text)} bytes")
print()

# Step 2: Parse
print("STEP 2: Parsing HTML...")
soup = BeautifulSoup(response.text, "html.parser")
result_links = soup.find_all("a", class_=["result__a", "result__url"])
print(f"  Found {len(result_links)} links with class 'result__a' or 'result__url'")
print()

# Step 3: Process each link
print("STEP 3: Processing each link...")
print()

discovered = []
for i, link in enumerate(result_links[:20], 1):  # Process first 20
    href = link.get("href", "")

    print(f"Link #{i}:")
    print(f"  href: {href[:120]}...")

    if "uddg=" not in href:
        print(f"  ❌ SKIP: No 'uddg=' parameter")
        print()
        continue

    # Extract uddg
    match = re.search(r"uddg=([^&]+)", href)
    if not match:
        print(f"  ❌ SKIP: Could not extract uddg parameter")
        print()
        continue

    encoded_url = match.group(1)
    print(f"  ✓ Extracted encoded URL: {encoded_url[:80]}...")

    # Decode
    actual_url = unquote(encoded_url)
    print(f"  ✓ Decoded URL: {actual_url[:100]}...")

    # Check if ad
    is_ad = "duckduckgo.com/y.js" in actual_url or "bing.com/aclick" in actual_url
    if is_ad:
        print(f"  ❌ SKIP: Ad URL (contains duckduckgo.com/y.js or bing.com/aclick)")
        print()
        continue

    print(f"  ✓ Not an ad")

    # Check if valid
    is_valid = is_valid_bpo_url(actual_url)
    print(f"  Valid BPO URL: {is_valid}")

    if not is_valid:
        parsed = urlparse(actual_url)
        print(f"    Domain: {parsed.netloc}")
        print(f"    Path: {parsed.path}")
        print(f"  ❌ SKIP: Failed is_valid_bpo_url() check")
        print()
        continue

    # Extract domain
    clean_url = extract_domain_from_url(actual_url)
    print(f"  ✓ Clean domain: {clean_url}")
    print(f"  ✅ SUCCESS - Would be added to results")
    discovered.append(clean_url)
    print()

print("=" * 80)
print(f"SUMMARY: Found {len(discovered)} valid URLs")
if discovered:
    print()
    print("Discovered URLs:")
    for url in discovered:
        print(f"  - {url}")
else:
    print()
    print("❌ NO URLS DISCOVERED")
    print()
    print("This means either:")
    print("  1. DuckDuckGo is returning only ads in your region")
    print("  2. The is_valid_bpo_url() filter is too strict")
    print("  3. Something else is filtering them out")
print("=" * 80)
