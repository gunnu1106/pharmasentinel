import json
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple

DATA_DIR = Path(__file__).parent.parent / "data"

with open(DATA_DIR / "adr_terms.json") as f:
    ADR_TERMS = json.load(f)

SYMPTOM_KEYWORDS = ADR_TERMS["symptom_keywords"]
FIRST_PERSON = ADR_TERMS["first_person_indicators"]
NEGATIONS = ADR_TERMS["negation_words"]
NOISE_PHRASES = ADR_TERMS["noise_phrases"]
CONFIDENCE_BOOSTERS = ADR_TERMS["confidence_boosters"]

ALL_SYMPTOMS = {
    symptom: category
    for category, symptoms in SYMPTOM_KEYWORDS.items()
    for symptom in symptoms
}


def is_first_person_report(text: str) -> bool:
    text_lower = text.lower()
    score = sum(1 for indicator in FIRST_PERSON if indicator in text_lower)
    noise_score = sum(1 for phrase in NOISE_PHRASES if phrase in text_lower)
    return score >= 2 and noise_score < 2


def has_negation(text: str, symptom: str) -> bool:
    text_lower = text.lower()
    idx = text_lower.find(symptom)
    if idx == -1:
        return False
    context = text_lower[max(0, idx - 60):idx]
    return any(neg in context for neg in NEGATIONS)


def extract_adrs(text: str) -> List[Dict]:
    text_lower = text.lower()
    found_adrs = []
    seen = set()

    for symptom, category in ALL_SYMPTOMS.items():
        if symptom in text_lower and symptom not in seen:
            if not has_negation(text, symptom):
                found_adrs.append({
                    "term": symptom,
                    "category": category,
                    "normalized": symptom.replace(" ", "_")
                })
                seen.add(symptom)

    return found_adrs


def compute_confidence(text: str, adrs: List[Dict], is_first_person: bool) -> float:
    if not adrs:
        return 0.0

    score = 0.3 if is_first_person else 0.1
    score += min(len(adrs) * 0.1, 0.3)

    text_lower = text.lower()
    boost = sum(1 for b in CONFIDENCE_BOOSTERS if b in text_lower)
    score += min(boost * 0.1, 0.2)

    word_count = len(text.split())
    if word_count > 50:
        score += 0.1
    if word_count > 150:
        score += 0.1

    return min(round(score, 2), 1.0)


PII_PATTERNS = [
    (r'\b[A-Z][a-z]+\s[A-Z][a-z]+\b', '[NAME]'),
    (r'\b\d{10}\b', '[PHONE]'),
    (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),
    (r'\b\d{1,3}\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Lane|Ln)\b', '[ADDRESS]'),
    (r'\bu/[A-Za-z0-9_-]+\b', '[USER]'),
    (r'\b@[A-Za-z0-9_]+\b', '[USER]'),
]


def anonymize_pii(text: str) -> Tuple[str, bool]:
    pii_found = False
    for pattern, replacement in PII_PATTERNS:
        new_text = re.sub(pattern, replacement, text)
        if new_text != text:
            pii_found = True
            text = new_text
    return text, pii_found


def hash_author(username: str) -> str:
    return hashlib.sha256(username.encode()).hexdigest()[:16]


def process_post(text: str, author: str = "") -> Dict:
    anonymized, pii_found = anonymize_pii(text)
    first_person = is_first_person_report(text)
    adrs = extract_adrs(text)
    confidence = compute_confidence(text, adrs, first_person)

    return {
        "anonymized_content": anonymized,
        "author_hash": hash_author(author) if author else "",
        "is_first_person": first_person,
        "extracted_adrs": adrs,
        "confidence_score": confidence,
        "pii_detected": pii_found,
    }
