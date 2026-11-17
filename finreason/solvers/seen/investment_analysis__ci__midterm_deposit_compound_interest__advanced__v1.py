from fractions import Fraction

from finreason.nums import grab, real_pow

TEMPLATE_ID = "fp.investment_analysis.ci.midterm_deposit_compound_interest.advanced.v1"


def _pow(base: Fraction, n: Fraction) -> Fraction:
    if n.denominator == 1:
        return base ** int(n)
    return real_pow(base, n)


def solve(text: str, q: dict) -> dict:
    principal = grab(r"starts with\s+USD\s+{N}", text)
    n1 = grab(r"After\s+{N}\s+years?,\s+an additional", text)
    deposit = grab(r"additional\s+USD\s+{N}\s+is deposited", text)
    rate = grab(r"annual compound rate is\s+{N}\s+percent", text) / 100
    n2 = grab(r"remains invested for\s+{N}\s+more years?", text)
    g = 1 + rate
    initial_end = principal * _pow(g, n1 + n2)
    deposit_end = deposit * _pow(g, n2)
    ending = initial_end + deposit_end
    return {
        "final": ending - principal - deposit,
        "slots": {
            "initial_ending_trace": initial_end,
            "deposit_ending_trace": deposit_end,
            "ending_balance_trace": ending,
        },
    }
