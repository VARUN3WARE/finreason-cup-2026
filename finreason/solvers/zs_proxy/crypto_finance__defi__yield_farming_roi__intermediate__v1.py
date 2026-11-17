from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.defi.yield_farming_roi.intermediate.v1"

PCT = r"\s*(?:percent|%)"


def solve(text: str, q: dict) -> dict:
    inv = grab(r"initial investment is (?:USD\s*)?{N}", text)
    roi = grab(r"annualized return is {N}" + PCT, text) / 100
    months = grab(r"holding period is {N}\s*months?", text)
    frac = months / 12
    return {
        "final": inv * roi * frac,
        "slots": {
            "annual_roi_ratio_trace": roi,
            "holding_fraction_trace": frac,
        },
    }
