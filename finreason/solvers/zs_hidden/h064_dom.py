# FINANCE MODEL (h064): green-bond structure choice, A vs B.
# For structure s in {A, B} with principal P, annual yield ratio y_s, term n_s (whole years),
# issuance cost c_s, eligible-proceeds share e_s:
#   - Standard annual compounding: one-period gross factor g_s = 1 + y_s  (y_s is a ratio, not percent).
#   - Compounded balance after the term = P * g_s ** n_s   (integer power, exact Fraction).
#   - Interest cost = balance - P.
#   - Total financing cost = interest cost + issuance cost c_s.
#   - Feasible iff total_cost <= cost cap ("does not exceed" -> non-strict)
#                  AND e_s >= eligibility threshold ("reaches" -> non-strict).
#   - Choice: both feasible -> lower total cost, exact tie -> structure_a;
#             exactly one feasible -> that one; none -> no_feasible_structure.
# Checkpoint: structure_a_annual_factor_checkpoint = g_A = 1 + y_A (unrounded; framework rounds to 8 dp).
# No overrides of standard conventions (no continuous / intra-year compounding stated).
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h064"


def _structure(label, text):
    # Segment of the text describing this structure: from "Structure X has" to the sentence end.
    # Sentences contain decimals with dots, so anchor on field names within the segment instead.
    start = text.index(f"Structure {label} has")
    nxt = text.find("Structure B has", start + 1) if label == "A" else text.find("For each structure", start + 1)
    seg = text[start:nxt]
    y = grab(r"annual yield ratio {N}", seg)
    n = grab(r"term {N}", seg)
    c = grab(r"issuance cost {N}", seg)
    e = grab(r"eligible-proceeds share {N}", seg)
    return y, n, c, e


def solve(text: str, q: dict) -> dict:
    P = grab(r"for the same principal {N}", text)
    cap = grab(r"total financing cost does not exceed {N}", text)
    thr = grab(r"its eligible share reaches {N}", text)

    res = {}
    for label in ("A", "B"):
        y, n, c, e = _structure(label, text)
        assert n.denominator == 1
        g = 1 + y
        balance = P * g ** int(n)
        interest = balance - P
        total = interest + c
        feasible = (total <= cap) and (e >= thr)
        res[label] = (g, total, feasible)

    gA, tA, fA = res["A"]
    gB, tB, fB = res["B"]
    if fA and fB:
        final = "structure_a" if tA <= tB else "structure_b"
    elif fA:
        final = "structure_a"
    elif fB:
        final = "structure_b"
    else:
        final = "no_feasible_structure"

    return {"final": final, "slots": {"structure_a_annual_factor_checkpoint": gA}}
