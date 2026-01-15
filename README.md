# BPO Certification Web Scraper

This repository contains a lightweight Python scraper that checks BPO (Business Process Outsourcing) websites for common security certifications (e.g., ISO 27001, SOC 2, PCI DSS) and mentions of remote work environments (VDI, Citrix, etc.).

## Features

- Scans BPO websites for security certifications
- Detects remote environment technologies
- Exports results to CSV format
- Configurable scan depth and request delays
- Follows internal links intelligently

## Quick Start

```bash
# Install dependencies
pip3 install -r requirements.txt

# Add your URLs to sites.txt (one per line)
# Then run the scraper
python3 scraper.py --input sites.txt --output results.csv
```

## Full Documentation

For complete instructions including:
- Installation steps
- How to configure URLs
- Command-line options
- Output format details
- Troubleshooting
- Customization guide

**See [INSTRUCTIONS.md](INSTRUCTIONS.md) for the complete guide.**

## Requirements

- Python 3.9 or higher
- beautifulsoup4
- requests

## How It Works

1. Reads URLs from input file (one per line)
2. Crawls each site starting from the homepage
3. Follows internal links with compliance/security keywords
4. Extracts and analyzes page text for certification patterns
5. Detects mentions of remote work environments
6. Saves findings to CSV file

## Notes

- Be respectful of website terms of service and robots.txt
- Use appropriate delays between requests
- Some sites may block automated scraping
- Results should be manually verified
