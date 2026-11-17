"""h115: one capped Newton-Raphson IRR step for a 2-year after-tax investment.

Cash flows:
  t=0   : -initial outlay
  t=y1  : after-tax distribution (basis unchanged, no further tax)
  t=y2  : net sale proceeds (gross * (1 - selling-cost fraction))
          minus capital-gains tax = rate * max(0, net proceeds - tax basis)

Starting from the trial rate r0, evaluate NPV(r0) exactly and the magnitude of
the negative derivative |dNPV/dr| = sum t*CF_t/(1+r0)^(t+1).  The raw Newton
correction is NPV / |dNPV/dr|; the applied step is min(raw correction, cap).
Final answer = (r0 + step) expressed in percent.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h115"


def solve(text: str, q: dict) -> dict:
    outlay = grab(r"investment requires {N} at time 0", text)
    basis = grab(r"tax basis {N}", text)
    dist = grab(r"after-tax distribution {N} at the end of year", text)
    t_dist = int(grab(r"after-tax distribution {N} at the end of year {N}", text, group=2))
    t_sale = int(grab(r"At the end of year {N} it is sold for", text))
    gross = grab(r"it is sold for {N}", text)
    cost_frac = grab(r"selling costs equal the fraction {N} of gross price", text)
    cg_rate = grab(r"capital-gains tax equals {N} of the positive gain", text)
    r0 = grab(r"annual effective trial rate {N}", text)
    cap = grab(r"rate-step cap {N}", text)

    # Year-2 sale: net proceeds after proportional selling costs, then gain tax.
    net_proceeds = gross * (1 - cost_frac)
    gain = net_proceeds - basis
    cg_tax = cg_rate * gain if gain > 0 else Fraction(0)
    terminal_cf = net_proceeds - cg_tax

    flows = [(0, -outlay), (t_dist, dist), (t_sale, terminal_cf)]

    growth = 1 + r0
    npv = sum((cf / growth ** t for t, cf in flows), Fraction(0))
    # dNPV/dr = sum(-t * CF_t / (1+r)^(t+1)); use its (negative-derivative) magnitude.
    deriv = sum((-t * cf / growth ** (t + 1) for t, cf in flows), Fraction(0))
    neg_deriv_mag = -deriv
    if neg_deriv_mag <= 0:
        raise ValueError("NPV derivative is not negative at the trial rate")

    raw_correction = npv / neg_deriv_mag
    step = min(raw_correction, cap)
    new_rate = r0 + step

    return {
        "final": new_rate * 100,
        "slots": {
            "net_sale_proceeds_after_cost_checkpoint": net_proceeds,
        },
    }
