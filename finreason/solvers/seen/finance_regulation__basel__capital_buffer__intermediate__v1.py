from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.basel.capital_buffer.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    rwa = grab(r"[Rr]isk-weighted assets in USD millions (?:are|is) {N}", text)
    base = grab(r"[Bb]ase required percent is {N}", text)
    buf = grab(r"[Bb]uffer percent is {N}", text)
    total_pct = base + buf
    required = total_pct / 100 * rwa  # exact; framework rounds half up to 2 dp
    return {"final": required, "slots": {"total_required_percent": total_pct}}
