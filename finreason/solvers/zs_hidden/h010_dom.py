# FINANCE MODEL (h010)
# Two initiatives A (cost synergy) and B (revenue synergy) with marginal success probabilities pA, pB
# and standalone payoffs vA, vB (USD millions, earned only on success). If BOTH succeed an extra
# incremental benefit S is earned. Joint success probability q = P(A and B), dependence unspecified.
# Unconditional integration cost C is paid with certainty (deducted once, not probability-weighted).
#
#   E[net] = pA*vA + pB*vB + q*S - C        (linearity of expectation; S only paid on the joint event)
#   Required E[net] >= T (target)           -> solve with equality for the required joint probability q*:
#   gross requirement G = T + C             (gross expected benefit before the integration cost is deducted)
#   q* = (G - pA*vA - pB*vB) / S
#
# Frechet bounds for P(A and B) given marginals (text-defined, per problem statement):
#   lower L = pB - (1 - pA)   (= pA + pB - 1 since the sum exceeds one; text defines it this way)
#   upper U = pB              (since pA > pB)
#   width W = 1 - pA          (= U - L)
# Answer: percentage of the feasible band consumed above its lower bound by q*:
#   100 * (q* - L) / W        (0% = lower bound, 100% = upper bound; >100% = infeasible, reported as is,
#                              no capping or clipping)
# Checkpoints: 1) gross requirement G (usd_million); 2) Frechet lower bound L (ratio).
# Overrides / notes: none; no rounding inside the computation, everything exact Fractions.
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h010"


def solve(text: str, q: dict) -> dict:
    pA, vA = grab_all(r"cost-synergy initiative has marginal success probability {N} and contributes {N} USD", text)
    pB, vB = grab_all(r"revenue-synergy initiative has marginal success probability {N} and contributes {N} USD", text)
    S = grab(r"incremental benefit {N} USD", text)
    C = grab(r"integration cost is {N} USD", text)
    T = grab(r"required expected net benefit is {N} USD", text)

    G = T + C
    q_req = (G - pA * vA - pB * vB) / S

    L = pB - (1 - pA)
    W = 1 - pA
    final = (q_req - L) / W * 100

    return {
        "final": final,
        "slots": {
            "gross_requirement_checkpoint": G,
            "frechet_lower_bound_checkpoint": L,
        },
    }
