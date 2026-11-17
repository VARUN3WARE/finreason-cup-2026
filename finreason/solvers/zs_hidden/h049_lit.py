"""h049 -- layered multiplicative tolerance envelope assurance gate (literal transcription).

Sentence by sentence:
 1. reported/audited energy savings and reported/audited waste-management savings.
 2. per-layer tolerance ratio t applies at exactly K sequential multiplicative layers.
 3. each layer: lower *= (1 - t), upper *= (1 + t); audited compared ONCE against the final
    inclusive envelope [reported*(1-t)^K, reported*(1+t)^K].
 4. audit coverage C must reach (>=) threshold; boolean flag must be true (completed engagement
    covered both metrics and issued an unmodified conclusion).
 5. assured only when every condition holds; otherwise review_required.

Checkpoint: lower_stage_factor_checkpoint = the one-layer lower tolerance factor = 1 - t (unrounded).
"""

import re
from fractions import Fraction

from finreason.nums import grab, NUMBER

TEMPLATE_ID = "h049"

_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}


def _layer_count(text: str) -> int:
    m = re.search(r"exactly\s+(\w+)\s+sequential", text)
    if m:
        tok = m.group(1).lower()
        if tok in _WORDS:
            return _WORDS[tok]
        if tok.isdigit():
            return int(tok)
    m = re.search(r"\(1-t\)\^(\d+)", text)
    if m:
        return int(m.group(1))
    raise ValueError("layer count not found")


def solve(text: str, q: dict) -> dict:
    # Sentence 1: the two metric pairs.
    rep_energy = grab(r"reported energy savings {N}", text)
    aud_energy = grab(r"audited energy savings {N}", text)
    rep_waste = grab(r"reported waste-management savings {N}", text)
    aud_waste = grab(r"audited waste-management savings {N}", text)

    # Sentence 2: per-layer tolerance ratio and number of layers.
    t = grab(r"per-layer tolerance ratio {N}", text)
    k = _layer_count(text)

    # Sentence 3: layer-by-layer envelope, applied sequentially from the reported amount.
    lower_factor = 1 - t          # one-layer lower tolerance factor
    upper_factor = 1 + t          # one-layer upper tolerance factor

    def envelope(reported: Fraction):
        lo = reported
        hi = reported
        for _ in range(k):
            lo = lo * lower_factor
            hi = hi * upper_factor
        return lo, hi

    e_lo, e_hi = envelope(rep_energy)
    w_lo, w_hi = envelope(rep_waste)
    # final inclusive envelope: lower <= audited <= upper (envelope ordered just in case)
    energy_ok = min(e_lo, e_hi) <= aud_energy <= max(e_lo, e_hi)
    waste_ok = min(w_lo, w_hi) <= aud_waste <= max(w_lo, w_hi)

    # Sentence 4: coverage must reach threshold; boolean flag must be true.
    m = re.search(r"[Aa]udit coverage (" + NUMBER + r") must reach (" + NUMBER + r")", text)
    if m:
        coverage = Fraction(m.group(1).replace(",", ""))
        cov_min = Fraction(m.group(2).replace(",", ""))
    else:
        coverage = grab(r"[Aa]udit coverage {N}", text)
        cov_min = grab(r"must reach {N}", text)
    coverage_ok = coverage >= cov_min

    fm = re.search(r"\b(true|false|True|False)\s+indicates that", text)
    if fm is None:
        raise ValueError("engagement flag not found")
    flag_ok = fm.group(1).lower() == "true"

    # Sentence 5: assured only when every condition holds.
    final = "assured" if (energy_ok and waste_ok and coverage_ok and flag_ok) else "review_required"

    return {
        "final": final,
        "slots": {"lower_stage_factor_checkpoint": lower_factor},
    }
