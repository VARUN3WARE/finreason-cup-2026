"""h043 -- inverse WACC: maximum pre-tax cost of debt that keeps WACC at a ceiling.

Literal transcription of the question text:
  "A company has equity value E, debt value D, cost of equity percentage Re,
   and corporate tax rate ratio t. The WACC ceiling W is also a percentage.
   Determine the maximum pre-tax cost of debt that keeps its WACC at that ceiling."

WACC (percent) = E/V * Re + D/V * Rd * (1 - t),  V = E + D.
Written in terms of the debt-to-equity ratio d = D/E (the checkpoint):
  E/V = 1/(1+d),  D/V = d/(1+d)
  W = Re/(1+d) + Rd*(1-t)*d/(1+d)
  => Rd = (W*(1+d) - Re) / ((1-t)*d)
WACC is increasing in Rd, so setting WACC equal to the ceiling gives the maximum Rd.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h043"


def solve(text: str, q: dict) -> dict:
    # Sentence 1: inputs.
    equity_value = grab(r"equity value {N}", text)
    debt_value = grab(r"debt value {N}", text)
    cost_of_equity_pct = grab(r"cost of equity percentage {N}", text)   # percent
    tax_rate = grab(r"corporate tax rate ratio {N}", text)              # ratio
    # Sentence 2: the WACC ceiling, also a percentage.
    wacc_ceiling_pct = grab(r"WACC ceiling {N}", text)                  # percent

    # Checkpoint: debt-to-equity ratio used by the inverse WACC calculation.
    debt_to_equity = Fraction(debt_value) / Fraction(equity_value)

    # Sentence 3: maximum pre-tax cost of debt keeping WACC at the ceiling.
    # W = Re/(1+d) + Rd*(1-t)*d/(1+d)  =>  Rd = (W*(1+d) - Re) / ((1-t)*d)
    cost_of_debt_pct = (wacc_ceiling_pct * (1 + debt_to_equity) - cost_of_equity_pct) / (
        (1 - tax_rate) * debt_to_equity
    )

    return {
        "final": cost_of_debt_pct,
        "slots": {"debt_to_equity_checkpoint": debt_to_equity},
    }
