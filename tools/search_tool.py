"""search_tool.py


Fetch simple trending topics using SerpAPI (if available)
or DuckDuckGo search as a fallback. Also attempts to query
Reddit's r/popular if reddit credentials are present.


Function:
get_trending_topics(query: str, limit: int) -> list[dict]


Each dict: {"title": str, "url": str, "source": str}
"""


from typing import List, Dict, Optional
import os
import logging
import random

logger = logging.getLogger(__name__)

try:
    from serpapi import GoogleSearch
    google_search = GoogleSearch
    SERPAPI_AVAILABLE = True
except Exception:
    logger.warning("SerpAPI is not available.")
    SERPAPI_AVAILABLE = False


try:
    from ddgs import DDGS
    ddg = DDGS
    DUCKDUCKGO_AVAILABLE = True
except Exception:
    logger.warning("DuckDuckGo search is not available.")
    DUCKDUCKGO_AVAILABLE = False


# Optional reddit
try:
    import praw
    praw = praw
    REDDIT_AVAILABLE = True
except Exception:
    logger.warning("Reddit lookup is not available.")
    REDDIT_AVAILABLE = False


def _search_serpapi(query: str, limit: int) -> List[Dict]:
    api_key = os.getenv("SERPAPI_API_KEY")
    if not SERPAPI_AVAILABLE or not api_key:
        logger.warning("SerpAPI search is not available.")
        return []
    params = {
    "engine": "google",
    "q": query,
    "api_key": api_key,
    "num": limit,
    }
    try:
        s = google_search(params)
        r = s.get_dict()
        results = r.get("organic_results", [])
        out = []
        for item in results[:limit]:
            title = item.get("title")
            link = item.get("link") or item.get("url")
            if title and link:
                out.append({"title": title, "url": link, "source": "[web] SerpAPI search"})
        return out
    except Exception as e:
        logger.warning("SerpAPI search failed: %s", e)
        return []

def _search_duckduckgo(query: str, limit: int) -> List[Dict]:
    if not DUCKDUCKGO_AVAILABLE or ddg is None:
        logger.warning("DuckDuckGo search is not available.")
        return []
    try:
        results = ddg().text(query, max_results=limit)
        out = []
        for r in results or []:
            title = r.get("title")
            link = r.get("href")
            if title and link:
                out.append({"title": title, "url": link, "source": "[web] DuckDuckGo search"})
        return out
    except Exception as e:
        logger.warning("DuckDuckGo search failed: %s", e)
        return []
    
def _search_reddit(limit: int) -> List[Dict]:
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT", "linkedin_auto_mvp")
    if not REDDIT_AVAILABLE or not client_id or not client_secret:
        return []
    out = []
    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        subreddits = ("technews", "tech")
        selected_subr = random.choice(subreddits)
        for submission in reddit.subreddit(selected_subr).hot(limit=limit):
            title = submission.title
            url = submission.url
            out.append({"title": title, "url": url, "source": "reddit"})
        return out
    except Exception as e:
        logger.warning("Reddit lookup failed: %s", e)
        return out
    
def get_trending_topics(query: Optional[str] = None, web_limit: int = 5, reddit_limit: int = 5) -> List[Dict]:
    """Return a list of trending topics as dicts {title, url, source}.


    Priority: SerpAPI -> DuckDuckGo -> Reddit (as an add-on)
    """
    query = query or os.getenv("DEFAULT_SEARCH_QUERY", "latest tech news")

    # Reddit search
    topics = _search_reddit(reddit_limit+1)
    topics = topics[1:]

    # Set the first result from redis as the search query for Serp
    search_query = topics[0]["title"]

    # SerpAPI 
    serp_results = _search_serpapi(search_query, web_limit)
    # merge without duplicates (by url)
    existing_urls = {t["url"] for t in topics}
    existing_titles = {t["title"] for t in topics}
    for r in serp_results:
        if r["url"] not in existing_urls and r["title"] not in existing_titles:
                topics.append(r)
                existing_urls.add(r["url"])
                existing_titles.add(r["title"])

    serp_results = []

    # Fallback to DuckDuckGo if serp did not work
    if not serp_results:
        ddg_results = _search_duckduckgo(search_query, web_limit)
        # merge without duplicates (by title and url)
        existing_urls = {t["url"] for t in topics}
        existing_titles = {t["title"] for t in topics}
        for r in ddg_results:
            if r["url"] not in existing_urls and r["title"] not in existing_titles:
                topics.append(r)
                existing_urls.add(r["url"])
                existing_titles.add(r["title"])

    return topics


if __name__ == "__main__":
    import dotenv
    dotenv.load_dotenv()
    import json
    topics = get_trending_topics(web_limit=3, reddit_limit=2)
    print(json.dumps(topics, indent=2))