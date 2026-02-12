"""
Web scraping module for offline browsing
"""
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict
import time
class WebScraper:
    """Scrape web content for local caching"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch(self, url: str) -> Optional[Dict]:
        """
        Fetch and parse a webpage.
        
        Args:
            url: URL to fetch
        
        Returns:
            Dict with title, content, text, and metadata
        """
        try:
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.title.string if soup.title else url
            
            # Extract main content
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text
            text = soup.get_text(separator='\n', strip=True)
            
            # Clean up text
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            clean_text = '\n'.join(lines)
            
            # Get main article content if available
            article = soup.find('article') or soup.find('main') or soup.find('div', class_='content')
            article_text = article.get_text(separator='\n', strip=True) if article else clean_text
            
            return {
                'url': url,
                'title': title,
                'content': response.text,
                'text': clean_text,
                'article_text': article_text,
                'fetched_at': time.time()
            }
            
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
        except Exception as e:
            print(f"Error parsing {url}: {e}")
            return None
    
    def search_duckduckgo(self, query: str, num_results: int = 5) -> list:
        """
        Search using DuckDuckGo (no API key needed).
        
        Args:
            query: Search query
            num_results: Number of results to return
        
        Returns:
            List of result dicts with title, url, snippet
        """
        try:
            # DuckDuckGo HTML search
            search_url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
            response = self.session.get(search_url, timeout=self.timeout)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            for result in soup.select('.result')[:num_results]:
                title_elem = result.select_one('.result__title')
                snippet_elem = result.select_one('.result__snippet')
                url_elem = result.select_one('.result__url')
                
                if title_elem and url_elem:
                    results.append({
                        'title': title_elem.get_text(strip=True),
                        'url': url_elem.get_text(strip=True),
                        'snippet': snippet_elem.get_text(strip=True) if snippet_elem else ''
                    })
            
            return results
            
        except Exception as e:
            print(f"Search error: {e}")
            return []
