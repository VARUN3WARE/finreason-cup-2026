"""h094 -- one Newton-Raphson step on a two-year NPV, starting from a trial rate.

AMBIGUITY HUNT (resolved from the text before coding):

A1. Sign convention of the NPV.
    "requires an initial outlay of C0 at time 0, pays C1 at the end of year 1, and pays
    C2 at the end of year 2"  ->  NPV(r) = -C0 + C1/(1+r) + C2/(1+r)^2.
    The text's own guarantee "the trial NPV is guaranteed to be positive" is consistent
    with this sign on all three instances (checked: +21.37, +68.65, +25.08), so the
    outlay is a negative time-0 flow and the receipts are positive.

A2. Is the trial rate 0.1 a ratio or a percent?
    "annual effective trial rate 0.1" -- an annual effective rate written as a plain
    decimal is a ratio (10%), not 0.1%.  Used as r0 = 1/10 exactly.  The final answer is
    requested "as an annual percentage", so only the OUTPUT is scaled by 100.

A3. Derivative with respect to what?
    "the NPV derivative" with the NPV evaluated at the "trial rate" -> dNPV/dr at r0,
    i.e. NPV'(r) = -C1/(1+r)^2 - 2*C2/(1+r)^3  (negative for positive receipts).
    Not the derivative w.r.t. the discount factor v = 1/(1+r); the iteration variable is
    the rate itself ("Report the updated trial rate").

A4. "using the positive magnitude of the NPV derivative" + "the update moves upward".
    Standard Newton: r1 = r0 - NPV(r0)/NPV'(r0).  With NPV'(r0) < 0 this is
    r1 = r0 + NPV(r0)/|NPV'(r0)|, which is exactly the wording (positive magnitude in the
    denominator, movement upward).  Both forms are algebraically identical here, so
    there is no real fork; implemented as r0 + NPV/|NPV'|.

A5. Exactly one update, no clipping.
    "perform exactly one Newton-Raphson update ... Do not iterate again" -> a single step.
    "while remaining below the unique economic IRR" is a guarantee, not an instruction to
    cap the result (and for a convex decreasing NPV a Newton step from the left of the
    root can never overshoot the root, so no cap is ever needed).

A6. Checkpoint "present value of the year-2 cash flow at the trial rate" (unit usd, 4dp).
    Position 1 in the chain = part of "evaluate the exact two-year NPV", i.e. BEFORE the
    update, so "the trial rate" is the starting rate r0 = 0.1, not the updated rate.
    Value = C2/(1+r0)^2, un-netted (just the year-2 term, not NPV, not the year-1 term).

A7. Rounding.  Everything is exact Fraction; the framework rounds the final (percent,
    2dp half-up) and the checkpoint (usd, 4dp half-up).  Nothing in the text says a
    rounded intermediate feeds a later step, so no internal rounding.

A8. Number formats.  Amounts may be decimals or rationals ("3035/11"); the {N} capture of
    finreason.nums handles both.  Regexes are anchored on the surrounding words
    ("initial outlay of", "end of year 1", "end of year 2", "trial rate").
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h094"


def solve(text: str, q: dict) -> dict:
    # --- parse (anchored on the surrounding words; decimals or rationals) ---
    c0 = grab(r"initial outlay of (?:USD\s*)?{N}\s+at time (?:0|zero)", text)
    c1 = grab(r"pays (?:USD\s*)?{N}\s+at the end of year 1\b", text)
    c2 = grab(r"pays (?:USD\s*)?{N}\s+at the end of year 2\b", text)
    r0 = grab(r"trial rate (?:of )?{N}", text)  # A2: plain ratio (0.1 == 10%)

    one_plus = 1 + r0  # Fraction

    # --- exact two-year NPV at the trial rate (A1) ---
    pv1 = c1 / one_plus
    pv2 = c2 / one_plus**2  # A6: checkpoint = PV of the year-2 flow at r0
    npv = -c0 + pv1 + pv2

    # --- derivative of NPV with respect to the rate, positive magnitude (A3, A4) ---
    # NPV'(r) = -C1/(1+r)^2 - 2*C2/(1+r)^3  ->  |NPV'(r0)| = C1/(1+r0)^2 + 2*C2/(1+r0)^3
    abs_deriv = c1 / one_plus**2 + 2 * c2 / one_plus**3

    # --- exactly one Newton-Raphson update, moving upward (A4, A5) ---
    r1 = r0 + npv / abs_deriv

    return {
        "final": r1 * 100,  # A2: reported as an annual percentage
        "slots": {
            "year_two_present_value_checkpoint": pv2,
        },
    }
