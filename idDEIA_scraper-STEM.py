"""
WORK IN PROGRESS - NOT YET FUNCTIONAL
------------------------------------------------------
Project Name: DEIA Compliance Scanner
Author: Max J. Tsai
Email: mt8168@gmail.com
License: MIT License
------------------------------------------------------
Description:  
This Python program is designed to identify DEIA (Diversity, Equity, Inclusion, and Accessibility) terms  
in compliance with Executive Order 14151. It is still experimental and should be used at your own risk,  
similar to other open-source software. Contributions and feedback are welcome.  
------------------------------------------------------
"""
from dotenv import load_dotenv
import os

import requests
from bs4 import BeautifulSoup

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, wordnet

from nltk.stem import PorterStemmer, WordNetLemmatizer

import urllib.parse
from urllib.parse import urlparse

import re
from collections import defaultdict

# NLTK resources
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet') #Synonym
nltk.download('punkt_tab')

stemmer = PorterStemmer()

# Load environment variables from .env file
load_dotenv()

# Fetch and parse the website content
def fetch_website_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        soup = BeautifulSoup(response.content, 'html.parser')
        
        ''' ONLY extract <p> tags
        paragraphs = soup.find_all('p')  # Extract all paragraphs        
        text = ' '.join([para.get_text() for para in paragraphs])
        '''
        text = " ".join(soup.get_text().split()) # Extract all text from the page
        ## print (text)
        ## input("MJT: Enter to continue")
        return text, soup
    except requests.exceptions.RequestException as e:
        ## print(f"Error fetching website content: {e}")
        return "", None

# Function to identify key phrases related to DEI in the content, including synonyms
def identify_dei_phrases(text, dei_phrases):
    # Tokenize the text
    tokens = word_tokenize(text.lower())  # Convert to lower case
    stop_words = set(stopwords.words('english'))  # Define stop words
    filtered_tokens = [word for word in tokens if word.isalpha() and word not in stop_words]

    # Find matching phrases
    found_phrases = []

    token_stem = stemmer.stem(filtered_tokens)
    for token in filtered_tokens:
        if token in dei_phrases:
            found_phrases.append(token)
    print (found_phrases)

    '''
    found_phrases = []
    for phrase in dei_phrases:
        # print (phrase)
        # print (filtered_tokens)
        # input("Enter to continue")

        if phrase in ' '.join(filtered_tokens):

            count = ' '.join(filtered_tokens).count(phrase)
            #print (f"DEI-related phrase found: {phrase} | Count: {count}")
            
            found_phrases.append(phrase + " (" + str(count) + ")")
    '''
    
    return found_phrases

# Function with the option to get synonyms for DEI-related terms from WordNet
def get_dei_phrases(gen_synonyms=False):

    core_deia_terms = [
    "diversity", "equity", "inclusion", "accessibility", "affirmative action",
    "bias", "cultural competence", "disparity", "discrimination", "equal opportunity",
    "underrepresented", "inclusionary", "merit", "minority", "preference",
    "protected class", "quota", "race", "sex", "inequality", "training",
    "workforce balancing"
    ]

    deia_terms = sorted(list(set(core_deia_terms)))  # Remove duplicates and sort;

    '''
    #LOADED VERSION 
    deia_terms = [
    # Diversity
    "Multicultural", "Heterogeneity", "Representation", "Pluralism", "Inclusion", "Difference", 
    "Variety", "Intersectionality", "Demographic", "Background", "Identity", "Cultural awareness",
    
    # Equity
    "Fairness", "Justice", "Equality", "Impartiality", "Redistribution", "Inclusiveness", 
    "Equal opportunity", "Accessibility", "Affirmative action", "Accountability", "Non-discrimination", 
    "Redistribution of resources",
    
    # Inclusion
    "Belonging", "Engagement", "Participation", "Integration", "Involvement", "Acceptance", 
    "Empowerment", "Community", "Unity", "Respect", "Open-mindedness", "Welcoming",
    
    # Accessibility
    "Usability", "Adaptability", "Availability", "Accommodation", "Universal design", "Equal access", 
    "Barrier-free", "Disability inclusion", "Access rights", "Accessibility tools", "Assistive technology", 
    "Access for all"
    ]'''

    if gen_synonyms:    
        dei_wordphrases = set(deia_terms)  # Start with the core terms

        # Get synonyms for each DEI term using WordNet
        for term in deia_terms:
            for syn in wordnet.synsets(term):
                for lemma in syn.lemmas():
                    dei_wordphrases.add(lemma.name().lower())
    else:
        dei_wordphrases = [word.lower() for word in deia_terms]

    return list(dei_wordphrases)

# Function to check if the URL points to an undesirable file type
def is_desirable_url(url):
    # Define undesirable file types (PDFs, videos, JavaScript, CSS)
    undesirable_extensions = ['.pdf', '.mp4', '.mov', '.avi', '.js', '.css', '.jpeg', '.jpg', '.png', '.gif', '.webm', 'xml', 'json', 'ppt', 'pptx', 'doc', 'docx', 'xls', 'xlsx', 'csv', 'zip', 'rar', 'tar', 'gz', '7z', 'exe', 'bin', 'dmg', 'iso', 'apk', 'deb', 'rpm', 'torrent', 'woff', 'woff2', 'ttf', 'otf', 'eot', 'svg', 'ico', 'mp3', 'wav', 'flac', 'ogg', 'wma', 'aac', 'm4a', 'opus', 'mid', 'midi', 'kar', 'webp', 'bmp', 'tiff', 'tif', 'eps', 'svgz', '3gp', '3g2', 'mkv', 'webm', 'flv', 'vob', 'ogv', 'ogg', 'drc', 'gifv', 'mng', 'avi', 'mov', 'qt', 'wmv', 'yuv', 'rm', 'rmvb', 'asf', 'amv', 'mpg', 'mp2', 'mpeg', 'mpe', 'mpv', 'mpg', 'mpeg', 'm2v', 'm4v', 'svi', '3gp', '3g2', 'mxf', 'roq', 'nsv', 'flv', 'f4v', 'f4p', 'f4a', 'f4b']
    return not any(url.endswith(ext) for ext in undesirable_extensions)

# Function to check if the URL is a bookmark link (i.e., containing '#')
def is_bookmark_link(url):
    #return url.startswith('#')
    return '#' in url

# Function to crawl the website and collect subpage URLs
def crawl_website(url, visited=set(), dei_phrases=[]):
    to_visit = [url]
    found_phrases = []

    while to_visit:
        current_url = to_visit.pop()
        if current_url not in visited:
            visited.add(current_url)
            #debug# print(f"Scraping: {current_url}")

            # Fetch the content of the current page
            text, soup = fetch_website_content(current_url)
            if text:
                # Identify DEI phrases on the current page
                dei_phrases_found = identify_dei_phrases(text, dei_phrases)

                if dei_phrases_found:
                    print(f"DEI-related phrases found: {current_url} | {dei_phrases_found}")
                found_phrases.extend(dei_phrases_found)
            

            # Extract all links in the page
            if soup:
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    # Resolve relative URLs to absolute URLs
                    full_url = urllib.parse.urljoin(current_url, href)
                    parsed_url = urlparse(full_url)
                    # Only follow links within the same domain
                    if parsed_url.netloc == urlparse(url).netloc and full_url not in visited and is_desirable_url(full_url) and not is_bookmark_link(full_url):
                        to_visit.append(full_url)

    return found_phrases

# Function to combine word counts -- helped by Copilot 
def combine_word_counts(paragraphs):
    # Use a regular expression to find all occurrences of the pattern "word (count)"
    pattern = re.compile(r'(\w+)\s\((\d+)\)')
    
    # Use a dictionary to store the combined counts
    word_counts = defaultdict(int)
    
    for paragraph in paragraphs:
        matches = pattern.findall(paragraph)
        for word, count in matches:
            word_counts[word] += int(count)
    
    # Format the output
    result = [f"{word} ({count})" for word, count in word_counts.items()]
    return "; ".join(result)

# Main function to execute the process
def main():

    url = os.getenv("URL")
    if not url:
        url = input("Enter the website URL: ")
    else:
        print(f"Scanning website: {url}")

    dei_phrases = get_dei_phrases(False)    #True for Synonyms

    # Stemming the DEI phrases - PorterStemmer
    core_stems = {stemmer.stem(term) for term in dei_phrases}
    
    '''print (dei_phrases)
    print ("\n\n",core_stems)
    input("Enter to continue")'''
    
    found_phrases = crawl_website(url, dei_phrases=dei_phrases)
    #found_phrases = crawl_website(url, dei_phrases=core_stems)

    if found_phrases:
        print("\n======\nKey DEI-related phrases found that may violate Executive Order 14173:")
        ''' this was before I added counting of macthed phrases
            for phrase in set(found_phrases):  # Using set to avoid duplicates
            print(f"- {phrase}")'
        '''
        combined_counts = combine_word_counts(found_phrases)
        print(combined_counts)
    else:
        print("No DEI-related phrases found that may violate Executive Order 14173.")

if __name__ == "__main__":
    main()
