from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.accounting_and_financial_reporting.depreciation_and_amortization.asset_impairment_reversal.advanced.v1"


def solve(text: str, q: dict) -> dict:
    current = grab(r"carrying amount before reversal is (?:USD )?{N}", text)
    ceiling = grab(r"had no impairment ever been recognized would be (?:USD )?{N}", text)
    proposed = grab(r"proposed reversal of (?:USD )?{N}", text)
    gap = ceiling - current  # trace_1: unfloored (may be negative)
    room = max(Fraction(0), gap)  # trace_2: nonnegative room under the ceiling
    recognized = min(proposed, room)
    return {"final": recognized, "slots": {"trace_1": gap, "trace_2": room}}
