"""Country/sector composite risk: composite = jurisdiction base score x sector multiplier.

Numeric band from the exact (unrounded) composite; final label adds the high-risk override
(forces high_risk) and the EDD flag (forces at least medium_risk).
"""
import re
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.kyc.country_sector_risk.intermediate.v1"


def _flag(name: str, text: str) -> bool:
    m = re.search(name + r"\s+is\s+(true|false)\b", text, flags=re.I)
    if m is None:
        raise ValueError(f"flag not found: {name}")
    return m.group(1).lower() == "true"


def solve(text: str, q: dict) -> dict:
    base = grab(r"jurisdiction base score is {N}", text)
    mult = grab(r"sector multiplier is {N}", text)
    override = _flag(r"high-risk override", text)
    edd = _flag(r"EDD flag", text)
    try:
        hi = grab(r"high_risk at an exact composite of at least {N}", text)
    except ValueError:
        hi = Fraction(8)
    try:
        med = grab(r"medium_risk at an exact composite of at least {N}", text)
    except ValueError:
        med = Fraction(5)

    composite = base * mult
    if composite >= hi:
        band = "high_risk"
    elif composite >= med:
        band = "medium_risk"
    else:
        band = "standard_risk"

    if composite >= hi or override:
        final = "high_risk"
    elif composite >= med or edd:
        final = "medium_risk"
    else:
        final = "standard_risk"

    return {"final": final, "slots": {"composite_risk_score": composite, "numeric_risk_band": band}}
