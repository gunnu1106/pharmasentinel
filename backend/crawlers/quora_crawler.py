"""
Quora crawler for drug-related health questions.
Uses httpx to fetch public Quora search results.
Note: Quora requires login for full access — this targets public search pages only.
"""
import httpx
import re
from datetime import datetime
from typing import List, Dict
from urllib.parse import quote_plus

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}

QUORA_SEARCH = "https://www.quora.com/search?q={query}&type=question"

SYMPTOM_TERMS = [
    "side effect", "adverse", "reaction", "caused", "experience",
    "symptom", "pain", "rash", "nausea", "dizzy", "problem",
]


def search_quora(drug_name: str, limit: int = 10) -> List[Dict]:
    query = quote_plus(f"{drug_name} side effects experience")
    url = QUORA_SEARCH.format(query=query)

    try:
        resp = httpx.get(url, headers=HEADERS, timeout=12, follow_redirects=True)
        if resp.status_code != 200:
            return []
        return _parse_quora_results(resp.text, drug_name, limit)
    except Exception:
        return []


def _parse_quora_results(html: str, drug_name: str, limit: int) -> List[Dict]:
    posts = []

    # Extract question titles and snippets from Quora search results
    titles = re.findall(
        r'<span[^>]*class="[^"]*qu-bold[^"]*"[^>]*>(.*?)</span>',
        html, re.DOTALL | re.IGNORECASE
    )
    snippets = re.findall(
        r'<span[^>]*class="[^"]*q-text[^"]*"[^>]*>(.*?)</span>',
        html, re.DOTALL | re.IGNORECASE
    )

    drug_lower = drug_name.lower()

    for i, title in enumerate(titles[:limit]):
        clean_title = re.sub(r'<[^>]+>', '', title).strip()
        clean_snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip() if i < len(snippets) else ""

        content = f"{clean_title}. {clean_snippet}".strip()
        if len(content) < 30:
            continue
        if drug_lower not in content.lower():
            continue
        if not any(term in content.lower() for term in SYMPTOM_TERMS):
            continue

        posts.append({
            "id": f"quora_{i}_{drug_name}",
            "source": "quora",
            "subreddit": "Quora",
            "author": "quora_user",
            "content": content,
            "url": f"https://www.quora.com/search?q={quote_plus(drug_name + ' side effects')}",
            "posted_at": datetime.utcnow().isoformat(),
            "location": None,
            "upvotes": 0,
        })

    return posts


def build_quora_query(drug_name: str, adr_term: str = "") -> str:
    if adr_term:
        return f"{drug_name} {adr_term} experience side effect"
    return f"What are the side effects of {drug_name}"
