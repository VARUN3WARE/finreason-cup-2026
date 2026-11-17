"""h084 -- DFL from EBT with two fixed-interest debt tranches (literal transcription)."""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F

TEMPLATE_ID = "h084"


def _rate(raw: str, pct_word: str | None) -> Fraction:
    r = F(raw)
    if pct_word:  # "rate 10 percent" / "rate 10%" -> ratio
        r = r / 100
    return r


def _tranche(name: str, text: str) -> tuple[Fraction, Fraction]:
    rx = (
        rf"Tranche {name} debt is (?:USD )?({NUMBER})(?: USD)? at (?:an? )?(?:annual )?(?:interest )?rate (?:of )?"
        rf"({NUMBER})\s*(percent|%)?"
    )
    m = re.search(rx, text, flags=re.S | re.I)
    if m is None:
        raise ValueError(f"tranche {name} not found")
    return F(m.group(1)), _rate(m.group(2), m.group(3))


def solve(text: str, q: dict) -> dict:
    # "a company has positive earnings before tax of 5137 USD after deducting all modeled interest expense"
    m = re.search(rf"earnings before tax of (?:USD )?({NUMBER})", text, flags=re.S | re.I)
    if m is None:
        raise ValueError("EBT not found")
    ebt = F(m.group(1))

    # "Tranche A debt is X USD at rate r_A, and tranche B debt is Y USD at rate r_B."
    debt_a, rate_a = _tranche("A", text)
    debt_b, rate_b = _tranche("B", text)

    # "All amounts and rates use the same period." -> period interest = debt * rate (fixed-interest model)
    interest_a = debt_a * rate_a
    interest_b = debt_b * rate_b

    # "reconstruct EBIT by adding both interest expenses back to earnings before tax"
    ebit = ebt + interest_a + interest_b

    # "compute degree of financial leverage as EBIT divided by earnings before tax"
    dfl = ebit / ebt

    return {
        "final": dfl,
        "slots": {
            "tranche_a_interest_checkpoint": interest_a,
            "tranche_b_interest_checkpoint": interest_b,
        },
    }
