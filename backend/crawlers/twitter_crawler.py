"""
Twitter/X crawler using twitterapi.io
Docs: https://twitterapi.io/docs
Falls back to mock data if API key not configured.
"""
import httpx
from datetime import datetime
from typing import List, Dict

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import TWITTER_API_KEY

TWITTER_AVAILABLE = bool(TWITTER_API_KEY)

TWITTERAPI_BASE = "https://api.twitterapi.io/twitter"
HEADERS = {"X-API-Key": TWITTER_API_KEY}

HEALTH_QUERY_SUFFIXES = [
    "side effect",
    "adverse reaction",
    "bad reaction",
    "taking medication",
    "prescribed",
]


def search_twitter(drug_name: str, limit: int = 20) -> List[Dict]:
    if not TWITTER_AVAILABLE:
        from crawlers.mock_generator import get_mock_posts
        return [p for p in get_mock_posts(drug_name, limit) if p.get("source") == "twitter"]

    posts = []
    for suffix in HEALTH_QUERY_SUFFIXES:
        query = f"{drug_name} {suffix} -is:retweet lang:en"
        try:
            resp = httpx.get(
                f"{TWITTERAPI_BASE}/tweet/search",
                headers=HEADERS,
                params={"query": query, "maxResults": 10},
                timeout=10,
            )
            if resp.status_code != 200:
                continue

            data = resp.json()
            for tweet in data.get("tweets", []):
                posts.append(_parse_tweet(tweet))

            if len(posts) >= limit:
                break
        except Exception:
            continue

    if not posts:
        from crawlers.mock_generator import get_mock_posts
        return [p for p in get_mock_posts(drug_name, limit) if p.get("source") == "twitter"]

    return posts[:limit]


def get_tweet_by_id(tweet_id: str) -> Dict:
    try:
        resp = httpx.get(
            f"{TWITTERAPI_BASE}/tweets",
            headers=HEADERS,
            params={"tweet_ids": tweet_id},
            timeout=10,
        )
        data = resp.json()
        tweets = data.get("tweets", [])
        return _parse_tweet(tweets[0]) if tweets else {}
    except Exception:
        return {}


def _parse_tweet(tweet: Dict) -> Dict:
    author = tweet.get("author", {})
    return {
        "id": f"twitter_{tweet.get('id', '')}",
        "source": "twitter",
        "subreddit": None,
        "author": author.get("userName", "anonymous"),
        "content": tweet.get("text", ""),
        "url": f"https://twitter.com/{author.get('userName', '')}/status/{tweet.get('id', '')}",
        "posted_at": tweet.get("createdAt", datetime.utcnow().isoformat()),
        "location": author.get("location"),
        "upvotes": tweet.get("likeCount", 0),
    }
