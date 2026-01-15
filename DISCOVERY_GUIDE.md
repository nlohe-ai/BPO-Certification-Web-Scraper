# BPO Website Discovery Guide

## Overview

The discovery feature automatically finds insurance BPO company websites using search engines, eliminating the need to manually compile a list of 1000+ URLs.

## How It Works

The discovery module:
1. Takes search queries related to insurance BPOs
2. Searches using Google or DuckDuckGo
3. Extracts company website URLs from search results
4. Filters out non-company sites (social media, directories, etc.)
5. Saves unique URLs to a file
6. Optionally continues to scrape the discovered sites

## Quick Start

### Discovery Only (Find URLs, Don't Scrape Yet)

```bash
# Use default insurance BPO queries
python3 scraper.py --discover-only --discovered-urls insurance_bpos.txt --output dummy.csv

# Then review and edit the discovered URLs
nano insurance_bpos.txt

# Finally, scrape the discovered URLs
python3 scraper.py --input insurance_bpos.txt --output results.csv
```

### Discovery + Scraping (All in One)

```bash
# Discover and scrape in one command
python3 scraper.py --discover --output results.csv --discovered-urls insurance_bpos.txt
```

## Using Custom Search Queries

The default queries target insurance BPOs working with agencies, brokers, and MGAs. You can customize these:

### Option 1: Edit the Provided File

Edit `search_queries.txt`:
```bash
nano search_queries.txt
```

Add or modify queries:
```
insurance BPO company
insurance broker BPO services
MGA back office services
property casualty BPO
# Add your custom queries here
```

Then run with custom queries:
```bash
python3 scraper.py --discover-only --queries search_queries.txt --discovered-urls bpos.txt --output dummy.csv
```

### Option 2: Create Your Own Query File

```bash
# Create custom query file
cat > my_queries.txt << EOF
insurance agency outsourcing
insurance BPO SOC 2
insurance remote BPO
EOF

# Use it
python3 scraper.py --discover-only --queries my_queries.txt --discovered-urls bpos.txt --output dummy.csv
```

## Command-Line Options

### Discovery Options

| Option | Default | Description |
|--------|---------|-------------|
| `--discover` | - | Find BPO websites, then scrape them |
| `--discover-only` | - | Only find URLs, don't scrape (saves time) |
| `--discovered-urls` | `discovered_bpos.txt` | File to save discovered URLs |
| `--queries` | Built-in queries | Custom search queries file |
| `--results-per-query` | 20 | Number of results per search query |
| `--search-engine` | `google` | `google` or `duckduckgo` |
| `--discovery-delay` | 2.0 | Seconds between search requests |

### Examples

**1. Find 1000+ URLs using default queries:**
```bash
python3 scraper.py --discover-only \
  --results-per-query 50 \
  --discovered-urls insurance_bpos.txt \
  --output dummy.csv
```

With 15 default queries × 50 results = ~750 URLs (after deduplication, expect 300-500 unique domains)

**2. Use DuckDuckGo (no rate limits, but fewer results):**
```bash
python3 scraper.py --discover-only \
  --search-engine duckduckgo \
  --discovered-urls bpos.txt \
  --output dummy.csv
```

**3. Fast discovery with minimal delay:**
```bash
python3 scraper.py --discover-only \
  --discovery-delay 1.0 \
  --results-per-query 30 \
  --discovered-urls bpos.txt \
  --output dummy.csv
```

**4. Discovery with custom queries, then scrape:**
```bash
python3 scraper.py --discover \
  --queries my_insurance_queries.txt \
  --results-per-query 40 \
  --output certification_results.csv \
  --discovered-urls insurance_bpos.txt \
  --max-pages 10
```

## Default Search Queries

The tool comes with 15 pre-configured queries targeting insurance BPOs:

```
insurance BPO company
insurance BPO services agency
insurance broker BPO services
insurance agency BPO
MGA BPO services
managing general agent BPO
insurance back office BPO
insurance policy administration BPO
insurance processing BPO
P&C insurance BPO
property casualty BPO services
commercial insurance BPO
insurance outsourcing services broker
insurance data entry BPO
insurance claims processing BPO
```

These are optimized for finding companies that work with:
- Insurance agencies
- Insurance brokers
- MGAs (Managing General Agents)

## Best Practices

### 1. Start with Discovery-Only Mode

Don't discover and scrape in one go for large batches:

```bash
# Good: Discover first
python3 scraper.py --discover-only --discovered-urls bpos.txt --output dummy.csv

# Review and edit the list
nano bpos.txt

# Then scrape
python3 scraper.py --input bpos.txt --output results.csv
```

**Why?** You can review the discovered URLs, remove obvious non-BPOs, and avoid wasting time scraping irrelevant sites.

### 2. Use Appropriate Delays

Be respectful of search engines:

```bash
# For Google (strict rate limits)
--discovery-delay 3.0

# For DuckDuckGo (more lenient)
--discovery-delay 1.0
```

### 3. Adjust Results Per Query

More results per query = fewer duplicate domains but longer discovery time:

```bash
# Quick discovery: fewer results
--results-per-query 10

# Comprehensive: more results
--results-per-query 50
```

### 4. Combine Multiple Search Engines

Run discovery twice with different engines, then combine:

```bash
# Google search
python3 scraper.py --discover-only --search-engine google --discovered-urls google_bpos.txt --output dummy.csv

# DuckDuckGo search
python3 scraper.py --discover-only --search-engine duckduckgo --discovered-urls ddg_bpos.txt --output dummy.csv

# Combine (removes duplicates)
cat google_bpos.txt ddg_bpos.txt | grep -v "^#" | sort -u > combined_bpos.txt
```

## Filtering & Validation

The discovery module automatically filters out:
- Social media sites (Facebook, Twitter, LinkedIn, YouTube)
- Job boards (Indeed, Glassdoor)
- Directories and review sites (Clutch, Gartner)
- Search engines themselves
- News and media sites

Only legitimate company websites are included.

## Expected Results

### Discovery Time

- **10 queries × 20 results/query**: ~5-10 minutes
- **15 queries × 30 results/query**: ~10-15 minutes
- **20 queries × 50 results/query**: ~20-30 minutes

Time increases with:
- More queries
- More results per query
- Longer delays between requests

### URL Yield

From search results, expect:
- **Google**: 40-60% of results are unique company websites
- **DuckDuckGo**: 30-50% (fewer total results)

Example: 15 queries × 50 results = 750 raw results → ~300-450 unique company domains

## Troubleshooting

### Issue: "Discovery complete! Found 0 unique BPO websites"

**Possible causes:**
- Rate limited by search engine
- Search engine HTML structure changed
- Network issues

**Solutions:**
1. Try DuckDuckGo instead: `--search-engine duckduckgo`
2. Increase delay: `--discovery-delay 5.0`
3. Reduce results per query: `--results-per-query 10`
4. Try different queries in `search_queries.txt`

### Issue: Rate Limited / CAPTCHAs

**Solution:**
- Increase delays: `--discovery-delay 5.0`
- Use DuckDuckGo (no CAPTCHAs)
- Run discovery in smaller batches
- Use a VPN or different network

### Issue: Found Irrelevant Websites

**Solution:**
- Review `discovered_urls` file and manually remove non-BPOs
- Adjust search queries to be more specific
- Use more targeted queries in custom query file

### Issue: Not Enough Results

**Solution:**
- Increase results per query: `--results-per-query 100`
- Add more search queries to `search_queries.txt`
- Try both Google and DuckDuckGo, combine results
- Add geographic queries: "insurance BPO Philippines", "insurance BPO India"

## Advanced: Custom Filtering

If you want to modify what URLs are included/excluded, edit `discovery.py`:

```python
# Around line 40 in discovery.py
def is_valid_bpo_url(url: str) -> bool:
    """Check if URL looks like a legitimate BPO company website."""

    # Add your custom filtering logic here
    excluded_domains = [
        "google.com",
        "linkedin.com",
        # Add more domains to exclude
    ]

    # Your custom logic
```

## Complete Workflow Example

Here's a complete workflow to discover and scrape 1000+ insurance BPOs:

```bash
# Step 1: Discover URLs with comprehensive settings
python3 scraper.py --discover-only \
  --queries search_queries.txt \
  --results-per-query 50 \
  --search-engine google \
  --discovery-delay 3.0 \
  --discovered-urls insurance_bpos_raw.txt \
  --output dummy.csv

# Step 2: Review and clean the list
nano insurance_bpos_raw.txt
# Remove any obviously wrong URLs

# Step 3: (Optional) Discover more with DuckDuckGo
python3 scraper.py --discover-only \
  --queries search_queries.txt \
  --results-per-query 30 \
  --search-engine duckduckgo \
  --discovered-urls ddg_bpos.txt \
  --output dummy.csv

# Step 4: Combine and deduplicate
cat insurance_bpos_raw.txt ddg_bpos.txt | grep -v "^#" | sort -u > final_bpo_list.txt

# Step 5: Scrape all discovered sites
python3 scraper.py \
  --input final_bpo_list.txt \
  --output certification_results.csv \
  --max-pages 10 \
  --delay 1.0

# Result: Comprehensive scan of 500-1000+ insurance BPOs
```

## Notes & Limitations

1. **Search Engine Terms of Service**: Web scraping search results may violate ToS. Consider using official APIs for production use.

2. **Rate Limiting**: Search engines may block or rate-limit your requests. Use appropriate delays.

3. **Result Quality**: Not all discovered URLs will be relevant. Manual review is recommended.

4. **Deduplication**: The tool automatically deduplicates domains (e.g., `company.com` and `www.company.com` are treated as the same).

5. **Coverage**: Some BPOs may not appear in search results. Consider supplementing with industry directories.

## Getting Help

If discovery isn't working:
1. Check the troubleshooting section above
2. Try DuckDuckGo instead of Google
3. Manually test your search queries in a browser first
4. Consider using the traditional method: manually compile URLs, save to `sites.txt`, run without discovery

For complex discovery needs, consider:
- Using official search engine APIs (Google Custom Search API, Bing Search API)
- Scraping industry directories (Clutch, GoodFirms, insurance BPO directories)
- Purchasing/licensing BPO company databases
