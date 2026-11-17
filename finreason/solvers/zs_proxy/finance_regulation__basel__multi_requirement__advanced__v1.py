from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.basel.multi_requirement.advanced.v1"


def _tok(b: bool) -> str:
    return "true" if b else "false"


def solve(text: str, q: dict) -> dict:
    t1 = grab(r"Tier 1 capital is {N} USD million", text)
    exposure = grab(r"Exposure is {N} USD million", text)
    total_cap = grab(r"Total capital is {N} USD million", text)
    rwa = grab(r"Risk-weighted assets (?:are|is) {N} USD million", text)
    liq = grab(r"Liquidity assets (?:are|is) {N} USD million", text)
    outflows = grab(r"Net outflows (?:are|is) {N} USD million", text)
    lev_min = grab(r"Leverage must be at least {N} percent", text)
    cap_min = grab(r"total capital at least {N} percent of RWA", text)
    liq_min = grab(r"liquidity at least {N} percent of outflows", text)

    # "at least" -> inclusive (>=)
    leverage_met = t1 / exposure * 100 >= lev_min
    capital_met = total_cap / rwa * 100 >= cap_min
    liquidity_met = liq / outflows * 100 >= liq_min
    final = leverage_met and capital_met and liquidity_met  # "All three must hold"
    return {
        "final": _tok(final),
        "slots": {
            "leverage_met": _tok(leverage_met),
            "capital_met": _tok(capital_met),
            "liquidity_met": _tok(liquidity_met),
        },
    }
