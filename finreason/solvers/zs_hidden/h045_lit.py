"""h045 -- ESG program A vs B: feasibility screen, then lowest net cost per effective ton.

Literal transcription of the question, sentence by sentence.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h045"


def _program(text: str, label: str) -> dict:
    """Sentence 1: 'program X, with cost C, financial benefit B, verified emissions reduction V,
    and attribution-overlap ratio O'."""
    rx = (
        rf"program {label},?\s+with cost (?:USD\s*)?(?P<cost>{NUMBER}),\s*"
        rf"financial benefit (?:USD\s*)?(?P<benefit>{NUMBER}),\s*"
        rf"verified emissions reduction (?P<verified>{NUMBER})[^,]*,\s*"
        rf"and attribution-overlap ratio (?P<overlap>{NUMBER})(?P<pct>\s*(?:percent|%))?"
    )
    m = re.search(rx, text, flags=re.S)
    if m is None:
        raise ValueError(f"program {label} terms not found")
    overlap = F(m.group("overlap"))
    if m.group("pct"):
        overlap = overlap / 100
    return {
        "cost": F(m.group("cost")),
        "benefit": F(m.group("benefit")),
        "verified": F(m.group("verified")),
        "overlap": overlap,
    }


def solve(text: str, q: dict) -> dict:
    # Sentence 1: the two programs' inputs.
    progs = {"program_a": _program(text, "A"), "program_b": _program(text, "B")}

    # Sentence 2: definitions applied to each program.
    #   effective reduction = verified reduction * (1 - overlap ratio)
    #   net cost per effective ton = (cost - financial benefit) / effective reduction
    for p in progs.values():
        p["effective"] = p["verified"] * (1 - p["overlap"])
        p["net_cost"] = p["cost"] - p["benefit"]
        p["net_cost_per_ton"] = (p["net_cost"] / p["effective"]) if p["effective"] != 0 else None

    # Sentence 3: feasibility -- cost does not exceed CAP (<=) and effective reduction reaches MIN (>=).
    cost_cap = grab(r"cost does not exceed (?:USD\s*)?{N}", text)
    min_effective = grab(r"effective reduction reaches {N}", text)
    for p in progs.values():
        p["feasible"] = (p["cost"] <= cost_cap) and (p["effective"] >= min_effective)

    # Sentences 4-5: among feasible programs pick the lower net cost per effective ton,
    # program_a on a tie; a sole feasible program is selected; none -> no_feasible_program.
    feasible = [name for name in ("program_a", "program_b") if progs[name]["feasible"]]
    if not feasible:
        final = "no_feasible_program"
    elif len(feasible) == 1:
        final = feasible[0]
    else:
        a = progs["program_a"]["net_cost_per_ton"]
        b = progs["program_b"]["net_cost_per_ton"]
        final = "program_a" if a <= b else "program_b"

    # Checkpoint: program A net cost after financial benefits (cost - benefit), in USD.
    slots = {"program_a_net_cost_checkpoint": progs["program_a"]["net_cost"]}
    return {"final": final, "slots": slots}
