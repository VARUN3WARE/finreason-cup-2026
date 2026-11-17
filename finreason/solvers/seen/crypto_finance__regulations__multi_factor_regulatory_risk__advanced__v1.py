from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "fp.crypto_finance.regulations.multi_factor_regulatory_risk.advanced.v1"


def solve(text: str, q: dict) -> dict:
    base = grab(r"baseline compliance cost of {N} USD", text)
    a, b, c = grab_all(r"surcharge factors are {N},\s*{N},?\s*and {N} percent", text)
    credit = grab(r"credit of {N} USD", text)
    total_pct = a + b + c                      # slot reported in percent units
    gross = base * total_pct / 100
    credited = gross - credit                  # unfloored (gold shows negatives)
    final = credited if credited > 0 else Fraction(0)
    return {
        "final": final,
        "slots": {
            "total_factor_trace": total_pct,
            "gross_cost_trace": gross,
            "credited_cost_trace": credited,
        },
    }
