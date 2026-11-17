"""h084: DFL from EBT with two fixed-rate debt tranches.

EBT is after deducting both tranches' interest; EBIT = EBT + I_A + I_B;
DFL = EBIT / EBT (a multiple).  Checkpoints: interest of tranche A, tranche B (USD).
"""
from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import F, NUMBER, grab

TEMPLATE_ID = "h084"


def _rate(raw: str, suffix: str) -> Fraction:
    r = F(raw)
    s = (suffix or "").strip().lower()
    if s.startswith("%") or s.startswith("percent"):
        r = r / 100
    return r


def _tranche(label: str, text: str) -> tuple[Fraction, Fraction]:
    rx = (
        rf"[Tt]ranche {label}\b[^.]*?(?:debt|principal|balance|borrowing)?[^.]*?"
        rf"(?:is|of|totals|equals)?\s*(?:USD\s*)?({NUMBER})\s*(?:USD)?[^.]*?"
        rf"\brate(?:\s+of|\s+is)?\s*({NUMBER})\s*(%|percent)?"
    )
    m = re.search(rx, text, flags=re.S)
    if m is None:
        raise ValueError(f"tranche {label} not found")
    principal = F(m.group(1))
    rate = _rate(m.group(2), m.group(3))
    return principal, rate


def solve(text: str, q: dict) -> dict:
    ebt = grab(r"earnings before tax (?:of|is|equal to|equals)?\s*(?:USD\s*)?{N}", text)
    pa, ra = _tranche("A", text)
    pb, rb = _tranche("B", text)
    ia = pa * ra
    ib = pb * rb
    ebit = ebt + ia + ib
    dfl = ebit / ebt
    return {
        "final": dfl,
        "slots": {
            "tranche_a_interest_checkpoint": ia,
            "tranche_b_interest_checkpoint": ib,
        },
    }
