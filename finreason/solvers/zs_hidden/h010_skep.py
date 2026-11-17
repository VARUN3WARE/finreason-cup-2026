"""Cluster h010 -- joint-success probability needed for a post-merger synergy target,
expressed as the share of the Fréchet feasible band it consumes.

Structure (per instance):
    pC, bC : cost-synergy marginal success probability and standalone benefit (USD mn)
    pR, bR : revenue-synergy marginal success probability and standalone benefit (USD mn)
    I      : incremental benefit earned only when BOTH succeed (beyond the standalones)
    C      : unconditional integration cost (paid regardless of outcomes)
    T      : required expected NET benefit

    E[net] = pC*bC + pR*bR + J*I - C  ==  T
    gross  = T + C                               -> slot gross_requirement_checkpoint (usd_million)
    J      = (gross - pC*bC - pR*bR) / I          (joint success probability needed)
    L      = pR - (1 - pC)                       -> slot frechet_lower_bound_checkpoint (ratio)
    U      = pR,   W = 1 - pC  (= U - L)
    final  = (J - L) / W * 100                   -> percent of the band consumed above L

AMBIGUITIES CONSIDERED AND RESOLUTIONS (with textual evidence):
 1. Expected-benefit model. "contributes X USD millions whenever it succeeds" -> standalone
    expected value pC*bC and pR*bR. "If both initiatives succeed, incremental benefit I is
    earned beyond the standalone benefits" -> the pair-event adds I on top, so E[benefit]
    = pC*bC + pR*bR + J*I, where J = P(both succeed). "without assuming independence" /
    "Do not assume a dependence structure" -> J is the unknown, NOT pC*pR.
 2. Gross requirement. The slot asks for "the gross expected benefit required before the
    integration cost is deducted". The cost is "Unconditional" (paid in every state), so
    E[net] = E[gross] - C and the gross requirement is T + C (not T, not T - C).
 3. "Meet the target" = equality (E[net] == T); J is solved from the equation, no inequality
    or ceiling/floor logic is involved.
 4. Fréchet bounds. The text defines them explicitly: lower = revenue-synergy probability minus
    cost-synergy FAILURE probability, i.e. pR - (1 - pC) = pC + pR - 1; upper = pR; width =
    1 - pC. This matches the generic bounds max(0, pC+pR-1) and min(pC, pR) because the text
    guarantees "cost-synergy probability is strictly higher than the revenue-synergy
    probability and their sum exceeds one". I implement the text's literal formulas (identical
    under those stated conditions); no max(0, .) clamp is needed or applied.
 5. Final quantity. "percentage of this feasible band consumed above its lower bound by the
    required joint success probability. Zero percent is the lower bound, one hundred percent
    is the upper bound" -> (J - L) / W * 100, reported in percent units (answer_spec unit is
    `percent`, so 155.56 means 155.56%).
 6. Infeasible results. "a result above one hundred percent is infeasible under the stated
    marginals" is an interpretation note, not a capping rule -> the raw value is reported
    uncapped (and likewise a negative value would be reported as-is, not floored at zero).
 7. Rounding. "use exact arithmetic through all intermediate steps, round only the final value"
    -> every value is returned as an exact Fraction; no intermediate rounding anywhere.
 8. Units. Probabilities are given as plain ratios (0.75), not percents -> used directly.
    Benefits/cost/target are all in USD millions -> gross slot is in usd_million as-is.
 9. Which probability is "failure probability": cost-synergy failure = 1 - pC (the text ties
    "failure probability" to the cost-synergy initiative for both the lower bound and the width).
"""

from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "h010"


def solve(text: str, q: dict) -> dict:
    # --- Parse inputs (anchored on surrounding words) ---------------------------------------
    pC, bC = grab_all(
        r"cost-synergy initiative has marginal success probability {N}\s+and contributes {N} USD millions",
        text,
    )
    pR, bR = grab_all(
        r"revenue-synergy initiative has marginal success probability {N}\s+and contributes {N} USD millions",
        text,
    )
    inc = grab(r"incremental benefit {N} USD millions", text)
    cost = grab(r"integration cost is {N} USD millions", text)
    target = grab(r"required expected net benefit is {N} USD millions", text)

    # --- Chain -----------------------------------------------------------------------------
    # Gross expected benefit required before the (unconditional) integration cost is deducted.
    gross_required = target + cost

    # Standalone expected contributions (marginals only; no dependence assumption needed).
    standalone_expected = pC * bC + pR * bR

    # Joint success probability needed so that E[net] == target.
    joint_required = (gross_required - standalone_expected) / inc

    # Fréchet band as defined in the text.
    cost_failure = Fraction(1) - pC
    lower = pR - cost_failure          # revenue prob minus cost-synergy failure prob
    width = cost_failure               # = upper - lower, with upper = pR

    # Share of the band consumed above its lower bound, in percent (uncapped).
    consumed_pct = (joint_required - lower) / width * 100

    return {
        "final": consumed_pct,
        "slots": {
            "gross_requirement_checkpoint": gross_required,
            "frechet_lower_bound_checkpoint": lower,
        },
    }
