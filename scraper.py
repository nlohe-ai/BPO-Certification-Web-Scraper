import argparse
import csv
import re
import time
from collections import deque
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# Import discovery module for finding BPO websites
try:
    from discovery import discover_bpo_websites, load_queries_from_file, save_discovered_urls
    DISCOVERY_AVAILABLE = True
except ImportError:
    DISCOVERY_AVAILABLE = False

CERTIFICATION_PATTERNS = {
    "ISO 27001": re.compile(r"\bISO\s*27001\b", re.IGNORECASE),
    "SOC 1": re.compile(r"\bSOC\s*1\b", re.IGNORECASE),
    "SOC 2": re.compile(r"\bSOC\s*2\b", re.IGNORECASE),
    "SOC 3": re.compile(r"\bSOC\s*3\b", re.IGNORECASE),
    "PCI DSS": re.compile(r"\bPCI\s*DSS\b", re.IGNORECASE),
    "HIPAA": re.compile(r"\bHIPAA\b", re.IGNORECASE),
    "HITRUST": re.compile(r"\bHITRUST\b", re.IGNORECASE),
    "GDPR": re.compile(r"\bGDPR\b", re.IGNORECASE),
}

REMOTE_ENV_PATTERNS = {
    "VDI": re.compile(r"\bVDI\b|virtual\s+desktop", re.IGNORECASE),
    "Remote Desktop": re.compile(r"remote\s+desktop", re.IGNORECASE),
    "Citrix": re.compile(r"\bCitrix\b", re.IGNORECASE),
    "VMware Horizon": re.compile(r"VMware\s+Horizon", re.IGNORECASE),
    "Azure Virtual Desktop": re.compile(r"Azure\s+Virtual\s+Desktop|AVD", re.IGNORECASE),
}

LINK_KEYWORDS = (
    "security",
    "compliance",
    "certification",
    "certifications",
    "privacy",
    "trust",
    "governance",
)

HEADERS = {
    "User-Agent": "BPO-Certification-Scraper/1.0",
}


@dataclass
class ScanResult:
    url: str
    certifications: set[str]
    remote_environment_mentions: set[str]
    pages_scanned: int
    pages_with_hits: int


def read_urls(path: str) -> list[str]:
    with open(path, "r", encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip() and not line.startswith("#")]


def is_same_domain(base: str, target: str) -> bool:
    base_host = urlparse(base).netloc.lower()
    target_host = urlparse(target).netloc.lower()
    return base_host == target_host


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    normalized = parsed._replace(fragment="").geturl()
    return normalized.rstrip("/") or normalized


def find_internal_links(base_url: str, html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    links: list[str] = []
    for anchor in soup.find_all("a", href=True):
        href = anchor["href"].strip()
        if href.startswith("mailto:") or href.startswith("tel:"):
            continue
        absolute = urljoin(base_url, href)
        if not is_same_domain(base_url, absolute):
            continue
        if any(keyword in href.lower() for keyword in LINK_KEYWORDS):
            links.append(normalize_url(absolute))
    return list(dict.fromkeys(links))


def extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = " ".join(soup.stripped_strings)
    return re.sub(r"\s+", " ", text)


def match_certifications(text: str) -> set[str]:
    matches = set()
    for label, pattern in CERTIFICATION_PATTERNS.items():
        if pattern.search(text):
            matches.add(label)
    return matches


def match_remote_environment_mentions(text: str) -> set[str]:
    matches = set()
    for label, pattern in REMOTE_ENV_PATTERNS.items():
        if pattern.search(text):
            matches.add(label)
    return matches


def fetch(url: str, timeout: int = 20) -> str:
    response = requests.get(url, headers=HEADERS, timeout=timeout)
    response.raise_for_status()
    return response.text


def scan_site(url: str, max_pages: int, delay: float) -> ScanResult:
    queue = deque([normalize_url(url)])
    seen = set()
    certifications: set[str] = set()
    remote_environment_mentions: set[str] = set()
    pages_scanned = 0
    pages_with_hits = 0

    while queue and pages_scanned < max_pages:
        current = queue.popleft()
        if current in seen:
            continue
        seen.add(current)
        try:
            html = fetch(current)
        except requests.RequestException:
            continue

        pages_scanned += 1
        text = extract_text(html)
        page_matches = match_certifications(text)
        remote_matches = match_remote_environment_mentions(text)
        if page_matches:
            pages_with_hits += 1
            certifications.update(page_matches)
        if remote_matches:
            remote_environment_mentions.update(remote_matches)

        if pages_scanned < max_pages:
            for link in find_internal_links(current, html):
                if link not in seen:
                    queue.append(link)

        if delay:
            time.sleep(delay)

    return ScanResult(
        url=url,
        certifications=certifications,
        remote_environment_mentions=remote_environment_mentions,
        pages_scanned=pages_scanned,
        pages_with_hits=pages_with_hits,
    )


def write_results(results: Iterable[ScanResult], output_path: str) -> None:
    with open(output_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "url",
                "certifications",
                "remote_environment_mentions",
                "pages_scanned",
                "pages_with_hits",
            ],
        )
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "url": result.url,
                    "certifications": ", ".join(sorted(result.certifications)) or "None",
                    "remote_environment_mentions": ", ".join(
                        sorted(result.remote_environment_mentions)
                    )
                    or "None",
                    "pages_scanned": result.pages_scanned,
                    "pages_with_hits": result.pages_with_hits,
                }
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape BPO websites for security certifications.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic scraping with existing URL list:
  python scraper.py --input sites.txt --output results.csv

  # Discovery mode - find insurance BPO websites first:
  python scraper.py --discover --output results.csv --discovered-urls insurance_bpos.txt

  # Discovery with custom search queries:
  python scraper.py --discover --queries search_queries.txt --output results.csv --discovered-urls found.txt

  # Discovery only (no scraping):
  python scraper.py --discover-only --discovered-urls bpo_list.txt
        """
    )

    # Input/Output options
    parser.add_argument("--input", help="Path to text file with one URL per line.")
    parser.add_argument("--output", required=True, help="Path to CSV output.")

    # Discovery options
    parser.add_argument(
        "--discover",
        action="store_true",
        help="Enable discovery mode: find BPO websites before scraping.",
    )
    parser.add_argument(
        "--discover-only",
        action="store_true",
        help="Only run discovery, don't scrape. Saves URLs to --discovered-urls file.",
    )
    parser.add_argument(
        "--discovered-urls",
        default="discovered_bpos.txt",
        help="File to save/load discovered URLs (default: discovered_bpos.txt).",
    )
    parser.add_argument(
        "--queries",
        help="File with custom search queries (one per line). Uses defaults if not specified.",
    )
    parser.add_argument(
        "--results-per-query",
        type=int,
        default=20,
        help="Number of results to collect per search query (default: 20).",
    )
    parser.add_argument(
        "--search-engine",
        choices=["google", "duckduckgo"],
        default="google",
        help="Search engine to use for discovery (default: google).",
    )
    parser.add_argument(
        "--discovery-delay",
        type=float,
        default=2.0,
        help="Delay between discovery requests in seconds (default: 2.0).",
    )

    # Scraping options
    parser.add_argument("--max-pages", type=int, default=6, help="Max pages to scan per site (default: 6).")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between page requests in seconds (default: 0.5).")

    args = parser.parse_args()

    # Validation
    if not args.discover and not args.discover_only and not args.input:
        parser.error("--input is required unless using --discover or --discover-only")

    if (args.discover or args.discover_only) and not DISCOVERY_AVAILABLE:
        parser.error("Discovery mode requires discovery.py module")

    return args


def main() -> None:
    args = parse_args()

    # Handle discovery mode
    if args.discover or args.discover_only:
        print("=" * 70)
        print("BPO WEBSITE DISCOVERY MODE")
        print("=" * 70)
        print()

        # Load search queries
        if args.queries:
            print(f"Loading custom search queries from: {args.queries}")
            queries = load_queries_from_file(args.queries)
            print(f"Loaded {len(queries)} custom queries")
        else:
            print("Using default insurance BPO search queries")
            queries = None  # Will use defaults in discover_bpo_websites

        print()

        # Discover BPO websites
        discovered = discover_bpo_websites(
            queries=queries,
            results_per_query=args.results_per_query,
            search_engine=args.search_engine,
            delay=args.discovery_delay,
        )

        # Save discovered URLs
        save_discovered_urls(discovered, args.discovered_urls)

        print()
        print("=" * 70)

        # If discover-only mode, exit here
        if args.discover_only:
            print(f"Discovery complete! URLs saved to: {args.discovered_urls}")
            print("To scrape these URLs, run:")
            print(f"  python scraper.py --input {args.discovered_urls} --output {args.output}")
            return

        # Otherwise, continue to scraping with discovered URLs
        print("Continuing to scraping phase...")
        print()
        urls = list(discovered)
    else:
        # Regular mode - load URLs from input file
        urls = read_urls(args.input)

    # Scrape the websites
    print("=" * 70)
    print("BPO WEBSITE SCRAPING")
    print("=" * 70)
    print(f"Websites to scan: {len(urls)}")
    print(f"Max pages per site: {args.max_pages}")
    print(f"Delay between requests: {args.delay}s")
    print()

    results = []
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Scanning: {url}")
        try:
            result = scan_site(url, max_pages=args.max_pages, delay=args.delay)
            results.append(result)

            # Print summary for this site
            if result.certifications:
                print(f"  ✓ Found certifications: {', '.join(sorted(result.certifications))}")
            if result.remote_environment_mentions:
                print(f"  ✓ Found remote env: {', '.join(sorted(result.remote_environment_mentions))}")
            if not result.certifications and not result.remote_environment_mentions:
                print(f"  - No certifications or remote environments found")
            print(f"  Pages scanned: {result.pages_scanned}")
            print()
        except Exception as e:
            print(f"  ✗ Error scanning site: {e}")
            print()
            continue

    write_results(results, args.output)

    print("=" * 70)
    print(f"Scraping complete! Results saved to: {args.output}")
    print(f"Total sites scanned: {len(results)}")
    print(f"Sites with certifications: {sum(1 for r in results if r.certifications)}")
    print(f"Sites with remote env: {sum(1 for r in results if r.remote_environment_mentions)}")
    print("=" * 70)


if __name__ == "__main__":
    main()
