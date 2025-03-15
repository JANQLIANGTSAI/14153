'''
create a python code to scrape a website entered by the user to identify pages with DEIA phrases and list the number of occurrences by each page
'''

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
from collections import defaultdict

def get_deia_phrases():
    # Common DEIA-related phrases (can be expanded)
    return [
        'diversity', 'equity', 'inclusion', 'accessibility',
        'inclusive', 'equal opportunity', 'cultural competence',
        'unconscious bias', 'representation', 'belonging',
        'social justice', 'fairness', 'multicultural',
        'disability accommodation', 'gender equality'
    ]

def crawl_website(start_url, max_pages=50):
    # Initialize data structures
    visited_urls = set()
    url_queue = [start_url]
    deia_counts = defaultdict(lambda: defaultdict(int))
    deia_phrases = get_deia_phrases()
    
    # Headers to mimic browser behavior
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    while url_queue and len(visited_urls) < max_pages:
        url = url_queue.pop(0)
        
        if url in visited_urls:
            continue

        try:
            # Fetch page content
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            text_content = soup.get_text().lower()

            # Count DEIA phrases
            for phrase in deia_phrases:
                count = len(re.findall(r'\b' + re.escape(phrase) + r'\b', text_content))
                if count > 0:
                    deia_counts[url][phrase] = count

            # Find all links on the page
            for link in soup.find_all('a', href=True):
                absolute_url = urljoin(url, link['href'])
                # Ensure we stay within the same domain
                if absolute_url.startswith(start_url.split('/')[0] + '//' + start_url.split('/')[2]):
                    if absolute_url not in visited_urls and absolute_url not in url_queue:
                        url_queue.append(absolute_url)

            visited_urls.add(url)
            print(f"Processed: {url} ({len(visited_urls)}/{max_pages})")

        except (requests.RequestException, Exception) as e:
            print(f"Error processing {url}: {str(e)}")
            continue

    return deia_counts

def display_results(deia_counts):
    print("\nDEIA Phrase Occurrences by Page:")
    print("=" * 50)
    
    for url, phrases in deia_counts.items():
        print(f"\nPage: {url}")
        print("-" * 40)
        total_count = 0
        for phrase, count in phrases.items():
            print(f"{phrase}: {count}")
            total_count += count
        print(f"Total DEIA phrases found: {total_count}")
        print("-" * 40)

def main():
    # Get website URL from user
    website_url = input("Enter the website URL to scrape (e.g., https://example.com): ").strip()
    
    # Ensure URL starts with http:// or https://
    if not website_url.startswith(('http://', 'https://')):
        website_url = 'https://' + website_url

    print(f"\nStarting to scrape {website_url}")
    print("This may take some time depending on the website size...")
    
    # Crawl website and get DEIA counts
    deia_counts = crawl_website(website_url)
    
    # Display results
    display_results(deia_counts)
    
    # Summary statistics
    total_pages = len(deia_counts)
    total_occurrences = sum(sum(phrases.values()) for phrases in deia_counts.values())
    print(f"\nSummary:")
    print(f"Total pages analyzed: {total_pages}")
    print(f"Total DEIA phrase occurrences: {total_occurrences}")

if __name__ == "__main__":
    # Required libraries: requests, beautifulsoup4
    try:
        main()
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        print(f"An error occurred: {str(e)}")