# FINANCE MODEL (Hamada, zero debt beta, tax shields fully usable and stable)
#
#   Levered beta:  bL = bU * [E + (1 - t) * D] / E        (Hamada, debt beta = 0)
#   Hamada factor: H  = [E + (1 - t) * D] / E = 1 + (1 - t) * D / E
#   Unlevering:    bU = bL / H                            (per comparable)
#
# Each comparable i in {A, B} supplies (bL_i, D_i, E_i, t_i):
#   checkpoint "tax-adjusted debt term" in its Hamada factor = (1 - t_i) * D_i   [USD]
#     (the quantity added to equity E_i in the numerator of the factor)
#   H_i  = (E_i + (1 - t_i) * D_i) / E_i
#   bU_i = bL_i / H_i
# Peer asset beta = unweighted arithmetic mean of bU_A and bU_B (equal weights).
# Target is re-levered with its own D, E, t:
#   H_T = (E_T + (1 - t_T) * D_T) / E_T
#   bL_target = mean(bU) * H_T                            (final answer, dimensionless)
#
# Conventions / notes:
#   - All arithmetic exact (Fractions); nothing rounded inside the computation. The two
#     checkpoints and the final are rounded only by the framework (4 dp half-up), and
#     displayed checkpoints are never fed back.
#   - Tax rates are given as decimals (0.2 = 20 percent), used directly as t, not divided by 100.
#   - No cash/hybrid/preferred adjustments, debt beta = 0 (explicit in text).
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h021"

_N = r"(-?\d+(?:\.\d+)?(?:/\d+)?)"


def solve(text: str, q: dict) -> dict:
    iA = text.index("Comparable A has")
    iB = text.index("Comparable B has")
    iT = text.index("The target has")
    iEnd = text.index("For each comparable", iT)

    segA = text[iA:iB]
    segB = text[iB:iT]
    segT = text[iT:iEnd]

    betaA = grab(r"levered beta " + _N, segA)
    debtA = grab(r"debt market value " + _N + r"\s*USD", segA)
    eqA = grab(r"common-equity market value " + _N + r"\s*USD", segA)
    taxA = grab(r"marginal corporate tax rate " + _N, segA)

    # Comparable B: "has corresponding values <beta>, <D> USD, <E> USD, and <t>."
    vals = grab_all(
        r"corresponding values " + _N + r",\s*" + _N + r"\s*USD,\s*" + _N + r"\s*USD,\s*and\s*" + _N,
        segB,
    )
    betaB, debtB, eqB, taxB = vals

    debtT = grab(r"debt market value " + _N + r"\s*USD", segT)
    eqT = grab(r"common-equity market value " + _N + r"\s*USD", segT)
    taxT = grab(r"tax rate " + _N, segT)

    def adj_debt(t, d):
        return (1 - t) * d

    def factor(t, d, e):
        return (e + adj_debt(t, d)) / e

    adjA = adj_debt(taxA, debtA)
    adjB = adj_debt(taxB, debtB)

    buA = betaA / factor(taxA, debtA, eqA)
    buB = betaB / factor(taxB, debtB, eqB)
    mean_bu = (buA + buB) / 2

    final = mean_bu * factor(taxT, debtT, eqT)

    return {
        "final": final,
        "slots": {
            "comparable_a_tax_adjusted_debt_checkpoint": adjA,
            "comparable_b_tax_adjusted_debt_checkpoint": adjB,
        },
    }
