import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

IGNORED_PATTERNS = ["login", "signup", "privacy", "terms", "cookie"]

def is_valid_url(url):
    for pattern in IGNORED_PATTERNS:
        if pattern in url.lower():
            return False
    return True

def extract_text_from_html(html):
    soup = BeautifulSoup(html, "html.parser")

    for script in soup(["script", "style", "nav", "footer"]):
        script.extract()

    return soup.get_text(separator=" ", strip=True)

def crawl_website(seed_url, max_pages=10):
    """Breadth-first crawl of a site, collecting text from each page.

    URLs are normalized (stripping query strings and fragments) so that
    the same page isn't crawled multiple times simply because the link
    contains a tracking parameter or an anchor.
    """

    def normalize(url):
        """Return a canonical form of the URL for deduplication."""
        parsed = urlparse(url)
        # keep scheme, netloc and path only
        return parsed.scheme + "://" + parsed.netloc + parsed.path.rstrip("/")

    visited = set()
    to_visit = [seed_url]
    documents = []

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        norm = normalize(url)

        if norm in visited or not is_valid_url(url):
            continue

        try:
            response = requests.get(
                url,
                timeout=10,
                headers={"User-Agent": "DocumentationAnalyzerBot/1.0"}
            )
            response.raise_for_status()
            visited.add(norm)

            text = extract_text_from_html(response.text)

            documents.append({
                "url": url,
                "content": text
            })

            soup = BeautifulSoup(response.text, "html.parser")

            for link in soup.find_all("a", href=True):
                full_url = urljoin(url, link["href"])
                if urlparse(full_url).netloc == urlparse(seed_url).netloc:
                    to_visit.append(full_url)

        except Exception as e:
            print(f"Failed to crawl {url}: {e}")

    return documents
