from fractions import Fraction
from finreason.nums import grab, grab_all

TEMPLATE_ID = "fp.crypto_finance.regulations.multi_factor_regulatory_risk.advanced.v1"


def solve(text: str, q: dict) -> dict:
    base = grab(r"baseline compliance cost of {N} USD", text)
    f1, f2, f3 = grab_all(r"factors are {N},? {N},? and {N} percent", text)
    credit = grab(r"credit of {N} USD", text)
    total_pct = f1 + f2 + f3                 # combined factor, in percent
    gross = base * total_pct / 100           # gross additional compliance cost
    credited = gross - credit                # after credit, before the zero floor
    final = max(credited, Fraction(0))
    return {
        "final": final,
        "slots": {
            "total_factor_trace": total_pct,
            "gross_cost_trace": gross,
            "credited_cost_trace": credited,
        },
    }
