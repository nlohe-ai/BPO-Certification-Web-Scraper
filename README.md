# BPO Certification Web Scraper

This repository contains a lightweight Python scraper that checks BPO (Business Process Outsourcing) websites for common security certifications (e.g., ISO 27001, SOC 2, PCI DSS) and mentions of remote work environments (VDI, Citrix, etc.).

## Features

- **🔍 Automatic Website Discovery**: Find 1000+ insurance BPO websites automatically using search engines
- Scans BPO websites for security certifications (ISO 27001, SOC 2, PCI DSS, etc.)
- Detects remote environment technologies (VDI, Citrix, etc.)
- Exports results to CSV format
- Configurable scan depth and request delays
- Follows internal links intelligently
- Optimized for insurance BPOs serving agencies, brokers, and MGAs

## Quick Start

### Option 1: With Automatic Discovery (Recommended for Large Scale)

```bash
# Install dependencies
pip3 install -r requirements.txt

# Discover insurance BPO websites automatically
python3 scraper.py --discover-only --discovered-urls insurance_bpos.txt --output dummy.csv

# Review and scrape the discovered sites
python3 scraper.py --input insurance_bpos.txt --output results.csv
```

### Option 2: With Manual URL List

```bash
# Install dependencies
pip3 install -r requirements.txt

# Add your URLs to sites.txt (one per line)
nano sites.txt

# Run the scraper
python3 scraper.py --input sites.txt --output results.csv
```

## Full Documentation

- **[INSTRUCTIONS.md](INSTRUCTIONS.md)** - Complete setup and usage guide
- **[DISCOVERY_GUIDE.md](DISCOVERY_GUIDE.md)** - Automatic website discovery guide (for finding 1000+ BPOs)

## Requirements

- Python 3.9 or higher
- beautifulsoup4
- requests

## How It Works

### Discovery Mode (Optional)
1. Searches Google/DuckDuckGo for insurance BPO companies
2. Extracts company website URLs from search results
3. Filters out non-company sites (social media, directories, etc.)
4. Saves unique company URLs to a file

### Scraping Mode
1. Reads URLs from input file or discovery results
2. Crawls each site starting from the homepage
3. Follows internal links with compliance/security keywords
4. Extracts and analyzes page text for certification patterns
5. Detects mentions of remote work environments (VDI, Citrix, etc.)
6. Saves findings to CSV file with certification and remote environment details

## Notes

- Be respectful of website terms of service and robots.txt
- Use appropriate delays between requests
- Some sites may block automated scraping
- Results should be manually verified
