"""h041 -- two-period loan: solve the second-period payment that hits a target ending balance.

Literal transcription of the question text:
  "A borrower starts with an outstanding principal of P0."
  "Two equal-length periods use the same effective rate of r, with interest applied
   before each end-of-period payment."
  "The borrower pays A1 at the end of the first period."
  "What exact second-period payment X, made at the end of the second period, leaves a
   balance of T immediately after that payment?"
  Target equality (unrounded exact payment):  (P0*(1+r) - A1)*(1+r) - X = T
"""

import re
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h041"


def _rate(text: str) -> Fraction:
    m = re.search(r"effective rate of (-?\d+(?:\.\d+)?(?:/\d+)?)\s*(percent|%)?", text)
    if m is None:
        r = grab(r"rate of {N}", text)
        return r
    r = Fraction(m.group(1))
    if m.group(2):
        r = r / 100
    return r


def solve(text: str, q: dict) -> dict:
    # Sentence 1: opening outstanding principal.
    p0 = grab(r"outstanding principal of (?:USD\s*)?\$?{N}", text)
    # Sentence 2: same effective per-period rate, interest accrues before each end-of-period payment.
    r = _rate(text)
    growth = 1 + r
    # Sentence 3: first-period payment at end of period 1.
    a1 = grab(r"pays (?:USD\s*)?\$?{N} at the end of the first period", text)
    # Sentence 4: target balance immediately after the second-period payment.
    target = grab(r"leaves a balance of (?:USD\s*)?\$?{N}", text)

    # Period 1: interest applied first, then the payment.
    interest1 = p0 * r
    balance_before_pay1 = p0 + interest1          # = p0 * (1 + r)
    balance1 = balance_before_pay1 - a1           # balance after first-period payment

    # Period 2: interest applied first, then the unknown payment X.
    balance_before_pay2 = balance1 * growth
    # Target equality: balance_before_pay2 - X = target  ->  X = balance_before_pay2 - target
    x = balance_before_pay2 - target

    return {
        "final": x,
        "slots": {"first_payment_balance_checkpoint": balance1},
    }
