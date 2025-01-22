import httpx
from bs4 import BeautifulSoup
import re
from typing import List, Tuple, Iterator
from concurrent.futures import ThreadPoolExecutor
import itertools
import time
import json
from datetime import datetime
from pathlib import Path

class PresidentialActionsScraper:
    def __init__(self, base_url: str = "https://www.whitehouse.gov/presidential-actions/"):
        self.base_url = base_url
        self.session = httpx.Client(follow_redirects=True)
        self.last_request_time = 0
        self.min_request_delay = 1  # minimum seconds between requests
        
    def _respectful_request(self, url: str) -> str:
        """Make a request with controlled timing."""
        # Ensure minimum delay between requests
        time_since_last = time.time() - self.last_request_time
        if time_since_last < self.min_request_delay:
            time.sleep(self.min_request_delay - time_since_last)
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            self.last_request_time = time.time()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return ""

    def get_total_pages(self) -> int:
        """Extract the total number of pages from the pagination section."""
        html_content = self._respectful_request(self.base_url)
        soup = BeautifulSoup(html_content, 'lxml')
        
        page_numbers = []
        for link in soup.find_all('a'):
            href = link.get('href', '')
            if 'presidential-actions/page/' in href:
                try:
                    page_num = int(href.split('page/')[-1].rstrip('/'))
                    page_numbers.append(page_num)
                except ValueError:
                    continue
        
        return max(page_numbers) if page_numbers else 1

    def generate_page_urls(self, total_pages: int) -> Iterator[str]:
        """Generate URLs for all pages."""
        return (
            f"{self.base_url}page/{page}/" if page > 1 else self.base_url
            for page in range(1, total_pages + 1)
        )

    def get_action_content(self, url: str) -> Tuple[str, str]:
        """Fetch and return the title and clean content of a presidential action."""
        html_content = self._respectful_request(url)
        if not html_content:
            return "", ""
        
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Get title from h1 tag if available, otherwise from URL
        title_tag = soup.find('h1')
        title = title_tag.text.strip() if title_tag else url.split('/')[-1].replace('-', ' ').title()
        
        # Get all paragraphs from the main content
        paragraphs = soup.find_all('p')
        content = '\n\n'.join(p.get_text().strip() for p in paragraphs if p.get_text().strip())
        
        return title, content

    def collect_page_actions(self, page_url: str) -> List[Tuple[str, str]]:
        """Collect all presidential actions from a single page."""
        html_content = self._respectful_request(page_url)
        if not html_content:
            return []
        
        # Extract action URLs from the page
        action_urls = re.findall(
            r'https://www\.whitehouse\.gov/presidential-actions/\d{4}/\d{2}/[^/]+',
            html_content
        )
        
        actions = []
        for url in action_urls:
            try:
                title, content = self.get_action_content(url)
                if title and content:
                    actions.append((title, content))
                    print(f"Collected: {title}")
            except Exception as e:
                print(f"Error collecting {url}: {e}")
        
        return actions

    def collect_all_actions(self) -> List[Tuple[str, str]]:
        """Collect actions from all pages."""
        total_pages = self.get_total_pages()
        print(f"Found {total_pages} pages to process")
        
        all_actions = []
        for page_url in self.generate_page_urls(total_pages):
            actions = self.collect_page_actions(page_url)
            all_actions.extend(actions)
            
        return all_actions

def save_actions(actions: List[Tuple[str, str]], output_dir: str = "presidential_actions"):
    """Save the collected actions to files."""
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Save individual actions
    for title, content in actions:
        # Create a safe filename from the title
        safe_title = re.sub(r'[^\w\s-]', '', title)
        safe_title = re.sub(r'[-\s]+', '-', safe_title).strip('-').lower()
        
        # Save as JSON with metadata
        action_data = {
            "title": title,
            "content": content,
            "collected_at": datetime.now().isoformat()
        }
        
        file_path = output_path / f"{safe_title}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(action_data, f, ensure_ascii=False, indent=2)
    
    # Save index file
    index_data = {
        "total_actions": len(actions),
        "titles": [title for title, _ in actions],
        "collected_at": datetime.now().isoformat()
    }
    
    with open(output_path / "index.json", 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

def main():
    # Initialize scraper
    scraper = PresidentialActionsScraper()
    
    # Collect all actions
    print("Starting collection of presidential actions...")
    actions = scraper.collect_all_actions()
    
    # Print summary
    print(f"\nCollected {len(actions)} total actions")
    
    # Save to files
    print("\nSaving actions to files...")
    save_actions(actions)
    print("Done! Check the 'presidential_actions' directory for the results.")

if __name__ == "__main__":
    main()