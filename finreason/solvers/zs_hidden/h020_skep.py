"""h020 -- cooperation credit percentage that makes credited penalty + fixed interest = max total remedy.

Chain (all exact Fractions, no rounding inside the computation):
    cap        = max_total_remedy - fixed_interest          # "cap amount available for penalty" (USD)
    gain_pen   = realized_gain * multiplier
    base       = max(gain_pen, statutory_floor)             # "the greater of those two amounts"
    (1 - c) * base + fixed_interest = max_total_remedy  ->  c = 1 - cap / base
    final      = c * 100                                    # percent

AMBIGUITY RESOLUTIONS
1. "Cap amount available for penalty": the remedy is split into penalty + fixed interest and totals the maximum,
   so the amount the penalty may occupy is max_total_remedy - fixed_interest. Reported UNROUNDED in USD; the
   framework rounds half-up to 2 dp. The rounded checkpoint is never fed back into c.
2. "Greater of those two amounts": plain max(). A tie yields the same value either way, so no tie rule is needed.
3. Percent unit: the question asks for a "percentage"; answer_spec unit is percent, so final = c * 100 (ratio c
   itself is NOT returned).
4. The multiplier ("multiplied by 3") is parsed as a number, not assumed an integer, so 1.5 etc. also works.
5. No clamp is stated (no floor at 0, no cap at 100): c is the exact algebraic value that makes the equation hold,
   even if cap > base (negative c) or cap < 0. Sign is preserved as worded ("what ... makes ... equal").
6. "Fixed interest" is a flat USD amount (not a rate) -- "19 USD is fixed interest".
7. Base for the credit ratio: text says (1 - c) times the PRE-CREDIT amount (the max), not the gain penalty alone
   and not the cap.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h020"


def solve(text: str, q: dict) -> dict:
    max_total = grab(r"maximum total remedy is {N} USD", text)
    interest = grab(r"of which {N} USD is fixed interest", text)
    gain = grab(r"realized gain {N} USD multiplied by", text)
    mult = grab(r"realized gain (?:{N}) USD multiplied by {N}", text, group=2)
    floor = grab(r"statutory floor is {N} USD", text)

    cap = max_total - interest                 # USD available for the credited penalty
    gain_pen = gain * mult
    base = max(gain_pen, floor)                # pre-credit penalty base
    c = Fraction(1) - cap / base               # cooperation credit ratio
    final = c * 100                            # percent

    return {"final": final, "slots": {"penalty_cap_checkpoint": cap}}
