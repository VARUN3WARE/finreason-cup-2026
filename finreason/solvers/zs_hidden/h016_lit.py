"""h016 -- two-phase account, smoothed-growth counterfactual, drag x uplift product index.

Literal transcription of the question text, sentence by sentence.
"""

from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F  # noqa: F401

TEMPLATE_ID = "h016"


def solve(text: str, q: dict) -> dict:
    # S1: "An account receives {C0} USD at the start of two equal phases,
    #      each lasting {n} whole annual compounding periods."
    c0 = grab(r"account receives {N} USD at the start of two equal phases", text)
    n = grab(r"each lasting {N} whole annual compounding periods", text)
    assert n.denominator == 1
    n = int(n)

    # S2: "The first-phase annual rate ratio is {r1}, the strictly higher second-phase
    #      rate ratio is {r2}, and {C1} USD is added at the phase boundary."
    r1 = grab(r"first-phase annual rate ratio is {N}", text)
    r2 = grab(r"second-phase rate ratio is {N}", text)
    c1 = grab(r"and {N} USD is added at the phase boundary", text)

    # Actual annual growth factors per phase.
    g1 = 1 + r1
    g2 = 1 + r2

    # Actual compound growth factors per phase (n periods each).
    phase1_factor = g1 ** n          # checkpoint 1
    phase2_factor = g2 ** n

    # S3: smoothed counterfactual: arithmetic mean of the two annual growth factors,
    #     applied in both phases; contribution dates preserved.
    g_bar = (g1 + g2) / 2
    smooth_phase_factor = g_bar ** n  # checkpoint 2

    # Terminal values (end of phase 2).
    # Initial contribution at time 0 grows through both phases.
    init_actual = c0 * phase1_factor * phase2_factor
    init_smooth = c0 * smooth_phase_factor * smooth_phase_factor
    # Boundary contribution at end of phase 1 grows through phase 2 only.
    bound_actual = c1 * phase2_factor
    bound_smooth = c1 * smooth_phase_factor

    # S4: drag = smoothed TV - actual TV (initial contribution);
    #     uplift = actual TV - smoothed TV (boundary contribution).
    drag = init_smooth - init_actual
    uplift = bound_actual - bound_smooth

    # S5: divide each by nominal undiscounted sum of contributed cash, multiply once, percent.
    contributed = c0 + c1
    drag_ratio = drag / contributed
    uplift_ratio = uplift / contributed
    final = drag_ratio * uplift_ratio * 100

    return {
        "final": final,
        "slots": {
            "first_phase_growth_checkpoint": phase1_factor,
            "smoothed_phase_growth_checkpoint": smooth_phase_factor,
        },
    }
