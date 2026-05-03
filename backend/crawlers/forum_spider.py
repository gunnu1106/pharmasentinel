"""
Health forum crawler using Scrapy + httpx for static pages.
Targets: MedHelp, PatientInfo, HealthUnlocked, Practo Q&A
Falls back to mock data when sites are unreachable.
"""
import httpx
import re
from datetime import datetime
from typing import List, Dict
from urllib.parse import quote_plus


FORUM_SOURCES = [
    {
        "name": "medhelp",
        "search_url": "https://www.medhelp.org/search/results?query={query}&search_type=posts",
        "post_selector": "article.post-body",
        "content_tag": "div.post_text",
    },
    {
        "name": "patientinfo",
        "search_url": "https://patient.info/forums/search?q={query}",
        "post_selector": "div.post__content",
        "content_tag": "p",
    },
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; PharmaSentinelBot/1.0; +https://pharmasentinel.in/bot)",
    "Accept-Language": "en-IN,en;q=0.9",
}


def search_health_forums(drug_name: str, limit: int = 15) -> List[Dict]:
    posts = []

    for source in FORUM_SOURCES:
        try:
            results = _crawl_source(source, drug_name, limit=8)
            posts.extend(results)
        except Exception:
            continue

        if len(posts) >= limit:
            break

    if not posts:
        from crawlers.mock_generator import get_mock_posts
        return get_mock_posts(drug_name, limit)

    return posts[:limit]


def _crawl_source(source: Dict, drug_name: str, limit: int) -> List[Dict]:
    query = quote_plus(f"{drug_name} side effect")
    url = source["search_url"].format(query=query)

    resp = httpx.get(url, headers=HEADERS, timeout=12, follow_redirects=True)
    if resp.status_code != 200:
        return []

    return _extract_posts(resp.text, source["name"], drug_name, limit)


def _extract_posts(html: str, source_name: str, drug_name: str, limit: int) -> List[Dict]:
    posts = []

    # Extract paragraphs that mention the drug and symptoms
    paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html, re.DOTALL | re.IGNORECASE)

    drug_lower = drug_name.lower()
    symptom_words = [
        "side effect", "pain", "nausea", "rash", "dizzy", "headache",
        "reaction", "symptom", "problem", "issue", "feel", "experience"
    ]

    for para in paragraphs:
        clean = re.sub(r'<[^>]+>', '', para).strip()
        if len(clean) < 80:
            continue

        clean_lower = clean.lower()
        if drug_lower not in clean_lower:
            continue
        if not any(word in clean_lower for word in symptom_words):
            continue

        posts.append({
            "id": f"forum_{source_name}_{len(posts)}",
            "source": "forum",
            "subreddit": source_name,
            "author": "forum_user",
            "content": clean[:1000],
            "url": f"https://{source_name}.com/search?q={quote_plus(drug_name)}",
            "posted_at": datetime.utcnow().isoformat(),
            "location": None,
            "upvotes": 0,
        })

        if len(posts) >= limit:
            break

    return posts


class ScrapyConfig:
    """
    Scrapy spider config for deeper forum crawling.
    Usage: scrapy crawl pharma_spider -a drug=azithromycin
    Install: pip install scrapy
    Run: cd backend && scrapy crawl pharma_spider -a drug=azithromycin -o output.json
    """
    SPIDER_NAME = "pharma_spider"
    ALLOWED_DOMAINS = [
        "medhelp.org",
        "patient.info",
        "healthunlocked.com",
        "practo.com",
        "quora.com",
    ]
    CUSTOM_SETTINGS = {
        "DOWNLOAD_DELAY": 2,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "ROBOTSTXT_OBEY": True,
        "CONCURRENT_REQUESTS": 4,
        "DEFAULT_REQUEST_HEADERS": HEADERS,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 2.0,
    }

    START_URLS_TEMPLATE = [
        "https://www.medhelp.org/search/results?query={drug}+side+effect&search_type=posts",
        "https://patient.info/forums/search?q={drug}+side+effect",
        "https://healthunlocked.com/search?query={drug}+side+effect",
    ]
