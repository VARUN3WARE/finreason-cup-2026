# =====================================================================================
# h107 -- two closed FX routes (3-leg Route A, 2-leg Route B), fee + fixed cost, hurdle
# Lens: FINANCE MODEL FIRST (domain analyst).
# =====================================================================================
#
# ECONOMIC MODEL
# --------------
# Inputs (all read from the text, never hardcoded):
#   C          starting USD capital                       ("USD capital N")
#   Route A    USD -> X -> Y -> USD, three quotes         ("N is X per USD", "N is Y per X", "N is USD per Y")
#   Route B    USD -> Z -> USD, two quotes                ("N is Z per USD", "N is USD per Z")
#   fee_A, fee_B   single aggregate proportional fee      ("proportional fee fA or fB", A first, then B)
#   K_A, K_B       fixed USD cost                         ("fixed USD cost kA or kB", A first, then B)
#   h          return hurdle on starting capital          ("return hurdle h on starting capital")
#
# 1. Quote convention.  "q is U per V" means one unit of V buys q units of U.  Converting a
#    holding of V into U therefore MULTIPLIES by q (converting U into V would divide by q).
#    Every leg of both routes is quoted in its direction of travel, so each leg multiplies.
#    (The solver nevertheless parses the route path and divides if a quote is ever given the
#    other way round; that branch is not exercised by these instances.)
#
# 2. Gross multiplier of a closed route (USD out per USD in, before fee and cost):
#        g_A = (X per USD) * (Y per X) * (USD per Y)          three legs
#        g_B = (Z per USD) * (USD per Z)                      two legs
#    These two ratios are the two checkpoints (position 1 = Route A, position 2 = Route B).
#    They are reported UNROUNDED; the framework rounds half up to 8 decimals.
#
# 3. Gross USD proceeds of a route:     P = C * g
#
# 4. Fee: a SINGLE aggregate proportional fee applied ONCE to the final USD proceeds
#    (NOT once per leg, NOT on the starting capital):     P_net = P * (1 - fee)
#    "proportional fee 0.1" is a plain ratio (10 percent of proceeds); no percent word is used.
#
# 5. Fixed cost is subtracted AFTER the fee, in USD:      T = P * (1 - fee) - K
#    T is the exact terminal USD value of the route.  No floor at zero is stated, so none is applied.
#
# 6. Qualification: "terminal value meets return hurdle h on starting capital" means
#        (T - C) / C  >=  h          <=>   T  >=  C * (1 + h)         (non-strict: "meets")
#    h = 0 is a break-even hurdle (T >= C).  h is a plain ratio, 0.08 = 8 percent.
#
# 7. Decision (all comparisons exact, Fractions only):
#       both qualify    -> higher exact T wins; exact tie -> "Route A"
#       exactly one     -> that route
#       neither         -> "No trade"
#
# 8. Rounding: none inside the computation.  Only the two checkpoints are rounded, and only
#    by the framework at render time (half up, 8 places).  The decision never uses a rounded value.
#
# OVERRIDES OF STANDARD CONVENTION: none beyond the text itself (fee once on final proceeds,
# fixed cost after fee, "meets" is >=, tie goes to Route A).
#
# AMBIGUITIES RESOLVED
#   * "fee 0.1 or 0.1", "cost 13 or 21": read as "Route A's value or Route B's value" in the
#     order the routes were introduced (A first).  The decisions do not depend on this order
#     for the three given instances.
#   * "return hurdle h on starting capital": read as profit/capital >= h, i.e. T >= C(1+h),
#     not as T >= h*C.
#   * The decision is also invariant, on all three instances, to reading the fee as a percent
#     or in basis points, or to taking the fixed cost before the fee.
# =====================================================================================

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab, grab_all

TEMPLATE_ID = "h107"

_QUOTE = re.compile(r"(" + NUMBER + r")\s+is\s+([A-Za-z]+)\s+per\s+([A-Za-z]+)")


def _route(label: str, text: str) -> Fraction:
    """Gross multiplier of closed route ``label`` ("A" or "B"): product of its leg conversions."""
    m = re.search(
        r"Route " + label + r" follows\s+([A-Za-z]+(?:\s+to\s+[A-Za-z]+)+)\s*:(.*?)(?:\.(?:\s|$)|$)",
        text,
        flags=re.S,
    )
    if m is None:
        raise ValueError(f"route {label} sentence not found")
    path = [p.strip() for p in re.split(r"\s+to\s+", m.group(1))]
    quotes = [(F(n), a, b) for n, a, b in _QUOTE.findall(m.group(2))]
    if len(quotes) != len(path) - 1:
        raise ValueError(f"route {label}: {len(quotes)} quotes for path {path}")
    g = Fraction(1)
    used: set[int] = set()
    cur = path[0]
    for nxt in path[1:]:
        # direct quote first ("rate is NEXT per CUR" -> multiply), each quote used by exactly one leg
        hit = next(
            (i for i, (_, u_per, v) in enumerate(quotes) if i not in used and u_per == nxt and v == cur),
            None,
        )
        if hit is not None:
            g *= quotes[hit][0]
        else:
            # inverted quote ("rate is CUR per NEXT" -> divide); not expected for these instances
            hit = next(
                (i for i, (_, u_per, v) in enumerate(quotes) if i not in used and u_per == cur and v == nxt),
                None,
            )
            if hit is None:
                raise ValueError(f"route {label}: no quote for leg {cur}->{nxt}")
            g /= quotes[hit][0]
        used.add(hit)
        cur = nxt
    return g


def solve(text: str, q: dict) -> dict:
    capital = grab(r"USD capital {N}", text)
    hurdle = grab(r"return hurdle {N} on starting capital", text)
    fee_a, fee_b = grab_all(r"proportional fee {N} or {N}", text)
    cost_a, cost_b = grab_all(r"fixed USD cost {N} or {N}", text)

    g_a = _route("A", text)  # three-leg gross multiplier
    g_b = _route("B", text)  # two-leg gross multiplier

    # terminal value = proceeds * (1 - single aggregate fee) - fixed cost
    t_a = capital * g_a * (1 - fee_a) - cost_a
    t_b = capital * g_b * (1 - fee_b) - cost_b

    # return hurdle on starting capital: (T - C) / C >= h  <=>  T >= C * (1 + h)
    needed = capital * (1 + hurdle)
    ok_a = t_a >= needed
    ok_b = t_b >= needed

    if ok_a and ok_b:
        final = "Route B" if t_b > t_a else "Route A"  # exact tie -> Route A
    elif ok_a:
        final = "Route A"
    elif ok_b:
        final = "Route B"
    else:
        final = "No trade"

    return {
        "final": final,
        "slots": {
            "a_gross_multiplier_checkpoint": g_a,
            "b_gross_multiplier_checkpoint": g_b,
        },
    }
