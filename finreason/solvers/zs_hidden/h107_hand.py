"""h107: compare two closed FX routes (3-leg Route A vs 2-leg Route B).

Per route:
  gross multiplier M = product of leg conversion factors along the stated path
                       (rate quoted "<dst> per <src>" multiplies; "<src> per <dst>" divides)
  terminal value TV  = capital * M * (1 - proportional fee) - fixed USD cost
  qualifies         iff (TV - capital) / capital >= hurdle     ("meets" = at least)
Decision: higher exact TV among qualifying routes; exact tie (both qualify) -> Route A;
neither qualifies -> No trade.
Checkpoints: unrounded gross multipliers of Route A and Route B (framework rounds half up, 8 dp).
"""

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h107"

_RATE_RX = re.compile(rf"({NUMBER})\s*(percent|%)?\s+is\s+([A-Za-z]+)\s+per\s+([A-Za-z]+)")


def _scaled(num: str, unit: str | None) -> Fraction:
    v = F(num)
    return v / 100 if unit else v


def _pair(pattern: str, text: str) -> tuple[Fraction, Fraction]:
    """Two numbers of an 'x or y' phrase (Route A's value first, Route B's second)."""
    rx = pattern.replace("{N}", rf"({NUMBER})(\s*(?:percent|%))?")
    m = re.search(rx, text, flags=re.S)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    a = _scaled(m.group(1), m.group(2))
    b = _scaled(m.group(3), m.group(4))
    return a, b


def _route_multiplier(text: str, label: str) -> Fraction:
    start = text.index(f"Route {label} follows")
    seg = text[start:]
    # sentence ends at a period followed by whitespace (decimal points are followed by digits)
    end = re.search(r"\.(\s|$)", seg)
    seg = seg[: end.start()] if end else seg
    path_txt, rates_txt = seg.split(":", 1)
    path_txt = path_txt[len(f"Route {label} follows"):].strip()
    path = [p.strip() for p in path_txt.split(" to ")]
    quotes = []
    for m in _RATE_RX.finditer(rates_txt):
        quotes.append((_scaled(m.group(1), m.group(2)), m.group(3), m.group(4)))
    legs = list(zip(path, path[1:]))
    if not legs:
        raise ValueError(f"no legs parsed for Route {label}")
    mult = Fraction(1)
    if len(quotes) == len(legs):
        # quotes are listed in leg order: pair them positionally
        for (src, dst), (rate, num_ccy, den_ccy) in zip(legs, quotes):
            if num_ccy == dst and den_ccy == src:
                mult *= rate          # "<dst> per <src>": units received per unit paid
            elif num_ccy == src and den_ccy == dst:
                mult /= rate          # inverse quote
            else:
                raise ValueError(f"quote {num_ccy}/{den_ccy} does not fit leg {src}->{dst}")
        return mult
    # fallback: prefer a direct quote for each leg, else an inverse one
    for src, dst in legs:
        direct = [r for r, n, d in quotes if n == dst and d == src]
        inverse = [r for r, n, d in quotes if n == src and d == dst]
        if direct:
            mult *= direct[0]
        elif inverse:
            mult /= inverse[0]
        else:
            raise ValueError(f"no quote for leg {src}->{dst} in Route {label}")
    return mult


def solve(text: str, q: dict) -> dict:
    capital = grab(r"USD capital {N}", text)

    m_a = _route_multiplier(text, "A")
    m_b = _route_multiplier(text, "B")

    fee_a, fee_b = _pair(r"proportional fee {N} or {N}", text)
    cost_a, cost_b = _pair(r"fixed USD cost {N} or {N}", text)

    hm = re.search(rf"return hurdle ({NUMBER})(\s*(?:percent|%))?", text)
    if hm is None:
        raise ValueError("hurdle not found")
    hurdle = _scaled(hm.group(1), hm.group(2))

    tv_a = capital * m_a * (1 - fee_a) - cost_a
    tv_b = capital * m_b * (1 - fee_b) - cost_b

    # "meets return hurdle h on starting capital": (TV - capital)/capital >= h
    q_a = (tv_a - capital) / capital >= hurdle
    q_b = (tv_b - capital) / capital >= hurdle

    if q_a and q_b:
        final = "Route A" if tv_a >= tv_b else "Route B"
    elif q_a:
        final = "Route A"
    elif q_b:
        final = "Route B"
    else:
        final = "No trade"

    return {
        "final": final,
        "slots": {
            "a_gross_multiplier_checkpoint": m_a,
            "b_gross_multiplier_checkpoint": m_b,
        },
    }
