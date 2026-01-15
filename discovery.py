import re
import time
from typing import Set
from urllib.parse import parse_qs, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# Search queries for insurance BPO companies
# Focused on companies working with agencies, brokers, and MGAs
DEFAULT_SEARCH_QUERIES = [
    "insurance BPO company",
    "insurance BPO services agency",
    "insurance broker BPO services",
    "insurance agency BPO",
    "MGA BPO services",
    "managing general agent BPO",
    "insurance back office BPO",
    "insurance policy administration BPO",
    "insurance processing BPO",
    "P&C insurance BPO",
    "property casualty BPO services",
    "commercial insurance BPO",
    "insurance outsourcing services broker",
    "insurance data entry BPO",
    "insurance claims processing BPO",
]


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
    excluded_paths = ["/search", "/maps", "/news", "/images", "/blog/"]
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
    # Remove www. prefix for consistency
    domain = parsed.netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]
    # Return as full URL with https
    return f"https://{domain}"


def scrape_google_results(query: str, num_results: int = 50, delay: float = 2.0) -> Set[str]:
    """
    Scrape Google search results for the given query.

    NOTE: Google now requires JavaScript for most searches, so this may return 0 results.
    DuckDuckGo is recommended as the primary search engine.

    Args:
        query: Search query string
        num_results: Target number of results to collect
        delay: Delay between page requests in seconds

    Returns:
        Set of discovered URLs
    """
    from urllib.parse import quote_plus

    discovered_urls: Set[str] = set()
    start = 0
    max_pages = (num_results // 10) + 1  # Google shows ~10 results per page

    print(f"  Searching Google for: '{query}'")
    print(f"    Note: Google may block automated searches. Consider using DuckDuckGo instead.")

    for page in range(max_pages):
        try:
            # Google search URL with proper encoding
            search_url = f"https://www.google.com/search?q={quote_plus(query)}&start={start}"

            response = requests.get(search_url, headers=HEADERS, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Check if Google is blocking us
            if "detected unusual traffic" in response.text.lower() or len(soup.find_all("a")) < 5:
                print(f"    Warning: Google may be blocking automated requests")
                print(f"    Try using --search-engine duckduckgo instead")
                break

            # Extract search result links
            # Google search results are in <a> tags with specific patterns
            for anchor in soup.find_all("a", href=True):
                href = anchor["href"]

                # Google wraps actual URLs in /url?q= parameters
                if href.startswith("/url?"):
                    # Parse the query string to extract the actual URL
                    query_params = parse_qs(urlparse(href).query)
                    if "q" in query_params:
                        actual_url = query_params["q"][0]

                        if is_valid_bpo_url(actual_url):
                            clean_url = extract_domain_from_url(actual_url)
                            discovered_urls.add(clean_url)
                            print(f"    Found: {clean_url}")

                # Also check for direct URLs in href
                elif href.startswith("http") and is_valid_bpo_url(href):
                    clean_url = extract_domain_from_url(href)
                    discovered_urls.add(clean_url)
                    print(f"    Found: {clean_url}")

            # Check if we have enough results
            if len(discovered_urls) >= num_results:
                break

            # If we got no results on first page, don't try more pages
            if page == 0 and len(discovered_urls) == 0:
                print(f"    No results found. Google may be blocking requests.")
                break

            # Move to next page
            start += 10

            # Be polite - add delay between requests
            if page < max_pages - 1:
                time.sleep(delay)

        except requests.RequestException as e:
            print(f"    Warning: Failed to fetch page {page + 1}: {e}")
            continue
        except Exception as e:
            print(f"    Warning: Error processing page {page + 1}: {e}")
            continue

    if len(discovered_urls) == 0:
        print(f"  Google returned 0 results (likely blocked)")
        print(f"  TIP: Use --search-engine duckduckgo for better results")
    else:
        print(f"  Discovered {len(discovered_urls)} unique URLs for this query")

    return discovered_urls


def scrape_duckduckgo_results(query: str, num_results: int = 50) -> Set[str]:
    """
    Scrape DuckDuckGo search results (alternative to Google, no rate limiting).

    Args:
        query: Search query string
        num_results: Target number of results to collect

    Returns:
        Set of discovered URLs
    """
    from urllib.parse import unquote, quote_plus

    discovered_urls: Set[str] = set()

    print(f"  Searching DuckDuckGo for: '{query}'")

    try:
        # Encode the query properly
        search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"

        response = requests.get(search_url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # DuckDuckGo wraps URLs in redirect links with uddg= parameter
        # Find all result links
        result_links = soup.find_all("a", class_=["result__a", "result__url"])

        for link in result_links:
            href = link.get("href", "")

            # DuckDuckGo wraps URLs: //duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com...
            if "uddg=" in href:
                # Extract the uddg parameter
                match = re.search(r"uddg=([^&]+)", href)
                if match:
                    encoded_url = match.group(1)
                    # URL decode it
                    actual_url = unquote(encoded_url)

                    # Filter out ads and non-company URLs
                    if is_valid_bpo_url(actual_url) and "duckduckgo.com/y.js" not in actual_url:
                        clean_url = extract_domain_from_url(actual_url)
                        if clean_url not in discovered_urls:
                            discovered_urls.add(clean_url)
                            print(f"    Found: {clean_url}")

                if len(discovered_urls) >= num_results:
                    break

    except Exception as e:
        print(f"    Warning: Error searching DuckDuckGo: {e}")

    print(f"  Discovered {len(discovered_urls)} unique URLs from DuckDuckGo")
    return discovered_urls


def load_queries_from_file(file_path: str) -> list[str]:
    """Load search queries from a text file."""
    queries = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith("#"):
                queries.append(line)
    return queries


def discover_bpo_websites(
    queries: list[str] = None,
    results_per_query: int = 20,
    search_engine: str = "google",
    delay: float = 2.0,
) -> Set[str]:
    """
    Discover BPO company websites using search engines.

    Args:
        queries: List of search queries. If None, uses DEFAULT_SEARCH_QUERIES
        results_per_query: Number of results to collect per query
        search_engine: Which search engine to use ("google" or "duckduckgo")
        delay: Delay between requests (seconds)

    Returns:
        Set of discovered BPO website URLs
    """
    if queries is None:
        queries = DEFAULT_SEARCH_QUERIES

    all_urls: Set[str] = set()

    print(f"Starting BPO website discovery...")
    print(f"Search engine: {search_engine}")
    print(f"Queries to process: {len(queries)}")
    print(f"Target results per query: {results_per_query}")
    print()

    for i, query in enumerate(queries, 1):
        print(f"[{i}/{len(queries)}] Processing query...")

        if search_engine.lower() == "duckduckgo":
            urls = scrape_duckduckgo_results(query, results_per_query)
        else:  # Default to Google
            urls = scrape_google_results(query, results_per_query, delay)

        all_urls.update(urls)
        print(f"  Total unique URLs so far: {len(all_urls)}")
        print()

        # Add delay between different queries
        if i < len(queries):
            time.sleep(delay)

    print(f"Discovery complete! Found {len(all_urls)} unique BPO websites.")
    return all_urls


def save_discovered_urls(urls: Set[str], output_path: str) -> None:
    """Save discovered URLs to a file."""
    sorted_urls = sorted(urls)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Discovered BPO Company Websites\n")
        f.write(f"# Total: {len(sorted_urls)} URLs\n")
        f.write("# Generated by BPO Discovery Module\n")
        f.write("#\n")
        f.write("# You can edit this file to remove unwanted URLs before running the scraper\n")
        f.write("\n")

        for url in sorted_urls:
            f.write(f"{url}\n")

    print(f"Saved {len(sorted_urls)} URLs to: {output_path}")
