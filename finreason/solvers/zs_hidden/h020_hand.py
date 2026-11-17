"""h020: cooperation credit percentage that makes credited penalty + fixed interest = max total remedy."""
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h020"


def solve(text: str, q: dict) -> dict:
    max_total = grab(r"maximum total remedy is {N} USD", text)
    interest = grab(r"of which {N} USD is fixed interest", text)
    gain = grab(r"realized gain {N} USD", text)
    mult = grab(r"realized gain [^ ]+ USD multiplied by {N}", text)
    floor_amt = grab(r"statutory floor is {N} USD", text)

    # Cap available for penalty after fixed interest.
    cap = max_total - interest
    # Pre-credit base: greater of gain-based penalty and statutory floor.
    base = max(gain * mult, floor_amt)
    # (1 - c) * base + interest = max_total  =>  c = 1 - cap / base
    c = 1 - cap / base
    return {
        "final": Fraction(c * 100),
        "slots": {"penalty_cap_checkpoint": Fraction(cap)},
    }
