"""Solver for hidden cluster h016 -- two-phase compounding "drag x uplift" product index.

Structure (all three instances):
  * P USD received at time zero (start of phase 1); two equal phases of n whole annual periods.
  * Phase-1 annual rate ratio r1, strictly higher phase-2 rate ratio r2; B USD added at the boundary.
  * Smoothed counterfactual: arithmetic mean of the two ANNUAL growth factors, applied in both phases,
    contribution dates preserved.
  * drag   = smoothed terminal value of P  - actual terminal value of P
  * uplift = actual terminal value of B    - smoothed terminal value of B
  * index  = 100 * (drag / (P + B)) * (uplift / (P + B))          [percent]

AMBIGUITY HUNT -- points where analysts could disagree, and the textual resolution adopted:
  A1  "rate ratio is 0.1": a decimal RATIO (0.1 = 10 %/yr), not a percent number. Evidence: the word
      "ratio" and "convert the product to percent" (percent conversion is only requested at the end).
      Annual growth factor g = 1 + r.
  A2  "arithmetic mean of the two annual growth factors": gm = ((1+r1) + (1+r2)) / 2 = 1 + (r1+r2)/2.
      Not a geometric mean (text says arithmetic), and not the mean of the per-PHASE compound factors
      ((1+r1)^n + (1+r2)^n)/2 -- the text says "annual" growth factors.
  A3  "in both phases ... preserving both contribution dates": in the smoothed world the initial P
      compounds at gm for all 2n periods (gm^(2n)); the boundary B is still added at the boundary and
      compounds at gm for n periods (gm^n).
  A4  "receives P USD at the start of two equal phases": P is received once, at time zero (the start of
      the two-phase horizon) -- NOT P at the start of each phase. Evidence: exactly two contributions are
      named later ("initial-contribution" and "boundary-contribution").
  A5  Boundary contribution B is added at the end of phase 1 = start of phase 2, so it earns exactly n
      periods of phase-2 growth (g2^n actual, gm^n smoothed) and no phase-1 growth.
  A6  "Divide each difference by the nominal, undiscounted sum of contributed cash": the SAME denominator
      P + B for both differences (the sum of all cash contributed), not each contribution's own amount.
      Nominal/undiscounted => plain P + B, no time-value adjustment.
  A7  Signs are taken exactly as worded: drag = smoothed - actual (for P), uplift = actual - smoothed
      (for B). Both are positive here (AM-GM gives gm^2 > g1*g2, and g2 > gm since r2 > r1 strictly),
      but no abs/floor is applied -- the sign would be preserved if it ever differed.
  A8  "multiply the resulting decimal ratios once": a single product of the two ratios (not a sum, not
      squared); "convert the product to percent" => multiply by 100. Final unit = percent.
  A9  "whole annual compounding periods": n is an integer, annual compounding only; exact Fraction ** int.
  A10 No rounding anywhere inside the computation; all values returned unrounded (framework rounds).
  A11 Checkpoint 1 "actual first-phase compound growth factor" = (1+r1)^n as a MULTIPLE (not the annual
      factor 1+r1, not a percent, not the full two-phase factor g1^n*g2^n).
  A12 Checkpoint 2 "one-phase compound growth factor under the smoothed counterfactual" = gm^n
      (one phase = n periods; not gm itself and not the two-phase gm^(2n)).
  A13 "strictly higher second-phase rate" is descriptive, not a branch; nothing conditional in the chain.
"""

from __future__ import annotations

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h016"


def solve(text: str, q: dict) -> dict:
    # --- parse (anchored on surrounding words) ---
    P = grab(r"receives {N} USD at the start of two equal phases", text)
    n_frac = grab(r"each lasting {N} whole annual compounding periods", text)
    r1 = grab(r"first-phase annual rate ratio is {N}", text)
    r2 = grab(r"second-phase rate ratio is {N}", text)
    B = grab(r"{N} USD is added at the phase boundary", text)

    if n_frac.denominator != 1:
        raise ValueError(f"phase length must be a whole number of periods, got {n_frac}")
    n = int(n_frac)

    # --- annual growth factors (A1, A2) ---
    g1 = 1 + r1
    g2 = 1 + r2
    gm = (g1 + g2) / 2  # arithmetic mean of the two annual growth factors

    # --- per-phase compound factors (A9, A11, A12) ---
    G1 = g1 ** n          # actual first-phase compound growth factor
    G2 = g2 ** n          # actual second-phase compound growth factor
    Gm = gm ** n          # one-phase compound growth factor, smoothed

    # --- terminal values (A3, A4, A5) ---
    init_actual = P * G1 * G2         # P compounds through both actual phases
    init_smooth = P * Gm * Gm         # P compounds 2n periods at gm
    bound_actual = B * G2             # B added at boundary, n periods at g2
    bound_smooth = B * Gm             # B added at boundary, n periods at gm

    # --- differences as worded (A7) ---
    drag = init_smooth - init_actual
    uplift = bound_actual - bound_smooth

    # --- normalise by nominal contributed cash (A6), multiply once, convert to percent (A8) ---
    contributed = P + B
    drag_ratio = drag / contributed
    uplift_ratio = uplift / contributed
    index_percent = drag_ratio * uplift_ratio * 100

    return {
        "final": index_percent,
        "slots": {
            "first_phase_growth_checkpoint": G1,
            "smoothed_phase_growth_checkpoint": Gm,
        },
    }
