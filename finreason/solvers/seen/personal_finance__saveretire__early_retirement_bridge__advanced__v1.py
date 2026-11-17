from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.personal_finance.saveretire.early_retirement_bridge.advanced.v1"


def solve(text: str, q: dict) -> dict:
    savings = grab(r"Liquid savings in USD (?:are|is) {N}", text)
    spending = grab(r"Annual spending in USD per year (?:is|are) {N}", text)
    years = grab(r"bridge years (?:are|is) {N}", text)
    other = grab(r"Annual other income in USD per year (?:is|are) {N}", text)
    ratio = grab(r"Contingency ratio (?:is|are) {N}", text)
    net_need = max(spending - other, Fraction(0))
    base = net_need * years
    contingency = base * ratio
    required = base + contingency
    gap = required - savings  # signed
    funded = savings >= required  # equality counts as funded
    return {
        "final": "true" if funded else "false",
        "slots": {
            "net_annual_need": net_need,
            "required_capital_usd": required,
            "funding_gap_usd": gap,
        },
    }
