from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.personal_finance.saveretire.additional_saving.basic.v1"


def solve(text: str, q: dict) -> dict:
    target = grab(r"Target savings in USD (?:are|is) {N}", text)
    current = grab(r"Current savings in USD (?:are|is) {N}", text)
    annual = grab(r"Existing annual saving in USD per year (?:is|are) {N}", text)
    years = grab(r"years remaining (?:are|is) {N}", text)
    projected = current + annual * years
    shortfall = max(target - projected, Fraction(0))
    additional = shortfall / years
    return {
        "final": additional,
        "slots": {"projected_available_usd": projected, "shortfall_usd": shortfall},
    }
