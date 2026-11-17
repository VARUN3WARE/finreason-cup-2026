"""h079: minimum reported EBITDA to support a target equity value.

Equity -> EV bridge via net debt (debt - cash), EV / multiple = required
normalized EBITDA, then add back the recurring diligence deduction to get the
reported EBITDA.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h079"


def _first(patterns, text):
    for p in patterns:
        try:
            return grab(p, text)
        except ValueError:
            continue
    raise ValueError(f"none of the patterns matched: {patterns!r}")


def solve(text: str, q: dict) -> dict:
    equity = _first([
        r"target equity value of\s+(?:USD\s*)?\$?{N}",
        r"equity value of\s+(?:USD\s*)?\$?{N}",
    ], text)
    debt = _first([
        r"total debt of\s+(?:USD\s*)?\$?{N}",
        r"debt of\s+(?:USD\s*)?\$?{N}",
    ], text)
    cash = _first([
        r"cash of\s+(?:USD\s*)?\$?{N}",
        r"cash (?:balance )?of\s+(?:USD\s*)?\$?{N}",
    ], text)
    multiple = _first([
        r"values normalized EBITDA at\s+(?:a multiple of\s+)?{N}",
        r"normalized EBITDA at\s+(?:a multiple of\s+)?{N}",
        r"multiple of\s+{N}",
    ], text)
    deduction = _first([
        r"EBITDA deduction of\s+(?:USD\s*)?\$?{N}",
        r"deduction of\s+(?:USD\s*)?\$?{N}",
    ], text)

    net_debt = debt - cash                      # may be negative (net cash)
    enterprise_value = equity + net_debt        # equity -> EV bridge
    normalized_ebitda = enterprise_value / multiple
    reported_ebitda = normalized_ebitda + deduction   # restore the deduction

    return {
        "final": Fraction(reported_ebitda),
        "slots": {"net_debt_checkpoint": Fraction(net_debt)},
    }
