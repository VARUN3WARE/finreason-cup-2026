"""h062: FX round-trip with entry/exit fee retention and a financing charge;
solve for the exit-quote threshold that delivers a target net return.

Capital C (reporting) -> base units C / E_entry, keep (1 - f_entry).
Exit: base * X * (1 - f_exit) reporting, then minus k * C financing charge.
Net return = (1-f_entry)(1-f_exit) X / E_entry - k - 1 = r
=> gross growth multiple (return + carry) G = 1 + r + k
=> X = G * E_entry / ((1 - f_entry)(1 - f_exit)).
"""
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h062"


def solve(text: str, q: dict) -> dict:
    e_entry = grab(r"normalized entry quote {N}", text)
    f_entry = grab(r"entry conversion retains one minus fee ratio {N}", text)
    f_exit = grab(r"exit quote to be solved for and retain one minus fee ratio {N}", text)
    k = grab(r"financing charge equal to {N} times", text)
    r = grab(r"net return equals {N}", text)

    gross = Fraction(1) + r + k
    keep = (Fraction(1) - f_entry) * (Fraction(1) - f_exit)
    x = gross * e_entry / keep

    return {"final": x, "slots": {"gross_growth_checkpoint": gross}}
