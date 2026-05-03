"""
Proportional Reporting Ratio (PRR) calculator.
PRR = (n_drug_adr / n_drug_total) / (n_other_adr / n_other_total)
PRR > 2.0 with >= 3 reports is considered a safety signal.
"""
import math
from typing import Dict, List


# Baseline ADR rates (approximate background rates per 1000 drug reports)
# These would normally come from a large pharmacovigilance database (e.g. VigiBase)
BACKGROUND_ADR_RATES = {
    "nausea": 85.0,
    "vomiting": 62.0,
    "diarrhea": 71.0,
    "headache": 55.0,
    "dizziness": 48.0,
    "rash": 32.0,
    "stomach pain": 41.0,
    "abdominal pain": 41.0,
    "fatigue": 39.0,
    "insomnia": 28.0,
    "muscle pain": 18.0,
    "myalgia": 18.0,
    "joint pain": 15.0,
    "tinnitus": 4.2,
    "ringing in ears": 4.2,
    "hearing loss": 2.1,
    "muscle weakness": 6.5,
    "hallucination": 1.8,
    "confusion": 12.0,
    "liver damage": 3.5,
    "jaundice": 2.8,
    "anaphylaxis": 0.8,
    "depression": 14.0,
    "anxiety": 18.0,
    "memory loss": 5.2,
    "seizure": 2.1,
    "vision changes": 7.8,
    "blurred vision": 7.8,
    "kidney damage": 3.1,
    "tendon pain": 2.5,
    "blood clot": 4.0,
    "photosensitivity": 8.5,
    "hair loss": 12.0,
    "weight gain": 22.0,
    "breathing difficulty": 9.5,
    "chest pain": 11.0,
    "palpitations": 14.0,
    "peripheral neuropathy": 5.8,
    "numbness": 9.2,
    "tingling": 9.2,
    "brain fog": 7.5,
}

DEFAULT_BACKGROUND_RATE = 10.0  # per 1000 reports


def get_background_rate(adr_term: str) -> float:
    adr_lower = adr_term.lower()
    if adr_lower in BACKGROUND_ADR_RATES:
        return BACKGROUND_ADR_RATES[adr_lower]
    for key, rate in BACKGROUND_ADR_RATES.items():
        if key in adr_lower or adr_lower in key:
            return rate
    return DEFAULT_BACKGROUND_RATE


def calculate_prr(
    drug_adr_count: int,
    drug_total_reports: int,
    background_rate_per_1000: float = None,
    adr_term: str = None
) -> Dict:
    if background_rate_per_1000 is None and adr_term:
        background_rate_per_1000 = get_background_rate(adr_term)
    elif background_rate_per_1000 is None:
        background_rate_per_1000 = DEFAULT_BACKGROUND_RATE

    # Estimated background counts (simulate large reference database of 10000 reports)
    ref_total = 10000
    ref_adr_count = (background_rate_per_1000 / 1000) * ref_total

    # Avoid division by zero
    if drug_total_reports == 0 or ref_adr_count == 0:
        return {"prr": 0.0, "chi_squared": 0.0, "is_signal": False, "interpretation": "Insufficient data"}

    a = drug_adr_count
    b = drug_total_reports - drug_adr_count
    c = ref_adr_count
    d = ref_total - ref_adr_count

    if b <= 0 or d <= 0:
        return {"prr": 0.0, "chi_squared": 0.0, "is_signal": False, "interpretation": "Insufficient data"}

    prr = (a / (a + b)) / (c / (c + d))

    # Chi-squared with Yates correction
    n = a + b + c + d
    try:
        chi_sq = (n * (abs(a * d - b * c) - n / 2) ** 2) / ((a + b) * (c + d) * (a + c) * (b + d))
    except ZeroDivisionError:
        chi_sq = 0.0

    # Signal criteria: PRR >= 2, chi-squared >= 4, n >= 3
    is_signal = prr >= 2.0 and chi_sq >= 4.0 and drug_adr_count >= 3

    if prr >= 5.0:
        interpretation = "Strong safety signal — immediate review recommended"
    elif prr >= 2.0:
        interpretation = "Potential safety signal — warrants further evaluation"
    elif prr >= 1.5:
        interpretation = "Weak signal — monitor closely"
    else:
        interpretation = "No signal detected"

    return {
        "prr": round(prr, 3),
        "chi_squared": round(chi_sq, 3),
        "is_signal": is_signal,
        "interpretation": interpretation,
        "drug_adr_count": drug_adr_count,
        "drug_total_reports": drug_total_reports,
        "background_rate_per_1000": background_rate_per_1000,
    }


def calculate_growth_rate(timeline: List[Dict]) -> float:
    """Calculate week-over-week growth rate of reports."""
    if len(timeline) < 2:
        return 0.0

    recent = timeline[-1].get("count", 0)
    previous = timeline[-2].get("count", 1)

    if previous == 0:
        return 100.0

    return round(((recent - previous) / previous) * 100, 1)
