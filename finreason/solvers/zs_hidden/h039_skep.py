"""h039 -- minimum equity injection to bring debt-to-equity down to a permitted ceiling.

Structure (all 3 instances):
    current debt D0, current equity E0 (USD millions);
    planned additional borrowing B and debt repayment R (USD millions);
    permitted debt-to-equity ceiling c (plain ratio, e.g. 1);
    find the minimum new equity injection X so that (D0 + B - R) / (E0 + X) == c.

AMBIGUITIES CONSIDERED AND RESOLVED
-----------------------------------
A1. Checkpoint "debt immediately after the planned borrowing and before repayment":
    D0 + B exactly (NOT net of the repayment).  Unit = usd_million, same as the inputs
    ("report the injection ... in USD millions" -> every money figure is in USD millions).
A2. Which actions touch which side of the ratio: both borrowing and repayment are
    *debt* actions ("after both debt actions"); nothing in the text says the repayment is
    funded from equity or that borrowing changes equity, so equity stays E0 until the
    injection.  Final debt D1 = D0 + B - R (order of the two actions is irrelevant for D1).
A3. Ceiling unit: "debt-to-equity ratio equals the permitted ceiling 1" -> plain ratio.
    Defensive parse: if the number is immediately followed by "percent"/"%", divide by 100.
A4. Ratio equation: D1 / (E0 + X) = c  ->  X = D1 / c - E0.  "Use full precision for the
    ratio equation": no intermediate rounding; the framework rounds the final half-up to 2dp.
A5. "Minimum ... required": an injection cannot be negative.  If D1 / c - E0 < 0 the ratio is
    already below the ceiling and the minimum required injection is 0.  (Does not bind on
    any of the three instances -- all three give a strictly positive X -- so this choice is
    harmless here; "equals the ceiling" and "minimum required" coincide when X > 0.)
A6. Sign/tie rules: none needed; the half-up rendering is done by the framework on the
    exact Fraction value (e.g. 91.0245 -> 91.02 is the framework's job, not ours).
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h039"


def _ceiling(text: str) -> Fraction:
    """Permitted debt-to-equity ceiling as a plain ratio."""
    m = re.search(
        r"permitted\s+ceiling(?:\s+of)?\s+(?:is\s+)?(" + NUMBER + r")\s*(percent|%)?",
        text,
        flags=re.S | re.I,
    )
    if m is None:
        # fallback wording: "ceiling of X" / "ceiling X"
        m = re.search(r"ceiling(?:\s+of)?\s+(?:is\s+)?(" + NUMBER + r")\s*(percent|%)?", text, flags=re.S | re.I)
    if m is None:
        raise ValueError("permitted ceiling not found")
    c = F(m.group(1))
    if m.group(2):
        c = c / 100
    return c


def solve(text: str, q: dict) -> dict:
    d0 = grab(r"current debt of (?:USD )?{N}", text)
    e0 = grab(r"current equity of (?:USD )?{N}", text)
    borrow = grab(r"additional borrowing of (?:USD )?{N}", text)
    repay = grab(r"debt repayment of (?:USD )?{N}", text)
    c = _ceiling(text)

    # Checkpoint: debt right after borrowing, before repayment.
    debt_after_borrowing = d0 + borrow

    # Final debt after both actions.
    debt_final = debt_after_borrowing - repay

    # Required equity so that debt / equity == ceiling, then the injection on top of E0.
    required_equity = debt_final / c
    injection = required_equity - e0
    if injection < 0:
        injection = Fraction(0)  # A5: minimum injection required cannot be negative

    return {
        "final": injection,
        "slots": {"debt_after_borrowing_checkpoint": debt_after_borrowing},
    }
