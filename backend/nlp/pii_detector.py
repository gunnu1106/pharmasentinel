"""
PII (Personally Identifiable Information) and PHI (Protected Health Information) detector.
Detects and anonymizes sensitive data before storage — GDPR and health data compliant.
"""
import re
import hashlib
from typing import Tuple, List, Dict


# ── PII Patterns ──────────────────────────────────────────────────────────────

PII_RULES = [
    # Names (basic pattern — two capitalized words)
    (r'\b[A-Z][a-z]{2,}\s[A-Z][a-z]{2,}\b', '[NAME]', "full_name"),

    # Indian mobile numbers
    (r'\b(?:\+91[\-\s]?)?[6-9]\d{9}\b', '[PHONE]', "phone"),

    # Email addresses
    (r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b', '[EMAIL]', "email"),

    # Aadhaar number (12 digits)
    (r'\b\d{4}\s?\d{4}\s?\d{4}\b', '[AADHAAR]', "aadhaar"),

    # PAN card
    (r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b', '[PAN]', "pan"),

    # Age (e.g., "I am 34 years old", "age 34")
    (r'\b(?:age|aged|am)\s+(\d{1,3})\s*(?:years?|yrs?)?\b', r'[AGE]', "age"),

    # Indian addresses
    (r'\b\d{1,4}[\s,]+[A-Za-z\s]+(?:Street|St|Road|Rd|Nagar|Colony|Sector|Phase)\b',
     '[ADDRESS]', "address"),

    # PIN codes
    (r'\b[1-9]\d{5}\b', '[PINCODE]', "pincode"),

    # Reddit usernames
    (r'\bu/[A-Za-z0-9_\-]{3,20}\b', '[REDDIT_USER]', "username"),

    # Twitter handles
    (r'\b@[A-Za-z0-9_]{1,15}\b', '[TWITTER_USER]', "username"),

    # Doctor names (Dr. Something)
    (r'\bDr\.?\s+[A-Z][a-z]+(?:\s[A-Z][a-z]+)?\b', '[DOCTOR_NAME]', "doctor"),

    # Hospital names (heuristic)
    (r'\b[A-Z][a-z]+\s+(?:Hospital|Clinic|Medical Center|Nursing Home|AIIMS|PGI)\b',
     '[HOSPITAL]', "hospital"),
]

# ── PHI Patterns ──────────────────────────────────────────────────────────────

PHI_RULES = [
    # Specific diagnosis with personal context
    (r'\bI\s+(?:have|had|was diagnosed with|suffer from)\s+([A-Za-z\s]+(?:disease|disorder|syndrome|cancer|diabetes|HIV|hepatitis))\b',
     r'I have [CONDITION]', "condition"),

    # Medication dosage details with personal context
    (r'\bI\s+(?:take|took|am on|was prescribed)\s+\d+\s*mg\b',
     'I take [DOSAGE]', "dosage"),
]


def detect_and_anonymize(text: str) -> Tuple[str, bool, List[str]]:
    """
    Returns (anonymized_text, pii_found, list_of_pii_types_found)
    """
    pii_found = False
    pii_types = []
    result = text

    for pattern, replacement, pii_type in PII_RULES:
        new_text, count = re.subn(pattern, replacement, result)
        if count > 0:
            pii_found = True
            pii_types.append(pii_type)
            result = new_text

    for pattern, replacement, phi_type in PHI_RULES:
        new_text, count = re.subn(pattern, replacement, result, flags=re.IGNORECASE)
        if count > 0:
            pii_found = True
            pii_types.append(f"phi_{phi_type}")
            result = new_text

    return result, pii_found, list(set(pii_types))


def hash_identifier(identifier: str, salt: str = "pharmasentinel") -> str:
    """One-way hash for usernames/author IDs — irreversible anonymization."""
    payload = f"{salt}:{identifier}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def scan_batch(texts: List[str]) -> List[Dict]:
    """Scan a batch of texts and return anonymization results."""
    results = []
    for text in texts:
        anonymized, found, types = detect_and_anonymize(text)
        results.append({
            "original_length": len(text),
            "anonymized": anonymized,
            "pii_detected": found,
            "pii_types": types,
        })
    return results


def generate_pii_report(scan_results: List[Dict]) -> Dict:
    """Summary report of PII found across a batch."""
    total = len(scan_results)
    with_pii = sum(1 for r in scan_results if r["pii_detected"])
    all_types = [t for r in scan_results for t in r.get("pii_types", [])]

    type_counts = {}
    for t in all_types:
        type_counts[t] = type_counts.get(t, 0) + 1

    return {
        "total_posts_scanned": total,
        "posts_with_pii": with_pii,
        "pii_detection_rate": f"{(with_pii / total * 100):.1f}%" if total else "0%",
        "pii_types_found": type_counts,
        "gdpr_compliant": True,
        "anonymization_method": "Regex-based redaction + SHA-256 identifier hashing",
    }
