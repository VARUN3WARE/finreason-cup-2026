"""h107 -- literal transcription: two closed FX routes from a home-currency capital.

Route A is a three-leg loop (home -> X -> Y -> home), Route B a two-leg loop
(home -> Z -> home).  Each closed route's final home-currency proceeds get one
aggregate proportional fee, then a fixed cost.  A route qualifies when its exact
terminal value meets the return hurdle on starting capital; pick the qualifying
route with the higher exact terminal value (exact tie -> Route A), else No trade.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab, grab_all

TEMPLATE_ID = "h107"


def _route(text: str, label: str) -> tuple[list[str], list[tuple[Fraction, str, str]]]:
    """Sentence 'Route <label> follows P0 to P1 to ... to Pn: <r> is C per D, ...'.

    Returns the currency path and the stated quotes (rate, numerator ccy, per ccy).
    The sentence ends at the first period followed by whitespace/end (decimal
    points inside numbers are followed by digits, so they never end it).
    """
    m = re.search(rf"Route {label} follows (.+?):\s*(.+?)\.(?=\s|$)", text, flags=re.S)
    if m is None:
        raise ValueError(f"route {label} sentence not found")
    path = [c.strip() for c in m.group(1).split(" to ")]
    quotes = [
        (F(q.group(1)), q.group(2), q.group(3))
        for q in re.finditer(rf"({NUMBER}) is (\w+) per (\w+)", m.group(2))
    ]
    return path, quotes


def _gross_multiplier(path: list[str], quotes: list[tuple[Fraction, str, str]]) -> Fraction:
    """Chain the legs: converting 1 unit of D into C at a quote 'r is C per D' yields r units of C."""
    mult = Fraction(1)
    for src, dst in zip(path, path[1:]):
        direct = [r for r, num, per in quotes if num == dst and per == src]  # 'dst per src'
        if len(direct) == 1:
            mult *= direct[0]
            continue
        # Fallback only if the leg is stated the other way round ('src per dst'): divide.
        inverse = [r for r, num, per in quotes if num == src and per == dst]
        if not direct and len(inverse) == 1:
            mult /= inverse[0]
            continue
        raise ValueError(f"no unique quote for leg {src}->{dst}")
    return mult


def solve(text: str, q: dict) -> dict:
    # S1: "Starting with USD capital 99, compare two closed FX routes."
    home = re.search(r"Starting with (\w+) capital", text).group(1)
    capital = grab(rf"Starting with {home} capital {{N}}", text)

    # S2: "Route A follows USD to X to Y to USD: 0.5 is X per USD, 0.5 is Y per X, and 1.6 is USD per Y."
    a_path, a_quotes = _route(text, "A")
    assert a_path[0] == home and a_path[-1] == home and len(a_path) == 4  # closed three-leg route
    a_gross = _gross_multiplier(a_path, a_quotes)  # Route A's three-leg gross multiplier

    # S3: "Route B follows USD to Z to USD: 0.5 is Z per USD and 1.612480005 is USD per Z."
    b_path, b_quotes = _route(text, "B")
    assert b_path[0] == home and b_path[-1] == home and len(b_path) == 3  # closed two-leg route
    b_gross = _gross_multiplier(b_path, b_quotes)  # Route B's two-leg gross multiplier

    # S4: "After each closed route, apply its single aggregate proportional fee 0.1 or 0.1 once to
    #      final USD proceeds, then subtract fixed USD cost 13 or 21."  ("x or y" = Route A or Route B)
    fee_a, fee_b = grab_all(r"single aggregate proportional fee {N} or {N}", text)
    cost_a, cost_b = grab_all(rf"fixed {home} cost {{N}} or {{N}}", text)

    a_final_proceeds = capital * a_gross          # USD after closing Route A
    b_final_proceeds = capital * b_gross          # USD after closing Route B
    a_after_fee = a_final_proceeds * (1 - fee_a)  # fee applied once to final proceeds
    b_after_fee = b_final_proceeds * (1 - fee_b)
    a_terminal = a_after_fee - cost_a             # then subtract fixed cost -> exact terminal value
    b_terminal = b_after_fee - cost_b

    # S5: "A route qualifies only if its exact terminal value meets return hurdle 0.08 on starting capital."
    hurdle = grab(r"return hurdle {N} on starting capital", text)
    a_return = (a_terminal - capital) / capital   # return on starting capital
    b_return = (b_terminal - capital) / capital
    a_qualifies = a_return >= hurdle              # "meets" = at least the hurdle
    b_qualifies = b_return >= hurdle

    # S6: "Select the qualifying route with the higher exact terminal value, select Route A when both
    #      qualify and tie exactly, or return No trade when neither qualifies."
    if a_qualifies and b_qualifies:
        if a_terminal > b_terminal:
            final = "Route A"
        elif b_terminal > a_terminal:
            final = "Route B"
        else:
            final = "Route A"  # exact tie
    elif a_qualifies:
        final = "Route A"
    elif b_qualifies:
        final = "Route B"
    else:
        final = "No trade"

    return {
        "final": final,
        "slots": {
            "a_gross_multiplier_checkpoint": a_gross,
            "b_gross_multiplier_checkpoint": b_gross,
        },
    }
