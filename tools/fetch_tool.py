"""fetch_tool.py


Fetch and extract article content using trafilatura with a
requests+BS4 fallback. Returns a dict with title and text.
"""


from typing import Dict
import trafilatura
import requests
from bs4 import BeautifulSoup
import logging
import re
import json


logger = logging.getLogger(__name__)


def fetch_article_content(url: str) -> Dict:
    """
    Downloads and extracts the main text and title from a URL.

    It first tries the high-quality parser `trafilatura`. If that fails,
    it uses a robust fallback method with `requests` and `BeautifulSoup`.

    Returns a dictionary:
    {
        "title": str,
        "text": str,
        "url": str
    }
    """
    if not url:
        logger.error("URL must be provided.")
        raise ValueError("URL must be provided")

    # --- Method 1: Trafilatura (Primary) ---
    try:
        logger.info(f"Attempting extraction with Trafilatura for: {url}")
        downloaded_html = trafilatura.fetch_url(url)
        
        if downloaded_html:
            # Get the output as a JSON string
            extracted_json_string = trafilatura.extract(
                downloaded_html,
                output_format='json',
                include_comments=False,
                include_tables=False,
                favor_precision=True
            )
            if extracted_json_string:
                data = json.loads(extracted_json_string)
                # If we get text, we're done. Return it.
                if data and data.get('text') and data['text'].strip():
                    logger.info(f"Trafilatura SUCCESS for: {url}")
                    return {
                        "title": (data.get('title') or url).strip(),
                        "text": data['text'].strip(),
                        "url": url
                    }
        logger.warning(f"Trafilatura failed to extract meaningful content from: {url}")
    except Exception as e:
        logger.warning(f"Trafilatura process failed for {url}: {e}")

    # --- Method 2: Requests + BeautifulSoup (Fallback) ---
    try:
        logger.info(f"Attempting fallback with Requests/BS4 for: {url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        r = requests.get(url, timeout=15, headers=headers)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")
        
        title_tag = soup.find("title")
        title = title_tag.get_text().strip() if title_tag else url

        # Find the main content container
        potential_containers = [
            soup.find("main"), soup.find("article"), soup.find(id="content"),
            soup.find(id="main-content"), soup.find(class_="post-content"),
            soup.find(class_="article-body"),
        ]
        content_container = next((c for c in potential_containers if c is not None), soup.body)
        
        # Extract text ONLY from within the container
        text_elements = content_container.find_all(["p", "h1", "h2", "h3", "li"])   # type: ignore
        text_blocks = [el.get_text(separator=" ", strip=True) for el in text_elements]
        
        full_text = "\n\n".join(block for block in text_blocks if block)
        cleaned_text = re.sub(r'\n{3,}', '\n\n', full_text).strip()

        if cleaned_text:
            logger.info(f"Requests/BS4 fallback SUCCESS for: {url}")
            return {"title": title, "text": cleaned_text, "url": url}
    except Exception as e:
        logger.error(f"Requests/BS4 fallback also failed for {url}: {e}")

    # --- Final Fallback: Return placeholders ---
    logger.warning(f"All extraction methods failed for: {url}. Returning placeholders.")
    return {"title": url, "text": "", "url": url}


if __name__ == "__main__":
    import dotenv, json
    dotenv.load_dotenv()
    test_url = "https://www.tomsguide.com/computing/vpns/arizona-sees-spike-in-demand-for-vpns-following-the-introduction-of-age-verification-laws"
    print(json.dumps(fetch_article_content(test_url), indent=2))