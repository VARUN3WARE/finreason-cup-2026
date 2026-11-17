from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.personal_finance.saveretire.years_to_target.basic.v1"


def solve(text: str, q: dict) -> dict:
    target = grab(r"Target savings in USD (?:are|is) {N}", text)
    current = grab(r"Current savings in USD (?:are|is) {N}", text)
    annual = grab(r"Annual saving in USD per year (?:is|are) {N}", text)
    gap = max(target - current, Fraction(0))
    # fractional years allowed, no ceiling; a zero gap needs zero years even if saving were zero
    years = Fraction(0) if gap == 0 else gap / annual
    return {"final": years, "slots": {"funding_gap_usd": gap}}
