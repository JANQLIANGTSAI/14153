'''
create a python code to scrape a website entered by the user to identify pages with DEIA phrases and list the number of occurrences by each page
'''

import requests
from bs4 import BeautifulSoup
from collections import Counter
from urllib.parse import urljoin, urlparse
import re

def get_all_links(base_url):
    """Retrieve all internal links from the given website."""
    visited = set()
    to_visit = {base_url}
    internal_links = set()
    domain = urlparse(base_url).netloc
    
    while to_visit:
        url = to_visit.pop()
        if url in visited:
            continue
        
        visited.add(url)
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
        except requests.RequestException:
            continue
        
        soup = BeautifulSoup(response.text, 'html.parser')
        for a_tag in soup.find_all('a', href=True):
            link = urljoin(base_url, a_tag['href'])
            if urlparse(link).netloc == domain and link not in visited:
                to_visit.add(link)
                internal_links.add(link)
    
    return internal_links

def count_deia_phrases(text, phrases):
    """Count occurrences of DEIA-related phrases in the given text."""
    counter = Counter()
    for phrase in phrases:
        counter[phrase] = len(re.findall(r'\b' + re.escape(phrase) + r'\b', text, re.IGNORECASE))
    return counter

def scrape_deia_content(base_url):
    """Scrape the website for DEIA-related content."""
    deia_phrases = ["diversity", "equity", "inclusion", "accessibility", "belonging", "justice", "inclusive", "equal opportunity"]
    results = {}
    
    links = get_all_links(base_url)
    for link in links:
        try:
            response = requests.get(link, timeout=5)
            response.raise_for_status()
            text = BeautifulSoup(response.text, 'html.parser').get_text()
            phrase_counts = count_deia_phrases(text, deia_phrases)
            results[link] = phrase_counts
        except requests.RequestException:
            continue
    
    return results

def main():
    base_url = input("Enter the website URL: ")
    results = scrape_deia_content(base_url)
    
    for page, counts in results.items():
        print(f"\nPage: {page}")
        for phrase, count in counts.items():
            if count > 0:
                print(f"  {phrase}: {count}")

if __name__ == "__main__":
    main()
