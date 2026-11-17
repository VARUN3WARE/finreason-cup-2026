"""h045: ESG program A vs B -- feasibility screen then lower net cost per effective ton."""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h045"


def _program(label: str, text: str) -> dict:
    # "program A, with cost 877, financial benefit 823.037, verified emissions
    #  reduction 128, and attribution-overlap ratio 0.2"
    seg_rx = rf"program {label},? with (.*?)(?:, against|\.\s|$)"
    import re

    m = re.search(seg_rx, text, flags=re.S)
    seg = m.group(1) if m else text
    cost = grab(r"cost (?:of )?(?:USD )?\$?{N}", seg)
    benefit = grab(r"financial benefit (?:of )?(?:USD )?\$?{N}", seg)
    verified = grab(r"verified emissions reduction (?:of )?{N}", seg)
    overlap_m = re.search(r"attribution-overlap ratio (?:of )?(-?\d+(?:\.\d+)?(?:/\d+)?)\s*(percent|%)?", seg)
    overlap = Fraction(overlap_m.group(1))
    if overlap_m.group(2):
        overlap /= 100
    effective = verified * (1 - overlap)
    net_cost = cost - benefit
    return {"cost": cost, "benefit": benefit, "effective": effective, "net": net_cost}


def solve(text: str, q: dict) -> dict:
    a = _program("A", text)
    b = _program("B", text)

    cost_cap = grab(r"cost does not exceed (?:USD )?\$?{N}", text)
    min_eff = grab(r"effective reduction reaches {N}", text)

    def feasible(p):
        return p["cost"] <= cost_cap and p["effective"] >= min_eff

    fa, fb = feasible(a), feasible(b)
    if fa and fb:
        per_a = a["net"] / a["effective"]
        per_b = b["net"] / b["effective"]
        final = "program_a" if per_a <= per_b else "program_b"
    elif fa:
        final = "program_a"
    elif fb:
        final = "program_b"
    else:
        final = "no_feasible_program"

    return {"final": final, "slots": {"program_a_net_cost_checkpoint": a["net"]}}
