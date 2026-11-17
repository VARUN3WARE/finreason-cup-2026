"""h104: two financing scenarios screened by a WACC cap and a staged debt-ratio ceiling.

Structure (from the question text):
  * debt ratio = D / (D + E); its permitted ceiling starts at a stated value (1.00) and,
    at each of n sequential covenant stages, the remaining ceiling is reduced by the same
    fraction t  ->  ceiling after k stages = start * (1 - t)^k; final shared ceiling = (1 - t)^n.
  * WACC (percent) = E/V * cost_of_equity% + D/V * pre_tax_cost_of_debt% * (1 - tax_ratio).
  * A scenario qualifies only if WACC <= maximum permitted WACC (a maximum is inclusive) and
    D/(D+E) <= final ceiling (a ceiling is inclusive).
  * Among qualifying scenarios: lower exact WACC wins, Scenario A on an exact tie;
    `Neither scenario` when none qualifies.
Checkpoint: ceiling remaining after ONE covenant stage = start * (1 - t), unrounded.
"""

import re
from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "h104"

_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}


def _stage_count(text: str) -> int:
    m = re.search(r"each of (?:exactly )?(\w+) sequential covenant stages", text)
    n_word = None
    if m:
        tok = m.group(1).lower()
        n_word = int(tok) if tok.isdigit() else _WORDS.get(tok)
    m2 = re.search(r"\(1\s*-\s*t\)\s*\^\s*(\d+)", text)
    n_pow = int(m2.group(1)) if m2 else None
    if n_word is not None and n_pow is not None and n_word != n_pow:
        raise ValueError(f"stage count mismatch: {n_word} vs {n_pow}")
    n = n_word if n_word is not None else n_pow
    if n is None:
        raise ValueError("stage count not found")
    return n


def _scenario(label: str, text: str):
    e, d, ke, kd = grab_all(
        rf"Scenario {label} has equity value {{N}}, debt value {{N}}, "
        rf"cost of equity percentage {{N}}, and pre-tax cost of debt percentage {{N}}",
        text,
    )
    return e, d, ke, kd


def solve(text: str, q: dict) -> dict:
    tax = grab(r"corporate tax rate ratio {N}", text)              # ratio, e.g. 0.25
    wacc_max = grab(r"maximum permitted WACC percentage {N}", text)  # percent
    start = grab(r"permitted ceiling starts at {N}", text)          # 1.00
    t = grab(r"reduces the remaining ceiling by the same fraction t\s*=\s*{N}", text)
    n = _stage_count(text)

    one_stage_cap = start * (1 - t)
    final_cap = start * (1 - t) ** n

    results = {}
    for label in ("A", "B"):
        e, d, ke, kd = _scenario(label, text)
        v = e + d
        debt_ratio = d / v
        wacc = (e / v) * ke + (d / v) * kd * (1 - tax)   # percent
        qualifies = (wacc <= wacc_max) and (debt_ratio <= final_cap)
        results[label] = (qualifies, wacc)

    qa, wa = results["A"]
    qb, wb = results["B"]
    if qa and qb:
        final = "Scenario A" if wa <= wb else "Scenario B"
    elif qa:
        final = "Scenario A"
    elif qb:
        final = "Scenario B"
    else:
        final = "Neither scenario"

    return {
        "final": final,
        "slots": {"one_stage_debt_ratio_cap_checkpoint": Fraction(one_stage_cap)},
    }
