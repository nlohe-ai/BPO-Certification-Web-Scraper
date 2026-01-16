#!/usr/bin/env python3
"""Alternative discovery methods when DuckDuckGo returns 202."""

import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote, quote_plus, urlparse
from typing import Set

# Try multiple user agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
]


def get_headers(user_agent):
    """Get headers with specific user agent."""
    return {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Cache-Control": "max-age=0",
    }


def try_duckduckgo_with_session(query: str) -> tuple[int, str]:
    """Try DuckDuckGo with a session and cookies."""
    session = requests.Session()

    # First, visit homepage to get cookies
    try:
        session.get("https://duckduckgo.com/", headers=get_headers(USER_AGENTS[0]), timeout=10)
        time.sleep(1)
    except:
        pass

    # Now try the search
    search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"

    for i, user_agent in enumerate(USER_AGENTS):
        print(f"  Attempt {i+1}/{len(USER_AGENTS)}: User agent #{i+1}")

        try:
            response = session.get(search_url, headers=get_headers(user_agent), timeout=15)
            print(f"    Status: {response.status_code}, Length: {len(response.text)} bytes")

            if response.status_code == 200 and len(response.text) > 30000:
                print(f"    ✓ Success!")
                return response.status_code, response.text
            elif response.status_code == 202:
                print(f"    ⚠️  Got 202 (Accepted) - trying next user agent...")
                time.sleep(2)
                continue
            else:
                print(f"    ⚠️  Unusual response - trying next user agent...")
                time.sleep(1)
                continue

        except Exception as e:
            print(f"    ✗ Error: {e}")
            continue

    # If all attempts fail, return last response
    print(f"  ❌ All attempts failed")
    return 202, ""


def parse_results(html: str) -> Set[str]:
    """Parse search results from HTML."""
    from discovery import is_valid_bpo_url, extract_domain_from_url

    soup = BeautifulSoup(html, "html.parser")
    result_links = soup.find_all("a", class_=["result__a", "result__url"])

    print(f"  Found {len(result_links)} result links")

    discovered_urls = set()

    for link in result_links:
        href = link.get("href", "")

        if "uddg=" in href:
            match = re.search(r"uddg=([^&]+)", href)
            if match:
                encoded_url = match.group(1)
                actual_url = unquote(encoded_url)

                # Skip ads
                if "duckduckgo.com/y.js" in actual_url or "bing.com/aclick" in actual_url:
                    continue

                # Filter
                if is_valid_bpo_url(actual_url):
                    clean_url = extract_domain_from_url(actual_url)
                    discovered_urls.add(clean_url)

    return discovered_urls


def discover_with_fallback(query: str) -> Set[str]:
    """Try discovery with multiple fallback methods."""
    print(f"\nSearching for: '{query}'")
    print("-" * 60)

    # Method 1: Session-based approach
    print("Method 1: Session-based DuckDuckGo")
    status, html = try_duckduckgo_with_session(query)

    if status == 200 and html:
        urls = parse_results(html)
        if urls:
            print(f"  ✓ Found {len(urls)} URLs")
            return urls

    print("  ❌ Method 1 failed")
    print()

    # Method 2: Simple GET with delay
    print("Method 2: Simple GET with delay")
    time.sleep(3)

    try:
        search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        response = requests.get(search_url, headers=get_headers(USER_AGENTS[1]), timeout=15)

        print(f"  Status: {response.status_code}, Length: {len(response.text)} bytes")

        if response.status_code == 200:
            urls = parse_results(response.text)
            if urls:
                print(f"  ✓ Found {len(urls)} URLs")
                return urls
    except Exception as e:
        print(f"  ✗ Error: {e}")

    print("  ❌ Method 2 failed")
    print()

    print("❌ All methods exhausted - DuckDuckGo not accessible from your location/network")
    return set()


if __name__ == "__main__":
    print("=" * 70)
    print("ALTERNATIVE DISCOVERY TEST")
    print("=" * 70)

    urls = discover_with_fallback("insurance BPO company")

    print()
    print("=" * 70)
    print(f"RESULT: Found {len(urls)} URLs")

    if urls:
        print()
        for url in sorted(urls):
            print(f"  - {url}")
    else:
        print()
        print("Unfortunately, DuckDuckGo is not returning results in your environment.")
        print()
        print("ALTERNATIVES:")
        print("1. Use a VPN to change your location")
        print("2. Manually compile a list of BPO websites from industry directories")
        print("3. Use the scraper with a manually curated sites.txt file")

    print("=" * 70)
