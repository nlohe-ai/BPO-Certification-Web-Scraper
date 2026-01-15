# BPO Certification Web Scraper

This repository contains a lightweight Python scraper that checks insurance BPO websites for common security certifications (e.g., ISO 27001, SOC 2, PCI DSS) and outputs a CSV summary.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python scraper.py --input sites.txt --output certifications.csv
```

## How it works

- Reads a list of URLs from `--input` (one per line).
- Crawls each site, starting with the homepage.
- Follows a small set of internal links that look related to compliance/security.
- Extracts page text and matches certification patterns.
- Detects mentions of remote environments/VDIs for brokers.

## Customization

Edit `CERTIFICATION_PATTERNS` and `REMOTE_ENV_PATTERNS` in `scraper.py` to add/remove matches or change the matching logic.

## Notes

Be mindful of each site's terms of service and robots.txt.
