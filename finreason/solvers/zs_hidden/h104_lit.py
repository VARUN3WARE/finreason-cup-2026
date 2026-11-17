"""h104 -- two financing scenarios screened by a WACC cap and a staged debt-ratio ceiling.

Literal transcription of the question, sentence by sentence:

 S1 "Compare two financing scenarios using corporate tax rate ratio {tax} and maximum permitted
     WACC percentage {wacc_max}."
 S2 "Under this scenario's internal leverage covenant, debt ratio means debt divided by debt plus
     equity, D/(D+E), and its permitted ceiling starts at {start}."
 S3 "At each of exactly {three} sequential covenant stages the company reduces the remaining
     ceiling by the same fraction t={t}, so the final shared ceiling is (1-t)^3."
 S4 "This is a scenario-specific financing policy, not a general regulatory rule."  (no numbers)
 S5 "Scenario A has equity value {E}, debt value {D}, cost of equity percentage {re}, and pre-tax
     cost of debt percentage {rd}."
 S6 same for Scenario B.
 S7 "A scenario qualifies only if both its exact WACC and D/(D+E) debt ratio satisfy their limits."
     -> WACC <= maximum permitted WACC (a maximum that is permitted), and
        D/(D+E) <= final shared ceiling (a permitted ceiling).
 S8 "among qualifying scenarios return the one with lower exact WACC, choose `Scenario A` on an
     exact tie, and return `Neither scenario` when neither qualifies."

WACC (after-tax, percent) = E/(D+E) * cost_of_equity% + D/(D+E) * pre_tax_cost_of_debt% * (1 - tax).

Checkpoint one_stage_debt_ratio_cap_checkpoint = ceiling remaining after ONE covenant stage
  = start * (1 - t)   (ratio, unrounded; the framework rounds half-up to 6 dp).
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h104"

_WORD_INT = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}


def _count(token: str) -> int:
    token = token.strip().lower()
    if token.isdigit():
        return int(token)
    return _WORD_INT[token]


def _scenario_sentence(text: str, label: str) -> str:
    """The body of the sentence 'Scenario <label> has ... .' (decimal points never precede a space)."""
    m = re.search(rf"Scenario {label} has (.*?)(?:\.\s|\.$|$)", text, flags=re.S)
    if m is None:
        raise ValueError(f"scenario {label} sentence not found")
    return m.group(1)


def _scenario(text: str, label: str) -> dict:
    s = _scenario_sentence(text, label)
    return {
        "E": grab(r"equity value {N}", s),
        "D": grab(r"debt value {N}", s),
        "re_pct": grab(r"cost of equity percentage {N}", s),
        "rd_pct": grab(r"pre-tax cost of debt percentage {N}", s),
    }


def solve(text: str, q: dict) -> dict:
    # S1: corporate tax rate (given as a ratio) and maximum permitted WACC (given in percent).
    m_tax_pct = re.search(r"corporate tax rate percentage", text)
    if m_tax_pct:
        tax = grab(r"corporate tax rate percentage {N}", text) / 100
    else:
        tax = grab(r"corporate tax rate ratio {N}", text)
    wacc_max_pct = grab(r"maximum permitted WACC percentage {N}", text)

    # S2: debt ratio = D/(D+E); permitted ceiling starts at `start`.
    start = grab(r"permitted ceiling starts at {N}", text)

    # S3: exactly n sequential stages, each reduces the REMAINING ceiling by the same fraction t.
    m_n = re.search(r"exactly (\w+) sequential covenant stages", text)
    n_stages = _count(m_n.group(1)) if m_n else 3
    t = grab(r"same fraction t\s*=\s*{N}", text)
    m_exp = re.search(r"final shared ceiling is \(1\s*-\s*t\)\^(\d+)", text)
    if m_exp:
        # the explicit formula for the final shared ceiling governs the stage count
        n_stages = int(m_exp.group(1))

    ceiling = start
    stage_ceilings = []
    for _ in range(n_stages):
        ceiling = ceiling * (1 - t)  # remaining ceiling reduced by fraction t
        stage_ceilings.append(ceiling)
    one_stage_ceiling = start * (1 - t)  # ceiling remaining after one covenant stage
    final_shared_ceiling = ceiling  # = start * (1-t)^n  (= (1-t)^3 with start 1.00)

    # S5/S6: scenario inputs.
    scen = {"A": _scenario(text, "A"), "B": _scenario(text, "B")}

    # S7: exact WACC and exact D/(D+E) debt ratio; qualification against both limits.
    results = {}
    for label, s in scen.items():
        E, D = s["E"], s["D"]
        V = D + E
        debt_ratio = D / V
        wacc_pct = (E / V) * s["re_pct"] + (D / V) * s["rd_pct"] * (1 - tax)
        qualifies = (wacc_pct <= wacc_max_pct) and (debt_ratio <= final_shared_ceiling)
        results[label] = {"wacc": wacc_pct, "debt_ratio": debt_ratio, "qualifies": qualifies}

    # S8: among qualifying scenarios the lower exact WACC wins; exact tie -> Scenario A.
    qa, qb = results["A"]["qualifies"], results["B"]["qualifies"]
    if qa and qb:
        final = "Scenario A" if results["A"]["wacc"] <= results["B"]["wacc"] else "Scenario B"
    elif qa:
        final = "Scenario A"
    elif qb:
        final = "Scenario B"
    else:
        final = "Neither scenario"

    slots = {}
    for slot in q["trace_spec"]["slots"]:
        sid = slot["slot_id"]
        if sid == "one_stage_debt_ratio_cap_checkpoint":
            slots[sid] = Fraction(one_stage_ceiling)
        else:
            raise KeyError(f"unknown slot {sid}")

    return {"final": final, "slots": slots}
