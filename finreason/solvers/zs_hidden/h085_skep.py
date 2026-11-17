"""h085 -- current loan vs refinance: signed second-period ending-balance difference.

AMBIGUITY HUNT (resolved from the text before coding):

A1. Rate units. "effective rate of 0.05" is a bare decimal with no "percent"/"%" label,
    and 0.05 is a sensible per-period rate, so it is a RATIO used directly (no /100).
    Guard: only if the number is immediately followed by "percent" or "%" is it divided
    by 100; as a last resort a bare value >= 1 (e.g. "rate of 5") is treated as percent
    because a 500% per-period loan rate is absurd.
A2. Rate basis. The problem is framed over "equal-length periods" with a payment "at each
    period end" and an "effective rate"; the rate is applied once per period with no
    annual/nominal conversion.
A3. Fee timing. "capitalizes a fee of F into its opening balance, THEN uses an effective
    rate" -> refinance opening balance = P + F, and interest in period 1 accrues on P + F.
    The fee belongs to the refinance only; the current loan starts at P.
A4. Interest vs payment order. "Interest accrues before each payment" -> each period:
    balance = balance * (1 + r) - payment (interest first, then payment). No interest is
    charged on the payment itself.
A5. Sign. "signed ... difference, current loan minus refinance" -> final = current_B2 -
    refinance_B2, possibly negative; no absolute value, no floor at zero for any balance.
A6. Rounding. Nothing says a rounded balance or payment is re-used, so every intermediate
    stays exact; the framework rounds the final and checkpoints half-up to 2 dp.
A7. Checkpoints. "balance after its first payment" = the end-of-period-1 balance (after
    interest AND after the payment), in USD, for the respective path. The refinance
    checkpoint includes the capitalized fee (it is part of the opening balance).
A8. Number of periods. Structure fixes "next two ... periods" and asks for the
    "second-period" ending balance; both are parsed (word -> int) with a fallback of 2
    so the horizon follows the text if an instance varied it.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h085"

# NUMBER has a top-level '|' alternation, so it must be grouped before embedding.
_NUM = f"(?:{NUMBER})"

_WORD_NUM = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}
_ORDINAL = {
    "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6,
    "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10, "eleventh": 11, "twelfth": 12,
}


def _rate(pattern: str, text: str) -> Fraction:
    """Grab a rate and convert to a ratio (A1)."""
    rx = pattern.replace("{N}", f"({NUMBER})")
    m = re.search(rx, text, flags=re.S)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    val = F(m.group(1))
    tail = text[m.end(1): m.end(1) + 12]
    if re.match(r"\s*(?:percent|%|pct)", tail, flags=re.I):
        return val / 100
    if val >= 1:
        return val / 100
    return val


def _count_periods(text: str) -> int:
    """A8: horizon from 'next two equal-length periods'; default 2."""
    m = re.search(r"next\s+(\w+)\s+(?:equal-length\s+)?periods", text, flags=re.I)
    if m:
        w = m.group(1).lower()
        if w in _WORD_NUM:
            return _WORD_NUM[w]
        if w.isdigit():
            return int(w)
    return 2


def _target_period(text: str, default: int) -> int:
    """A8: which period's ending balance is asked ('second-period'); default horizon."""
    m = re.search(r"(\w+)-period ending-balance", text, flags=re.I)
    if m:
        w = m.group(1).lower()
        if w in _ORDINAL:
            return _ORDINAL[w]
    m = re.search(r"period\s+(\d+)\s+ending", text, flags=re.I)
    if m:
        return int(m.group(1))
    return default


def _roll(balance: Fraction, rate: Fraction, payment: Fraction, periods: int) -> list[Fraction]:
    """A4: per period, interest accrues first, then the payment is subtracted.
    Returns the ending balance after each period (index 0 = after first payment)."""
    out = []
    b = balance
    for _ in range(periods):
        b = b * (1 + rate) - payment
        out.append(b)
    return out


def solve(text: str, q: dict) -> dict:
    # Opening principal, shared by both paths.
    principal = grab(r"outstanding principal of\s*(?:USD\s*)?{N}", text)

    # Split the text at the refinance clause so each path's numbers are read only
    # from its own sentence (the two sentences share identical wording otherwise).
    refi_at = re.search(r"refinance capitalizes", text, flags=re.I)
    if refi_at is None:
        raise ValueError("refinance clause not found")
    cur_text = text[: refi_at.start()]
    ref_text = text[refi_at.start():]

    # Current loan: rate and payment (A1, A2).
    r_cur = _rate(r"current loan uses an effective rate of\s*{N}", cur_text)
    cur_block = re.search(
        r"current loan uses an effective rate of\s*" + _NUM + r"(?:\s*(?:percent|%|pct))?"
        r"\s*and a payment of\s*(?:USD\s*)?(" + _NUM + ")",
        cur_text, flags=re.S | re.I,
    )
    if cur_block is None:
        raise ValueError("current-loan payment not found")
    pay_cur = F(cur_block.group(1))

    # Refinance: capitalized fee, rate and payment (A1, A3).
    fee = grab(r"capitalizes a fee of\s*(?:USD\s*)?{N}", ref_text)
    r_ref = _rate(r"then uses an effective rate of\s*{N}", ref_text)
    ref_block = re.search(
        r"then uses an effective rate of\s*" + _NUM + r"(?:\s*(?:percent|%|pct))?"
        r"\s*and a payment of\s*(?:USD\s*)?(" + _NUM + ")",
        ref_text, flags=re.S | re.I,
    )
    if ref_block is None:
        raise ValueError("refinance payment not found")
    pay_ref = F(ref_block.group(1))

    n_periods = _count_periods(text)
    target = _target_period(text, n_periods)
    horizon = max(n_periods, target)

    cur_path = _roll(principal, r_cur, pay_cur, horizon)            # starts at P
    ref_path = _roll(principal + fee, r_ref, pay_ref, horizon)      # starts at P + fee (A3)

    cur_first = cur_path[0]                 # A7: after first payment
    ref_first = ref_path[0]                 # A7: after first payment, fee included
    final = cur_path[target - 1] - ref_path[target - 1]   # A5: signed, current minus refi

    return {
        "final": final,
        "slots": {
            "current_first_payment_balance_checkpoint": cur_first,
            "refinance_first_payment_balance_checkpoint": ref_first,
        },
    }
