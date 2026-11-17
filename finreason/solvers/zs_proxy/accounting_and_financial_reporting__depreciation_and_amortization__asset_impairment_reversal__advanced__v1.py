from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.accounting_and_financial_reporting.depreciation_and_amortization.asset_impairment_reversal.advanced.v1"


def solve(text: str, q: dict) -> dict:
    carrying = grab(r"carrying amount before reversal is {N} USD", text)
    ceiling = grab(r"had no impairment ever been recognized would be {N} USD", text)
    proposed = grab(r"proposed reversal of {N} USD", text)
    gap = ceiling - carrying                      # unfloored gap to the ceiling
    room = max(Fraction(0), gap)                  # nonnegative reversal room
    recognized = min(proposed, room)
    return {"final": recognized, "slots": {"trace_1": gap, "trace_2": room}}
