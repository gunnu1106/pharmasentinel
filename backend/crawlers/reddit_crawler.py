"""
Reddit crawler using PRAW. Falls back to mock data if credentials are not configured.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime
from typing import List, Dict
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT

REDDIT_AVAILABLE = bool(REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET)

if REDDIT_AVAILABLE:
    try:
        import praw
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT,
        )
        REDDIT_AVAILABLE = True
    except Exception:
        REDDIT_AVAILABLE = False

SUBREDDITS = [
    "AskDocs", "pharmacy", "india", "medical", "diabetes_t2",
    "ChronicPain", "druginteractions", "pharmacology", "IndianHealthcare"
]


def search_reddit(drug_name: str, limit: int = 25) -> List[Dict]:
    if not REDDIT_AVAILABLE:
        from crawlers.mock_generator import get_mock_posts
        return get_mock_posts(drug_name, limit)

    posts = []
    queries = [
        f"{drug_name} side effect",
        f"{drug_name} adverse reaction",
        f"{drug_name} symptoms",
        f"{drug_name} experience",
    ]

    seen_ids = set()
    for subreddit_name in SUBREDDITS[:4]:
        for query in queries[:2]:
            try:
                subreddit = reddit.subreddit(subreddit_name)
                for submission in subreddit.search(query, limit=5, time_filter="month"):
                    if submission.id in seen_ids:
                        continue
                    seen_ids.add(submission.id)

                    content = submission.selftext or submission.title
                    if len(content) < 30:
                        continue

                    posts.append({
                        "id": f"reddit_{submission.id}",
                        "source": "reddit",
                        "subreddit": f"r/{subreddit_name}",
                        "author": str(submission.author) if submission.author else "deleted",
                        "content": f"{submission.title}\n\n{content}",
                        "url": f"https://reddit.com{submission.permalink}",
                        "posted_at": datetime.fromtimestamp(submission.created_utc).isoformat(),
                        "location": None,
                        "upvotes": submission.score
                    })

                    if len(posts) >= limit:
                        return posts
            except Exception:
                continue

    if len(posts) < 3:
        from crawlers.mock_generator import get_mock_posts
        mock = get_mock_posts(drug_name, limit - len(posts))
        posts.extend(mock)

    return posts[:limit]
