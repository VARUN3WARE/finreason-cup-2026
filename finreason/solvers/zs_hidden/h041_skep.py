"""h041 -- two-period loan: find the second payment that leaves a target balance.

Structure (all three instances):
    P0  = outstanding principal at time zero
    i   = per-period effective rate (given as a decimal ratio, e.g. 0.05)
    X1  = payment at the end of period 1
    T   = target balance immediately after the end-of-period-2 payment
    B1  = P0 * (1 + i) - X1            (interest first, then payment)   <- checkpoint
    X2  = B1 * (1 + i) - T             (unrounded exact payment)        <- final

AMBIGUITIES RESOLVED (skeptic pass):
 A1. Rate units: "effective rate of 0.05" is a bare decimal with no "percent" word, so it
     is a ratio (5%), NOT 0.05%. Sanity: as 0.05% the required second payment would be
     negative (986*1.0005 - 99 = 887.49 < 908.96), which is nonsensical. A "percent"/"%"
     suffix is still honoured (divide by 100) for robustness.
 A2. Order of operations within a period: "interest applied before each end-of-period
     payment" => balance accrues (1+i) first, THEN the payment is subtracted:
     B1 = P0*(1+i) - X1, not (P0 - X1)*(1+i). If a text instead says interest is applied
     "after" the payment, the ordering is flipped (detected from the wording).
 A3. Checkpoint quantity: "balance remaining after the first-period payment" is B1, the
     balance after BOTH the period-1 interest and the period-1 payment (not the pre-payment
     accrued balance, not the pre-interest principal). Unit = USD. Returned unrounded.
 A4. Intermediate rounding: "Define the target equality using the unrounded exact payment
     ... the displayed amount is a reporting approximation" => no cent-rounding of B1 before
     period 2, and X2 is returned exact; the framework rounds half-up to 2dp. Instance 1 lands
     exactly on 74.155 (a half-up boundary), so exact Fractions are essential here.
 A5. Per-period vs annual: "equal-length periods use the same effective rate" and no period
     length is stated, so the rate is already per period; no conversion.
 A6. Sign / floor: no floor-at-zero or "no payment required" wording, so X2 is returned as
     computed (sign preserved). All three instances give a positive X2 anyway.
 A7. The target balance is the balance "immediately after that payment" at the end of period
     2, so the equality is B1*(1+i) - X2 = T (no further interest after the payment).
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h041"

_CUR = r"(?:USD|usd|\$)?\s*"


def _rate(text: str) -> Fraction:
    """Per-period effective rate as a ratio; honour an explicit percent suffix."""
    m = re.search(
        rf"effective\s+(?:interest\s+)?rate\s+of\s+{_CUR}({NUMBER})\s*(percent|%)?",
        text,
        flags=re.S,
    )
    if m is None:
        m = re.search(rf"rate\s+(?:of|is|equals)\s+({NUMBER})\s*(percent|%)?", text, flags=re.S)
    if m is None:
        raise ValueError("rate not found")
    r = F(m.group(1))
    if m.group(2):
        r /= 100
    return r


def _interest_after_payment(text: str) -> bool:
    """True only if the text says interest is applied AFTER the payment (not our cluster)."""
    t = text.lower()
    if re.search(r"interest\s+(?:is\s+)?applied\s+after\s+each", t):
        return True
    if re.search(r"payment\s+(?:is\s+)?(?:made|applied|deducted)\s+before\s+(?:the\s+)?interest", t):
        return True
    return False


def solve(text: str, q: dict) -> dict:
    p0 = grab(rf"outstanding\s+principal\s+of\s+{_CUR}{{N}}", text)
    i = _rate(text)
    x1 = grab(rf"pays\s+{_CUR}{{N}}\s+at\s+the\s+end\s+of\s+the\s+first\s+period", text)
    target = grab(rf"leaves\s+a\s+balance\s+of\s+{_CUR}{{N}}\s+immediately\s+after", text)

    g = 1 + i
    if _interest_after_payment(text):
        b1 = (p0 - x1) * g            # payment first, then interest (not this cluster's wording)
        x2 = b1 - target / g          # (b1 - x2) * g = target
    else:
        b1 = p0 * g - x1              # interest first, then payment (A2)
        x2 = b1 * g - target          # b1 * g - x2 = target (A7)

    return {
        "final": x2,
        "slots": {"first_payment_balance_checkpoint": b1},
    }
