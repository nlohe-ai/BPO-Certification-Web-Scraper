# BPO Certification Web Scraper - Complete Instructions

## Overview
This tool scrapes BPO (Business Process Outsourcing) websites to detect:
- Security certifications (ISO 27001, SOC 2, PCI DSS, HIPAA, etc.)
- Remote work environment mentions (VDI, Citrix, Azure Virtual Desktop, etc.)

**NEW**: The tool now includes automatic website discovery to find 1000+ insurance BPO companies without manual URL compilation.

The results are saved in a CSV file for easy analysis.

## Two Ways to Use This Tool

1. **Discovery Mode** - Automatically find insurance BPO websites using search engines (recommended for finding 1000+ sites)
2. **Manual Mode** - Provide your own list of URLs to scrape

---

## Discovery Mode (NEW!)

If you need to scan 1000+ insurance BPO websites but don't have a URL list, use discovery mode.

### Quick Discovery Example

```bash
# Find insurance BPO websites automatically
python3 scraper.py --discover-only --discovered-urls insurance_bpos.txt --output dummy.csv

# This will search for insurance BPOs and save URLs to insurance_bpos.txt
# Then you can review and scrape them:
python3 scraper.py --input insurance_bpos.txt --output results.csv
```

### Discovery Options

| Option | Description |
|--------|-------------|
| `--discover-only` | Find websites but don't scrape yet |
| `--discover` | Find websites AND scrape them immediately |
| `--discovered-urls FILE` | Where to save discovered URLs |
| `--queries FILE` | Custom search queries file |
| `--results-per-query N` | Number of results per query (default: 20) |
| `--search-engine` | Use `google` or `duckduckgo` |

### For Complete Discovery Documentation

**See [DISCOVERY_GUIDE.md](DISCOVERY_GUIDE.md)** for detailed information on:
- How discovery works
- Finding 1000+ insurance BPOs
- Custom search queries
- Best practices and troubleshooting

---

## Prerequisites

### Required Software
1. **Python 3.9 or higher** (This system has Python 3.11.14 installed ✓)
   - To check your version: `python3 --version`

2. **pip** (Python package installer - usually comes with Python)
   - To check: `pip3 --version`

3. **Internet connection** - Required to download packages and scrape websites

---

## Installation Steps

### Step 1: Navigate to the Project Directory
Open your terminal and navigate to this project:
```bash
cd /home/user/BPO-Certification-Web-Scraper
```

### Step 2: Install Required Python Packages
Run this command to install the dependencies:
```bash
pip3 install -r requirements.txt
```

This installs:
- `beautifulsoup4` - For parsing HTML
- `requests` - For making HTTP requests

**Note**: If you get permission errors, you can use a virtual environment (optional but recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Configuration

### Step 3: Add URLs to Scan
Edit the `sites.txt` file and add one URL per line:

```bash
nano sites.txt  # Or use any text editor
```

Example content:
```
https://www.examplebpo.com
https://www.anotherbpo.com
https://www.yetanotherbpo.com
```

**Tips**:
- Include the full URL with `https://` or `http://`
- One URL per line
- Lines starting with `#` are treated as comments and ignored
- Remove the example.com placeholder

---

## Running the Scraper

### Basic Usage
```bash
python3 scraper.py --input sites.txt --output results.csv
```

This will:
- Read URLs from `sites.txt`
- Scan up to 6 pages per site (default)
- Save results to `results.csv`
- Wait 0.5 seconds between requests (to be polite to servers)

### Advanced Usage

**Scan more pages per site**:
```bash
python3 scraper.py --input sites.txt --output results.csv --max-pages 10
```

**Increase delay between requests** (recommended for slower servers):
```bash
python3 scraper.py --input sites.txt --output results.csv --delay 1.0
```

**Scan fewer pages (faster)**:
```bash
python3 scraper.py --input sites.txt --output results.csv --max-pages 3 --delay 0.2
```

**Custom input/output files**:
```bash
python3 scraper.py --input my_urls.txt --output my_results.csv
```

### Command-Line Options

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--input` | Yes | - | Path to text file with URLs (one per line) |
| `--output` | Yes | - | Path where CSV results will be saved |
| `--max-pages` | No | 6 | Maximum number of pages to scan per site |
| `--delay` | No | 0.5 | Seconds to wait between page requests |

---

## Understanding the Output

The scraper creates a CSV file with these columns:

| Column | Description |
|--------|-------------|
| `url` | The website that was scanned |
| `certifications` | Comma-separated list of certifications found (e.g., "ISO 27001, SOC 2") |
| `remote_environment_mentions` | Remote work technologies found (e.g., "VDI, Citrix") |
| `pages_scanned` | Number of pages that were successfully scanned |
| `pages_with_hits` | Number of pages where certifications were found |

**Example output**:
```csv
url,certifications,remote_environment_mentions,pages_scanned,pages_with_hits
https://example.com,"ISO 27001, SOC 2",VDI,5,2
https://another.com,None,"Citrix, Azure Virtual Desktop",3,0
```

### Opening the Results
You can open the CSV file with:
- Microsoft Excel
- Google Sheets
- LibreOffice Calc
- Any text editor

---

## How It Works

1. **Starts at homepage**: The scraper begins with each URL you provide
2. **Follows internal links**: It looks for links containing keywords like "security", "compliance", "certification", "privacy"
3. **Scans page text**: Extracts visible text and searches for certification patterns
4. **Detects certifications**: Uses regular expressions to find mentions of:
   - ISO 27001
   - SOC 1, SOC 2, SOC 3
   - PCI DSS
   - HIPAA
   - HITRUST
   - GDPR
5. **Detects remote environments**: Looks for mentions of:
   - VDI (Virtual Desktop Infrastructure)
   - Remote Desktop
   - Citrix
   - VMware Horizon
   - Azure Virtual Desktop (AVD)
6. **Respects limits**: Only scans up to `--max-pages` per site
7. **Saves results**: Writes all findings to CSV

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'bs4'"
**Solution**: Install the required packages:
```bash
pip3 install -r requirements.txt
```

### Issue: "Permission denied" when installing packages
**Solution**: Use a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Scraper times out or fails for certain sites
**Possible causes**:
- Website blocks automated scraping
- Website requires JavaScript (this scraper only handles static HTML)
- Network connectivity issues

**Solutions**:
- Increase the timeout (edit `scraper.py` line 112 to use a larger timeout value)
- Try a different URL for the same company
- Some sites may be inaccessible to automated tools

### Issue: No certifications found but you know they exist
**Possible causes**:
- Certifications are on pages not linked with keywords
- Certifications are in images or PDFs (not detected)
- Different wording/format than expected patterns

**Solutions**:
- Increase `--max-pages` to scan more pages
- Add more keywords to `LINK_KEYWORDS` in `scraper.py`
- Modify the regex patterns in `CERTIFICATION_PATTERNS`

---

## Customization

### Adding More Certifications
Edit `scraper.py` and add patterns to the `CERTIFICATION_PATTERNS` dictionary (around line 13):

```python
CERTIFICATION_PATTERNS = {
    "ISO 27001": re.compile(r"\bISO\s*27001\b", re.IGNORECASE),
    # Add your custom certification here:
    "ISO 9001": re.compile(r"\bISO\s*9001\b", re.IGNORECASE),
}
```

### Adding More Remote Environment Keywords
Edit the `REMOTE_ENV_PATTERNS` dictionary (around line 24):

```python
REMOTE_ENV_PATTERNS = {
    "VDI": re.compile(r"\bVDI\b|virtual\s+desktop", re.IGNORECASE),
    # Add your custom pattern here:
    "AWS WorkSpaces": re.compile(r"AWS\s+WorkSpaces", re.IGNORECASE),
}
```

### Changing Link Keywords
Edit the `LINK_KEYWORDS` tuple (around line 32) to look for different types of pages:

```python
LINK_KEYWORDS = (
    "security",
    "compliance",
    "about",  # Add this to also check "About" pages
)
```

---

## Best Practices

1. **Start small**: Test with 2-3 URLs before running a large batch
2. **Be respectful**: Use appropriate delays (`--delay 1.0` or higher for production)
3. **Check robots.txt**: Ensure you're allowed to scrape the sites
4. **Review results**: Some matches may be false positives - always verify
5. **Keep updated**: Websites change - re-run periodically for fresh data

---

## Example Workflow

```bash
# 1. Navigate to project
cd /home/user/BPO-Certification-Web-Scraper

# 2. Edit sites.txt with your URLs
nano sites.txt

# 3. Run the scraper
python3 scraper.py --input sites.txt --output results.csv --max-pages 10 --delay 1.0

# 4. View the results
cat results.csv
# Or open in Excel/Sheets
```

---

## Quick Reference

**Install dependencies**:
```bash
pip3 install -r requirements.txt
```

**Run with defaults**:
```bash
python3 scraper.py --input sites.txt --output results.csv
```

**Get help**:
```bash
python3 scraper.py --help
```

---

## Support

If you encounter issues:
1. Check the Troubleshooting section above
2. Verify Python version is 3.9+
3. Ensure all dependencies are installed
4. Check that URLs in sites.txt are valid and accessible
