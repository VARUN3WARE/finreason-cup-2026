"""h115 -- one capped Newton-Raphson step on the NPV of a two-year after-tax hold-and-sell investment.

Literal transcription, sentence by sentence:

  S1 "An investment requires I0 at time 0 and has unchanged tax basis B."
  S2 "It pays the after-tax distribution D at the end of year t1 without changing that basis."
  S3 "At the end of year t2 it is sold for P; selling costs equal the fraction s of gross price, and
      capital-gains tax equals g of the positive gain measured as net sale proceeds after selling costs
      minus tax basis."
  S4 "Starting from annual effective trial rate r0, evaluate exact NPV and form one positive
      Newton-Raphson correction using the negative-derivative magnitude."
  S5 "Apply the fixed absolute rate-step cap c, add the smaller of the raw correction and cap to the
      trial rate, and report the result as an annual percentage."
  S6 "Do not iterate again ..."  -> exactly one step.

Checkpoint (position 1): year-2 net sale proceeds after proportional selling costs, before gain tax (USD).
Final: (r0 + min(raw correction, cap)) * 100, in percent.  All arithmetic exact (Fraction).
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h115"


def solve(text: str, q: dict) -> dict:
    # --- S1: time-0 requirement (outflow) and the unchanged tax basis.
    initial_requirement = grab(r"requires {N} at time 0", text)
    tax_basis = grab(r"unchanged tax basis {N}", text)

    # --- S2: after-tax distribution at the end of year t1 (basis is not changed by it).
    distribution = grab(r"after-tax distribution {N} at the end of year", text)
    t_dist = grab(r"after-tax distribution {N} at the end of year {N}", text, group=2)

    # --- S3: sale at the end of year t2.
    t_sale = grab(r"At the end of year {N} it is sold for", text)
    gross_price = grab(r"it is sold for {N}", text)
    selling_cost_fraction = grab(r"selling costs equal the fraction {N} of gross price", text)
    gain_tax_rate = grab(r"capital-gains tax equals {N} of the positive gain", text)

    selling_costs = selling_cost_fraction * gross_price
    net_sale_proceeds = gross_price - selling_costs           # after selling costs, before gain tax
    gain = net_sale_proceeds - tax_basis                       # net sale proceeds minus tax basis
    positive_gain = gain if gain > 0 else Fraction(0)          # only the positive gain is taxed
    capital_gains_tax = gain_tax_rate * positive_gain
    sale_cash_flow = net_sale_proceeds - capital_gains_tax     # after-tax year-t2 sale cash flow

    # Cash-flow schedule: (time, amount); the time-0 requirement is an outflow.
    flows = [
        (0, -initial_requirement),
        (int(t_dist), distribution),
        (int(t_sale), sale_cash_flow),
    ]

    # --- S4: exact NPV at the annual effective trial rate, and the derivative magnitude.
    trial_rate = grab(r"annual effective trial rate {N}", text)
    growth = 1 + trial_rate
    npv = sum((amt / growth ** t for t, amt in flows), Fraction(0))
    # dNPV/dr = sum( -t * CF_t / (1+r)^(t+1) )
    derivative = sum((-t * amt / growth ** (t + 1) for t, amt in flows), Fraction(0))
    negative_derivative_magnitude = abs(derivative)
    # Newton-Raphson: r - NPV/NPV' = r + NPV / |NPV'| (NPV' < 0): the raw (positive) correction.
    raw_correction = npv / negative_derivative_magnitude

    # --- S5: fixed absolute rate-step cap; add the smaller of raw correction and cap.
    cap = grab(r"rate-step cap {N}", text)
    step = min(raw_correction, cap)
    next_rate = trial_rate + step
    final_percent = next_rate * 100                            # annual percentage

    return {
        "final": final_percent,
        "slots": {
            "net_sale_proceeds_after_cost_checkpoint": net_sale_proceeds,
        },
    }
