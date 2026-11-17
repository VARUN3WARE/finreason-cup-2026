"""h081: two-strategy allocation with upside/downturn floor constraints.

Feasible interval for the Strategy A weight w comes from two linear
requirements (upside floor -> lower endpoint, downturn floor -> upper
endpoint).  The endpoint is chosen by comparing the exact
probability-weighted ending values of an all-A versus an all-B allocation
(strictly greater for A -> upper endpoint; otherwise, ties included ->
lower endpoint).
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h081"


def _rate(pattern: str, text: str) -> Fraction:
    """Grab a rate; tolerate an optional trailing percent marker."""
    import re

    from finreason.nums import NUMBER

    rx = pattern.replace("{N}", f"({NUMBER})\\s*(%|percent)?")
    m = re.search(rx, text, flags=re.S)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    v = Fraction(m.group(1).replace(",", ""))
    if m.group(2):
        v /= 100
    return v


def solve(text: str, q: dict) -> dict:
    cap = grab(r"of capital (?:USD |\$)?{N}", text)
    p_down = _rate(r"downturn probability is {N}", text)
    p_up = 1 - p_down

    b_up = _rate(r"Strategy B earns upside return {N}", text)
    b_loss = _rate(r"and loses {N} in the downturn", text)
    inc_up = _rate(r"positive incremental return {N}", text)
    inc_loss = _rate(r"positive incremental loss {N}", text)

    a_up = b_up + inc_up          # Strategy A upside return
    a_loss = b_loss + inc_loss    # Strategy A downturn loss (magnitude)

    need_up = grab(r"at least (?:USD |\$)?{N} in the upside scenario", text)
    need_down = grab(r"at least (?:USD |\$)?{N} in the downturn", text)

    # Gross growth factors per unit of capital.
    ga_u, gb_u = 1 + a_up, 1 + b_up
    ga_d, gb_d = 1 - a_loss, 1 - b_loss

    # Upside: cap*(gb_u + w*(ga_u-gb_u)) >= need_up  -> w >= lo  (ga_u > gb_u)
    lo = (need_up / cap - gb_u) / (ga_u - gb_u)
    # Downturn: cap*(gb_d + w*(ga_d-gb_d)) >= need_down -> w <= hi (ga_d < gb_d)
    hi = (need_down / cap - gb_d) / (ga_d - gb_d)

    # Probability-weighted ending values of all-A vs all-B allocations.
    a_up_weighted = p_up * cap * ga_u
    a_down_weighted = p_down * cap * ga_d
    ev_a = a_up_weighted + a_down_weighted

    b_up_value = cap * gb_u
    b_down_value = cap * gb_d
    ev_b = p_up * b_up_value + p_down * b_down_value

    w = hi if ev_a > ev_b else lo

    return {
        "final": w * 100,
        "slots": {
            "strategy_a_weighted_upside_checkpoint": a_up_weighted,
            "strategy_b_downturn_checkpoint": b_down_value,
        },
    }
