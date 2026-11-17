from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.personal_finance.taxcalc.capital_gains.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    proceeds = grab(r"[Ss]ale proceeds in USD (?:are|is) {N}", text)
    basis = grab(r"[Cc]ost basis in USD (?:is|are) {N}", text)
    ratio = grab(r"[Cc]apital-gain tax ratio is {N}", text)
    # Taxable gain is the larger of (proceeds - basis) and zero.
    gain = max(proceeds - basis, Fraction(0))
    tax = gain * ratio
    return {"final": tax, "slots": {"taxable_gain_usd": gain}}
