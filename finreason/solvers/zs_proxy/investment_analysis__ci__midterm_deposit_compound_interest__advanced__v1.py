from fractions import Fraction
from finreason.nums import grab, real_pow

TEMPLATE_ID = "fp.investment_analysis.ci.midterm_deposit_compound_interest.advanced.v1"


def _pow(base: Fraction, e: Fraction) -> Fraction:
    e = Fraction(e)
    return base ** int(e) if e.denominator == 1 else real_pow(base, e)


def solve(text: str, q: dict) -> dict:
    p0 = grab(r"starts with USD {N}", text)
    t1 = grab(r"After {N} years?, an additional", text)
    d = grab(r"an additional USD {N} is deposited", text)
    r = grab(r"compound rate is {N} percent", text)
    t2 = grab(r"remains invested for {N} more years?", text)
    g = 1 + r / 100
    init_end = p0 * _pow(g, t1 + t2)
    dep_end = d * _pow(g, t2)
    total = init_end + dep_end
    return {
        "final": total - p0 - d,
        "slots": {
            "initial_ending_trace": init_end,
            "deposit_ending_trace": dep_end,
            "ending_balance_trace": total,
        },
    }
