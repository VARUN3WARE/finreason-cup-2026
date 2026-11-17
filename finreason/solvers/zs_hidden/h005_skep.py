"""h005 -- carbon-credit break-even price vs. internal abatement (skeptical analyst).

Structure (all 3 instances):
    "Treat one carbon credit as covering one ton of CO2e. A company has internal abatement
     capacity C tons of CO2e and commits to utilization u. Mobilizing internal abatement costs
     FIX USD, plus VAR USD for each ton internally abated. Compute the carbon-credit price in USD
     per ton of CO2e at which buying credits for the same planned abatement quantity costs exactly
     as much as internal abatement."

AMBIGUITY HUNT -- points where analysts could disagree, and the resolution with textual evidence:

A1. Utilization: ratio vs percent.
    Text: "commits to utilization 0.5" / "0.4" -- bare numbers, no "percent" word, values in (0, 1].
    => Treat as a plain ratio. Defensive: if the word "percent" immediately follows the number,
       divide by 100 (does not fire on these instances).

A2. What is the "planned abatement quantity"? Full capacity C, or C * u?
    Text: capacity is a ceiling the company *has*; it "commits to utilization u" -- the plan is to
    use fraction u of the capacity. The slot is described as "the internally planned reduction
    quantity" in tons_co2e, which is the committed plan, not the ceiling.
    => Q = C * u.

A3. Whole-ton / whole-credit rounding of Q?
    Text: "Treat one carbon credit as covering one ton of CO2e" only fixes the 1:1 credit/ton
    mapping; nothing says credits are bought in whole units or that abatement is in whole tons.
    The slot spec rounds to 4 dp (instance 2: 203.1601 * 0.5 = 101.58005 -> fractional), which
    only makes sense if Q may be fractional. "same planned abatement quantity" => credits = Q exactly.
    => No rounding anywhere inside the computation.

A4. To which base does the variable cost apply -- capacity C or planned Q?
    Text: "plus VAR USD for each ton internally abated" -- tons actually abated under the plan = Q.
    => Internal cost = FIX + VAR * Q.

A5. Is FIX a lump sum independent of quantity?
    Text: "Mobilizing internal abatement costs FIX USD, plus ..." -- a one-off mobilization cost,
    then a per-ton add-on. => Yes, FIX is fixed.

A6. Break-even definition.
    Text: "price ... at which buying credits for the same planned abatement quantity costs exactly
    as much as internal abatement" => P * Q = FIX + VAR * Q  =>  P = (FIX + VAR * Q) / Q.
    Unit: USD per ton of CO2e (one credit = one ton, so USD per credit == USD per ton).
    Returned unrounded; framework rounds half-up to 2 dp.

A7. Edge: Q == 0 would make the break-even undefined -- not present in any instance; raise.

Checkpoint:
    planned_abatement_checkpoint = Q = C * u  (tons CO2e, unrounded; framework rounds 4 dp half-up)
Final:
    P = (FIX + VAR * Q) / Q   (USD per ton CO2e, unrounded; framework rounds 2 dp half-up)
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h005"


def _utilization(text: str) -> Fraction:
    """Utilization as a ratio. Bare number => ratio; number followed by 'percent' => /100."""
    m = re.search(rf"utilization\s*(?:of\s*)?({NUMBER})(\s*(?:percent|%))?", text, flags=re.S | re.I)
    if m is None:
        raise ValueError("utilization not found")
    u = F(m.group(1))
    if m.group(2):
        u = u / 100
    return u


def solve(text: str, q: dict) -> dict:
    capacity = grab(r"internal abatement capacity\s*{N}\s*tons", text)
    util = _utilization(text)
    fixed = grab(r"Mobilizing internal abatement costs\s*{N}\s*USD", text)
    var = grab(r"plus\s*{N}\s*USD for each ton internally abated", text)

    # A2/A3: planned quantity = capacity * utilization, exact, no whole-unit rounding.
    planned = capacity * util
    if planned == 0:
        raise ValueError("planned abatement quantity is zero; break-even price undefined")

    # A4/A5: internal cost = lump-sum mobilization + per-ton cost on planned tons.
    internal_cost = fixed + var * planned

    # A6: credits needed = planned tons (1 credit = 1 ton); P * planned = internal_cost.
    price = internal_cost / planned

    return {
        "final": price,
        "slots": {"planned_abatement_checkpoint": planned},
    }
