"""h086 -- downturn / recovery scenario choice: expansion vs defensive vs wait.

Structure (all three instances share it):
  revenue R, downturn ratio d, recovery ratio g (only if the one-period cash outlay C is made),
  baseline operating cost K inflated by ratio i, available cash A, required one-period surplus S.
  Expansion surplus  = R*(1-d)*(1+g) - K*(1+i) - C
  Defensive surplus  = R*(1-d)       - K*(1+i)
  expansion if (expansion surplus >= S) and (A >= C); else defensive if defensive surplus >= S; else wait.
  Checkpoint post_downturn_checkpoint = R*(1-d)  (usd, 2dp half-up, applied by the framework).

AMBIGUITIES CONSIDERED AND HOW THEY WERE RESOLVED
1. "downturn ratio d": fractional DECLINE (post-downturn revenue = R*(1-d)), not a survival multiplier (R*d).
   Evidence: instance 3 has R = 99133/990 and d = 0.01; R*(1-d) = 99.133 exactly (a clean terminating decimal,
   i.e. the generator back-solved R from a target post-downturn value), whereas R*d = 99133/99000 does not
   terminate.  A "downturn ratio 0.01" read as a 99 % collapse is also economically absurd.  For d = 0.5 the two
   readings coincide, so only instance 3's checkpoint depends on this.
2. "recovery ratio g" in the expansion scenario: multiplicative uplift on the post-downturn revenue,
   R*(1-d)*(1+g) ("applies both downturn and recovery" = apply the two factors in sequence).  The alternative
   reading (recover fraction g of the LOST revenue: R*(1-d) + g*R*d) gives the identical number whenever d = 0.5,
   which is the only instance with g != 0 (instance 2: 102*1.2 = 122.4 either way); instances 1 and 3 have g = 0.
   The branch outcome of instance 2 is insensitive to the reading anyway (surplus passes, cash fails).
3. "inflated operating cost": K*(1+i), the cost-inflation ratio is a fractional increase ("rises by").  i = 0 in
   all three instances, so no instance is sensitive to this.
4. Expansion surplus subtracts BOTH the inflated operating cost AND the cash outlay; defensive subtracts only the
   inflated operating cost (no outlay, no recovery) -- exactly as the two sentences say.
5. "surplus of at least S": NON-STRICT (surplus >= S).  Instance 2's defensive surplus is exactly 41 = S, so this is
   the designed tie; "at least" is unambiguous -> passes -> "defensive".
6. "cash requirement" for expansion: available cash must cover the one-period cash outlay, A >= C (non-strict:
   cash equal to the outlay suffices).  Instances 1 and 3 have A == C (both pass the cash test but fail the surplus
   test, so the strictness never changes their outcome); instance 2 has A = 4 < C = 11 -> fails -> falls through to
   defensive even though its expansion surplus (50.4) passes.  No other quantity in the text could be a "cash
   requirement" (the surplus threshold is already named separately as the "surplus threshold").
7. Decision order: expansion is checked first (needs BOTH tests); "Otherwise" defensive needs only its own surplus
   test; "wait if neither passes".  Note the defensive check is made even when expansion's surplus passed but its
   cash failed (that IS the "otherwise" case).
8. Checkpoint "revenue after the downturn" = R*(1-d) only -- before recovery, before cost deductions.  Unit usd,
   same unit as the stated revenue.  Returned unrounded; no intermediate rounding is mentioned anywhere in the text.
9. All quantities are plain ratios (the text says "ratio" everywhere); a percent form is handled defensively
   (divided by 100) in case a sibling instance phrases a rate as "N percent" / "N%".
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F

TEMPLATE_ID = "h086"

_PCT_TAIL = r"\s*(?:%|percent|per cent)"


def _num(patterns: list[str], text: str) -> Fraction:
    """First pattern that matches wins; {N} is the number capture."""
    for pat in patterns:
        m = re.search(pat.replace("{N}", f"({NUMBER})"), text, flags=re.S | re.I)
        if m:
            return F(m.group(1))
    raise ValueError(f"none of {patterns!r} found")


def _rate(patterns: list[str], text: str) -> Fraction:
    """Like _num, but a trailing '%'/'percent' turns the number into a ratio."""
    for pat in patterns:
        rx = pat.replace("{N}", f"({NUMBER})") + f"(?P<pct>{_PCT_TAIL})?"
        m = re.search(rx, text, flags=re.S | re.I)
        if m:
            v = F(m.group(1))
            return v / 100 if m.group("pct") else v
    raise ValueError(f"none of {patterns!r} found")


def solve(text: str, q: dict) -> dict:
    revenue = _num([r"starts with (?:a |an )?(?:initial |baseline |current )?revenue (?:of )?(?:USD )?{N}",
                    r"revenue (?:of )?(?:USD )?{N}"], text)
    downturn = _rate([r"downturn (?:ratio|rate|of) (?:of )?{N}", r"downturn {N}"], text)
    recovery = _rate([r"recovery (?:ratio|rate|of) (?:of )?{N}", r"recovery {N}"], text)
    outlay = _num([r"cash outlay (?:of )?(?:USD )?{N}", r"outlay (?:of )?(?:USD )?{N}"], text)
    op_cost = _num([r"operating cost (?:of )?(?:USD )?{N}", r"operating costs? (?:of )?(?:USD )?{N}"], text)
    inflation = _rate([r"cost-inflation (?:ratio|rate|of) (?:of )?{N}", r"cost inflation (?:ratio|rate|of) (?:of )?{N}",
                       r"inflation (?:ratio|rate|of) (?:of )?{N}"], text)
    cash = _num([r"available cash (?:of )?(?:USD )?{N}", r"cash available (?:of )?(?:USD )?{N}",
                 r"cash (?:on hand |balance )?(?:of )?(?:USD )?{N}"], text)
    threshold = _num([r"surplus of at least (?:USD )?{N}", r"at least (?:USD )?{N}"], text)

    one = Fraction(1)
    post_downturn = revenue * (one - downturn)            # checkpoint: revenue after the downturn
    inflated_cost = op_cost * (one + inflation)
    expansion_surplus = post_downturn * (one + recovery) - inflated_cost - outlay
    defensive_surplus = post_downturn - inflated_cost

    expansion_ok = (expansion_surplus >= threshold) and (cash >= outlay)
    defensive_ok = defensive_surplus >= threshold

    if expansion_ok:
        final = "expansion"
    elif defensive_ok:
        final = "defensive"
    else:
        final = "wait"

    return {"final": final, "slots": {"post_downturn_checkpoint": post_downturn}}
