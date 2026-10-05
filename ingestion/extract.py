"""
Extract function: Scrapes Kubernetes documentation.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from typing import List, Dict, Set


def extract(start_url: str = "https://kubernetes.io/docs/", max_pages: int = 150) -> List[Dict[str, str]]:
    """
    Scrape Kubernetes documentation starting from the given URL.
    
    Args:
        start_url: The starting URL for scraping (default: Kubernetes docs home)
        max_pages: Maximum number of pages to scrape (default: 150)
    
    Returns:
        List of dicts with {url, title, raw_html, text}
    """
    visited: Set[str] = set()
    to_visit: List[str] = [start_url]
    results: List[Dict[str, str]] = []
    
    base_domain = urlparse(start_url).netloc
    
    while to_visit and len(results) < max_pages:
        url = to_visit.pop(0)
        
        # Skip if already visited
        if url in visited:
            continue
        
        visited.add(url)
        
        try:
            # Add a small delay to be respectful
            time.sleep(0.5)
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            raw_html = response.text
            soup = BeautifulSoup(raw_html, 'html.parser')
            
            # Extract title
            title_tag = soup.find('title')
            title = title_tag.get_text(strip=True) if title_tag else url
            
            # Extract main content text
            # Kubernetes docs typically use main tag or article tag
            main_content = soup.find('main') or soup.find('article') or soup.find('body')
            
            if main_content:
                # Remove script and style elements
                for script in main_content(['script', 'style', 'nav', 'footer', 'header']):
                    script.decompose()
                
                text = main_content.get_text(separator=' ', strip=True)
            else:
                text = soup.get_text(separator=' ', strip=True)
            
            # Store the result
            results.append({
                'url': url,
                'title': title,
                'raw_html': raw_html,
                'text': text
            })
            
            print(f"Scraped {len(results)}/{max_pages}: {title}")
            
            # Find and add new links to visit
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                parsed = urlparse(full_url)
                
                # Only follow links within the docs section and same domain
                if (parsed.netloc == base_domain and 
                    '/docs/' in parsed.path and 
                    full_url not in visited and 
                    full_url not in to_visit and
                    not parsed.fragment):  # Ignore anchor links
                    
                    to_visit.append(full_url)
        
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            continue
    
    print(f"Extraction complete. Scraped {len(results)} pages.")
    return results
