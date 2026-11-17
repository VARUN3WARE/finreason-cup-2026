"""h064 -- green-bond structure A vs B: compounded interest cost + issuance cost, feasibility screen, choice.

Literal transcription of the question, sentence by sentence.
"""

from fractions import Fraction

from finreason.nums import grab, F

TEMPLATE_ID = "h064"


def _structure(label: str, text: str) -> dict:
    # "Structure X has annual yield ratio r, term T, issuance cost C, and eligible-proceeds share s."
    pat = (
        r"Structure " + label + r" has annual yield ratio {N}, term {N}, issuance cost {N}, "
        r"and eligible-proceeds share {N}"
    )
    return {
        "yield": grab(pat, text, 1),
        "term": grab(pat, text, 2),
        "issuance_cost": grab(pat, text, 3),
        "eligible_share": grab(pat, text, 4),
    }


def solve(text: str, q: dict) -> dict:
    # Sentence 1: "... for the same principal P."
    principal = grab(r"for the same principal {N}", text)

    # Sentences 2-3: per-structure parameters.
    sa = _structure("A", text)
    sb = _structure("B", text)

    # Sentence 5: thresholds.
    cost_cap = grab(r"total financing cost does not exceed {N}", text)
    share_floor = grab(r"eligible share reaches {N}", text)

    # Sentence 4: "compound the principal over its term, subtract principal to obtain interest cost,
    #              and add issuance cost to obtain total financing cost."
    def evaluate(s: dict) -> dict:
        factor = 1 + s["yield"]                     # one-period gross compound factor
        term = s["term"]
        if term.denominator != 1:
            raise ValueError("non-integer term")
        compounded = principal * factor ** int(term)
        interest_cost = compounded - principal
        total_cost = interest_cost + s["issuance_cost"]
        # "feasible only if total financing cost does not exceed cap (<=) and its eligible share reaches floor (>=)"
        feasible = (total_cost <= cost_cap) and (s["eligible_share"] >= share_floor)
        return {"factor": factor, "total": total_cost, "feasible": feasible}

    ra = evaluate(sa)
    rb = evaluate(sb)

    # Sentence 6: choice rule.
    if ra["feasible"] and rb["feasible"]:
        if ra["total"] <= rb["total"]:              # lower cost; structure_a on a cost tie
            final = "structure_a"
        else:
            final = "structure_b"
    elif ra["feasible"]:
        final = "structure_a"
    elif rb["feasible"]:
        final = "structure_b"
    else:
        final = "no_feasible_structure"

    slots = {}
    for slot in q["trace_spec"]["slots"]:
        sid = slot["slot_id"] if isinstance(slot, dict) else slot
        if sid == "structure_a_annual_factor_checkpoint":
            slots[sid] = ra["factor"]
        else:
            raise KeyError(f"unexpected slot {sid}")
    return {"final": final, "slots": slots}
