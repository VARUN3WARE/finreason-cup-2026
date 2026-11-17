"""h077 -- minimum opening cash satisfying two sequential period-end cash floors.

Structure (all three instances):
    opening cash C (unknown) -> period one: inflow I1, outflow O1 -> period two: inflow I2, outflow O2.
    Every flow occurs before its period end; only the two period-end balances are tested against one
    common floor L ("Each period-end cash balance must be at least L").

    end-of-period-one balance : C + (I1 - O1)                 >= L   ->  C >= L - N1
    end-of-period-two balance : C + (I1 - O1) + (I2 - O2)     >= L   ->  C >= L - N1 - N2
    minimum C = max(L - N1, L - N1 - N2)      (N1 = I1 - O1, N2 = I2 - O2)

AMBIGUITY HUNT -- points where analysts could diverge, and the textual resolution used:
  1. Which balances are tested?  "only period-end balances are tested ... no intraperiod liquidity
     requirements" -> exactly two constraints (end of P1, end of P2); no intraperiod minimum, no test of the
     opening balance itself.
  2. Is the floor the same for both periods?  "Each period-end cash balance must be at least L" -> one
     common floor L applied to both period ends.
  3. Strict vs non-strict?  "at least" -> non-strict (>=), so the minimum is attained exactly at the
     binding bound (no epsilon / no supremum issue).
  4. Does period two's net flow help or hurt?  N2 may be positive (P2 bound slacker than P1 bound) or
     negative (P2 bound tighter).  Both bounds are computed and the max taken -- branch resolves per
     instance from the numbers, not assumed.
  5. Sign of period-one net flow: N1 = I1 - O1, sign preserved (could be negative if outflow > inflow);
     the checkpoint ratio keeps that sign.
  6. Interest / timing / other flows: text says none -> plain sums, no discounting.
  7. Non-negativity of opening cash: a negative "minimum opening cash" is not cash; the result is floored
     at zero.  Does NOT bind on any of the three instances (all bounds are well above zero), so this
     choice cannot change any answer here.
  8. Rounding: "use exact arithmetic and round only the final answer" -> no intermediate rounding; the
     framework rounds the final (2 dp half-up, usd_million) and the checkpoint (6 dp half-up, ratio).
  9. Checkpoint "period-one net cash flow as a fraction of the required cash floor": net cash flow is a
     FLOW (inflow minus outflow), not the end-of-period balance and not including opening cash;
     "fraction of the required cash floor" -> (I1 - O1) / L as a plain ratio (not percent).
 10. Units: all amounts are already in USD millions, so the final is returned as-is in usd_million.

Number parsing is anchored on the sentence that starts with "Period one" / "Period two" and the words
"inflow" / "outflow" inside that sentence, so insertions like "of" or "USD" would not break it.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER_RE, F, grab

TEMPLATE_ID = "h077"


def _period_sentence(text: str, words: tuple[str, ...]) -> str:
    """The sentence that introduces the named period (e.g. 'Period one has ...')."""
    for w in words:
        m = re.search(rf"\bPeriod\s+{w}\b[^.]*?(?:inflow|outflow)[^\n]*?(?:\.\s|\.$|\n|$)", text, flags=re.S | re.I)
        if m:
            return m.group(0)
    raise ValueError(f"period sentence not found for {words!r}")


def _flow(sentence: str, kind: str) -> Fraction:
    """First number following the word `kind` ('inflow' / 'outflow') in the sentence."""
    m = re.search(rf"{kind}s?\b\s*(?:of\s*)?(?:USD\s*)?(?:\$\s*)?", sentence, flags=re.I)
    if m is None:
        raise ValueError(f"'{kind}' not found in {sentence!r}")
    n = NUMBER_RE.search(sentence, m.end())
    if n is None:
        raise ValueError(f"no number after '{kind}' in {sentence!r}")
    return F(n.group(0))


def solve(text: str, q: dict) -> dict:
    s1 = _period_sentence(text, ("one", "1", "I"))
    s2 = _period_sentence(text, ("two", "2", "II"))

    i1 = _flow(s1, "inflow")
    o1 = _flow(s1, "outflow")
    i2 = _flow(s2, "inflow")
    o2 = _flow(s2, "outflow")

    # Required period-end cash floor (one common floor for both period ends).
    floor = grab(
        r"(?:at least|no less than|not less than|a minimum of|or more than|minimum of)\s*(?:USD\s*)?(?:\$\s*)?{N}",
        text,
    )

    n1 = i1 - o1            # period-one net cash flow (sign preserved)
    n2 = i2 - o2            # period-two net cash flow (sign preserved)

    bound_p1 = floor - n1          # C >= L - N1
    bound_p2 = floor - n1 - n2     # C >= L - N1 - N2
    min_opening = max(bound_p1, bound_p2)
    min_opening = max(min_opening, Fraction(0))   # cash cannot be negative (non-binding here)

    ratio = n1 / floor             # period-one net cash flow as a fraction of the floor (plain ratio)

    return {
        "final": min_opening,
        "slots": {"period_one_net_to_floor_ratio_checkpoint": ratio},
    }
