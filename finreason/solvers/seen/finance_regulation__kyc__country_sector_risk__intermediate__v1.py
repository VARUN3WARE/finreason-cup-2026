import re
from fractions import Fraction

from finreason.nums import NUMBER, grab

TEMPLATE_ID = "fp.finance_regulation.kyc.country_sector_risk.intermediate.v1"


def _bool(pattern: str, text: str) -> bool:
    m = re.search(pattern + r"\s+(true|false)\b", text, flags=re.I)
    if m is None:
        raise ValueError(f"flag not found: {pattern!r}")
    return m.group(1).lower() == "true"


def _threshold(label: str, text: str, default: Fraction) -> tuple[Fraction, bool]:
    """Lower bound of a band: (value, inclusive). 'at least' -> inclusive, 'above' -> strict."""
    m = re.search(
        rf"{label} at an exact composite of (at least|above|greater than|more than) ({NUMBER})",
        text,
    )
    if m is None:
        return default, True
    return Fraction(m.group(2).replace(",", "")), m.group(1) == "at least"


def _meets(x: Fraction, bound: tuple[Fraction, bool]) -> bool:
    value, inclusive = bound
    return x >= value if inclusive else x > value


def solve(text: str, q: dict) -> dict:
    base = grab(r"jurisdiction base score is {N}", text)
    mult = grab(r"sector multiplier is {N}", text)
    override = _bool(r"high-risk override is", text)
    edd = _bool(r"EDD flag is", text)

    # Exact composite; thresholds are applied to the exact (unrounded) value.
    composite = base * mult

    high_t = _threshold("high_risk", text, Fraction(8))
    med_t = _threshold("medium_risk", text, Fraction(5))

    numeric_high = _meets(composite, high_t)
    numeric_med = _meets(composite, med_t)

    if numeric_high:
        band = "high_risk"
    elif numeric_med:
        band = "medium_risk"
    else:
        band = "standard_risk"

    if numeric_high or override:
        final = "high_risk"
    elif numeric_med or edd:
        final = "medium_risk"
    else:
        final = "standard_risk"

    return {
        "final": final,
        "slots": {"composite_risk_score": composite, "numeric_risk_band": band},
    }
