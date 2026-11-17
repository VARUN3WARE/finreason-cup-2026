# FINANCE MODEL (h045): ESG program selection under feasibility constraints.
#
# For each program P in {A, B} given: cost c_P, financial benefit b_P, verified emissions
# reduction v_P (tons), attribution-overlap ratio o_P (plain ratio, 0.2 = 20%).
#   effective reduction  e_P = v_P * (1 - o_P)                      (tons)
#   net cost             n_P = c_P - b_P                            (USD; may be negative)
#   net cost per eff.ton k_P = n_P / e_P                            (USD per ton; only defined if e_P > 0)
# Feasibility (both must hold):  c_P <= cost_cap   (cost "does not exceed" -> non-strict)
#                                e_P >= min_eff    (effective reduction "reaches" -> non-strict)
# Decision:
#   - both feasible: pick lower k_P; tie -> program_a
#   - exactly one feasible: pick it
#   - none feasible: "no_feasible_program"
# Checkpoint "program A net cost after financial benefits" = c_A - b_A in USD (unrounded;
# framework applies half-up to 2 dp). It is computed regardless of A's feasibility.
# Overrides of standard conventions: none. The cost cap and min effective reduction are shared
# by both programs (a single threshold pair in the text).
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h045"


def _program(label: str, text: str):
    # Segment of text describing the program, up to the next "program"/period boundary.
    m = grab_all(
        r"program " + label + r",? with cost {N}, financial benefit {N}, verified emissions reduction {N},"
        r" and attribution-overlap ratio {N}",
        text,
    )
    return m  # cost, benefit, verified, overlap


def solve(text: str, q: dict) -> dict:
    ca, ba, va, oa = _program("A", text)
    cb, bb, vb, ob = grab_all(
        r"program B with cost {N}, financial benefit {N}, verified emissions reduction {N},"
        r" and attribution-overlap ratio {N}",
        text,
    )
    cap = grab(r"cost does not exceed {N}", text)
    min_eff = grab(r"effective reduction reaches {N}", text)

    def metrics(c, b, v, o):
        eff = v * (1 - o)
        net = c - b
        feasible = (c <= cap) and (eff >= min_eff) and eff > 0
        per_ton = net / eff if eff > 0 else None
        return eff, net, feasible, per_ton

    eff_a, net_a, feas_a, k_a = metrics(ca, ba, va, oa)
    eff_b, net_b, feas_b, k_b = metrics(cb, bb, vb, ob)

    if feas_a and feas_b:
        final = "program_a" if k_a <= k_b else "program_b"
    elif feas_a:
        final = "program_a"
    elif feas_b:
        final = "program_b"
    else:
        final = "no_feasible_program"

    return {"final": final, "slots": {"program_a_net_cost_checkpoint": net_a}}
