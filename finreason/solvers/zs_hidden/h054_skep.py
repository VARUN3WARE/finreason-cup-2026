"""h054 -- quick-ratio convexity premium from a two-state inventory sale.

AMBIGUITY RESOLUTIONS (skeptical pass):

A1. "Retained cash in the low-recovery state" (slot 1): the text defines retained
    cash as "fraction f of net proceeds remains as cash in quick assets". So the
    checkpoint is f * r_low * INV -- the cash retained FROM THE SALE -- not the
    total post-sale quick assets (QA0 + f*r_low*INV). Slot 2 ("high-state
    increment in retained cash") only makes sense on the same base:
    f*r_high*INV - f*r_low*INV = f*spread*INV. Slot 3 is the complementary
    (1-f)*spread*INV increment in repayment.
A2. Net proceeds = recovery_rate * inventory carrying amount. "net-recovery
    states" / "net proceeds" / "recovery rate" all point to rate x carrying amount.
A3. High rate is ADDITIVE: r_high = r_low + spread ("that low rate plus positive
    spread"; "generated cases keep their sum below one" confirms addition).
A4. Pre-sale liabilities are implied from the high-state remainder:
    L0 = L_high_remaining + (1-f) * r_high * INV. The same L0 applies in the low
    state, so L_low = L0 - (1-f)*r_low*INV = L_high_remaining + (1-f)*spread*INV.
A5. Repayment "at par": liabilities fall by exactly the cash paid.
A6. Post-sale quick ratio in state s = (QA0 + f*r_s*INV) / (L0 - (1-f)*r_s*INV).
    Inventory is excluded from quick assets both before and after (it is sold
    anyway), so no inventory term enters the numerator.
A7. "probability-weighted average of the two state quick ratios" = p*QR_H +
    (1-p)*QR_L (expectation of ratios). "quick ratio formed from
    probability-weighted post-sale quick assets and liabilities" = E[QA]/E[L]
    (ratio of expectations). Gap = E[QR] - E[QA]/E[L] (the first minus the
    second, per "subtract [ratio-of-expectations] from [average of ratios]").
    By Jensen this is positive, matching "positive expectation-order gap".
A8. Low-state probability = 1 - p (two mutually exclusive states).
A9. "percentage-point equivalent" of a ratio gap = gap * 100; answer unit is
    percent, so return gap*100 unrounded.
A10. No intermediate rounding anywhere; every value is exact Fraction and the
    framework applies half-up rounding to each result_spec independently.
A11. Rates/fractions/probabilities are given as plain decimals (0.4, 0.5, ...).
    Defensive: if a captured value is immediately followed by "percent" or "%",
    it is divided by 100.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h054"


def _rate(pattern: str, text: str) -> Fraction:
    """Grab a number with {N}; if the match is followed by 'percent'/'%', scale."""
    rx = pattern.replace("{N}", f"({NUMBER})")
    m = re.search(rx, text, flags=re.S | re.I)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    val = F(m.group(1))
    tail = text[m.end(1): m.end(1) + 12]
    if re.match(r"\s*(?:percent|%)", tail, flags=re.I):
        val = val / 100
    return val


def solve(text: str, q: dict) -> dict:
    # --- inputs -------------------------------------------------------------
    qa0 = grab(r"[Qq]uick assets before the sale[^.]*?are\s+(?:USD\s+)?{N}", text)
    inv = grab(r"inventory carrying amount\s+(?:of\s+)?(?:USD\s+)?{N}", text)
    f_keep = _rate(r"fraction\s+{N}\s+of (?:the )?net proceeds remains", text)
    r_low = _rate(r"low recovery rate is\s+{N}", text)
    spread = _rate(r"plus (?:a )?positive spread(?: of)?\s+{N}", text)
    p_high = _rate(r"high state occurs with probability\s+{N}", text)
    l_high_rem = grab(
        r"scenario gives\s+(?:USD\s+)?{N}\s*(?:USD)?,\s*the liabilities remaining after high-state repayment",
        text,
    )

    r_high = r_low + spread
    f_repay = 1 - f_keep
    p_low = 1 - p_high

    # --- state cash flows ---------------------------------------------------
    proceeds_low = r_low * inv
    proceeds_high = r_high * inv

    cash_low = f_keep * proceeds_low            # slot 1
    cash_high = f_keep * proceeds_high
    repay_low = f_repay * proceeds_low
    repay_high = f_repay * proceeds_high

    incr_cash = cash_high - cash_low            # slot 2  (= f*spread*INV)
    incr_repay = repay_high - repay_low         # slot 3  (= (1-f)*spread*INV)

    # --- implied pre-sale liabilities (A4) ----------------------------------
    l0 = l_high_rem + repay_high

    qa_low = qa0 + cash_low
    qa_high = qa0 + cash_high
    l_low = l0 - repay_low
    l_high = l0 - repay_high                    # == l_high_rem

    qr_low = qa_low / l_low
    qr_high = qa_high / l_high

    # --- expectation-order gap (A7) ----------------------------------------
    e_qr = p_high * qr_high + p_low * qr_low
    e_qa = p_high * qa_high + p_low * qa_low
    e_l = p_high * l_high + p_low * l_low
    qr_of_e = e_qa / e_l

    gap = e_qr - qr_of_e
    final_pct = gap * 100                       # percentage points (A9)

    return {
        "final": final_pct,
        "slots": {
            "low_state_retained_cash_checkpoint": cash_low,
            "incremental_retained_cash_checkpoint": incr_cash,
            "incremental_repayment_checkpoint": incr_repay,
        },
    }
