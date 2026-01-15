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
    parser = argparse.ArgumentParser(description="Scrape BPO websites for security certifications.")
    parser.add_argument("--input", required=True, help="Path to text file with one URL per line.")
    parser.add_argument("--output", required=True, help="Path to CSV output.")
    parser.add_argument("--max-pages", type=int, default=6, help="Max pages to scan per site.")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between page requests (seconds).")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    urls = read_urls(args.input)
    results = []
    for url in urls:
        results.append(scan_site(url, max_pages=args.max_pages, delay=args.delay))
    write_results(results, args.output)


if __name__ == "__main__":
    main()
