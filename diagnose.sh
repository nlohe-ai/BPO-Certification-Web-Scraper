#!/bin/bash
# Diagnostic script to help troubleshoot discovery issues

echo "========================================="
echo "BPO Scraper Discovery Diagnostics"
echo "========================================="
echo ""

echo "1. Python version:"
python3 --version
echo ""

echo "2. Check if discovery.py exists:"
ls -lh discovery.py
echo ""

echo "3. Test DuckDuckGo connectivity:"
python3 -c "
import requests
try:
    response = requests.get('https://html.duckduckgo.com/html/?q=test', timeout=10)
    print(f'Status code: {response.status_code}')
    print(f'Response length: {len(response.text)} bytes')
    print('✓ DuckDuckGo is accessible')
except Exception as e:
    print(f'✗ Error connecting to DuckDuckGo: {e}')
"
echo ""

echo "4. Test discovery module import:"
python3 -c "
try:
    from discovery import scrape_duckduckgo_results
    print('✓ Discovery module imports successfully')
except Exception as e:
    print(f'✗ Error importing discovery module: {e}')
"
echo ""

echo "5. Run minimal discovery test:"
python3 -c "
from discovery import scrape_duckduckgo_results
print('Testing single query...')
urls = scrape_duckduckgo_results('insurance BPO company', num_results=3)
print(f'Found {len(urls)} URLs:')
for url in urls:
    print(f'  - {url}')
"
echo ""

echo "========================================="
echo "Diagnostics complete"
echo "========================================="
