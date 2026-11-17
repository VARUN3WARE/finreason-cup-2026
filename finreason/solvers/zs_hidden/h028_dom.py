"""h028 -- adjusted run-rate EPS accretion/dilution after a stylized acquisition.

FINANCE MODEL (standard conventions; no overrides beyond the text):
  * Acquirer predeal shares N0 have aggregate reference value E at the fixed contractual price P,
    so N0 = E / P.  Only the ratio new_shares / N0 matters; P cancels.
  * Base upfront consideration B (excl. earnout), cash fraction c:
        cash leg   = c * B
        stock leg  = (1 - c) * B   -> issued as shares at P
  * Fully realized earnout A (incremental to B) settled 100% in shares at the same P.
        new shares = ((1 - c) * B + A) / P
        issuance ratio = new shares / N0 = ((1 - c) * B + A) / E          [checkpoint 1]
  * The whole cash leg is debt funded at pre-tax rate i:
        pretax interest = c * B * i                                        [checkpoint 2, USD m]
  * With tax rate t: after-tax interest = interest*(1-t); after-tax synergies = S*(1-t)
    (target NI excludes synergies, so they are added separately).
  * Pro forma NI = NI_acq + NI_tgt + S*(1-t) - interest*(1-t)
  * Pro forma shares = N0 * (1 + issuance ratio) (all shares outstanding full year; no weighting).
  * Standalone EPS = NI_acq / N0.   Pro forma EPS = NI_pf / (N0*(1+ratio)).
  * Accretion % = (EPS_pf / EPS_sa - 1) * 100 = (NI_pf / ((1+ratio) * NI_acq) - 1) * 100.
"""
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h028"


def solve(text: str, q: dict) -> dict:
    E = grab(r"aggregate reference equity value {N}", text)
    B = grab(r"Upfront base consideration is {N}", text)
    c = grab(r"{N} is paid in cash", text)
    A = grab(r"earnout with settlement value {N}", text)
    i = grab(r"annual pre-tax interest rate {N}", text)
    ni_a = grab(r"net income is {N} for the acquirer", text)
    ni_t = grab(r"and {N} for the target", text)
    S = grab(r"synergies of {N}", text)
    t = grab(r"tax rate {N}", text)

    cash = c * B
    stock = (1 - c) * B
    ratio = (stock + A) / E
    interest = cash * i

    ni_pf = ni_a + ni_t + S * (1 - t) - interest * (1 - t)
    eps_ratio = ni_pf / ((1 + ratio) * ni_a)
    accretion_pct = (eps_ratio - 1) * 100

    return {
        "final": accretion_pct,
        "slots": {
            "deal_share_issuance_checkpoint": ratio,
            "pretax_interest_checkpoint": interest,
        },
    }
