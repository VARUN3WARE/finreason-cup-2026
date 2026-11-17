from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.basel.capital_buffer.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    rwa = grab(r"[Rr]isk-weighted assets in USD millions (?:are|is) {N}", text)
    base = grab(r"[Bb]ase required percent is {N}", text)
    buffer = grab(r"[Bb]uffer percent is {N}", text)
    total_pct = base + buffer                      # percent
    required = total_pct / 100 * rwa               # USD millions, unrounded (framework rounds final)
    return {"final": required, "slots": {"total_required_percent": total_pct}}
