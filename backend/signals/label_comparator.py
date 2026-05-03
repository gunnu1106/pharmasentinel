import json
from pathlib import Path
from typing import List, Dict, Tuple

DATA_DIR = Path(__file__).parent.parent / "data"

with open(DATA_DIR / "cdsco_labels.json") as f:
    CDSCO_LABELS = json.load(f)


def get_drug_label(drug_name: str) -> Dict:
    key = drug_name.lower().strip()
    return CDSCO_LABELS.get(key, {})


def is_adr_on_label(drug_name: str, adr_term: str) -> Tuple[bool, float]:
    label = get_drug_label(drug_name)
    if not label:
        return False, 0.5

    known_effects = [e.lower() for e in label.get("known_side_effects", [])]
    adr_lower = adr_term.lower()

    # Exact match
    if adr_lower in known_effects:
        return True, 1.0

    # Partial match
    for effect in known_effects:
        if adr_lower in effect or effect in adr_lower:
            return True, 0.8

    # Word-level overlap
    adr_words = set(adr_lower.split())
    for effect in known_effects:
        effect_words = set(effect.split())
        overlap = adr_words & effect_words
        if overlap and len(overlap) / max(len(adr_words), 1) >= 0.5:
            return True, 0.6

    return False, 0.0


def compare_signal_to_label(drug_name: str, adr_term: str, report_count: int) -> Dict:
    on_label, match_confidence = is_adr_on_label(drug_name, adr_term)
    label = get_drug_label(drug_name)

    if on_label:
        priority = "LOW"
        label_status = "known"
    else:
        label_status = "unlisted"
        if report_count >= 3:
            priority = "HIGH"
        elif report_count >= 2:
            priority = "MEDIUM"
        else:
            priority = "LOW"

    return {
        "is_on_label": on_label,
        "match_confidence": match_confidence,
        "label_status": label_status,
        "priority": priority,
        "drug_info": {
            "generic_name": label.get("generic_name", drug_name),
            "brand_names": label.get("brand_names", []),
            "drug_class": label.get("drug_class", ""),
            "known_side_effects": label.get("known_side_effects", []),
            "serious_warnings": label.get("serious_warnings", []),
            "cdsco_approval": label.get("cdsco_approval", ""),
        }
    }
