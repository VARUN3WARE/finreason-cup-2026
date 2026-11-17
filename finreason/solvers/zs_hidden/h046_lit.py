"""h046 -- three-year retirement bridge: solve the first-year withdrawal W that leaves a required reserve.

Literal transcription of the question, sentence by sentence.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h046"


def solve(text: str, q: dict) -> dict:
    # "A saver enters a three-year retirement bridge with {P}."
    opening_capital = grab(r"retirement bridge with {N}", text)

    # "The remaining balance earns {r} annually."
    earn_rate = grab(r"remaining balance earns {N} annually", text)
    balance_factor = 1 + earn_rate

    # "Withdrawals occur at each year-end: W after year 1, W times one plus {g} after year 2,
    #  and W times the square of that growth factor after year 3."
    withdrawal_growth = grab(r"W times one plus {N} after year 2", text)
    growth_factor = 1 + withdrawal_growth
    # withdrawal multipliers (in units of W) for years 1, 2, 3
    mult = [Fraction(1), growth_factor, growth_factor ** 2]

    # "Immediately after the third withdrawal, {R} must remain."
    reserve = grab(r"after the third withdrawal, {N} must remain", text)

    # Balance recursion with year-end withdrawals, written as B3 = A - W * K (linear in W):
    #   B1 = P*(1+r) - W
    #   B2 = B1*(1+r) - W*(1+g)
    #   B3 = B2*(1+r) - W*(1+g)^2
    const_part = opening_capital          # coefficient-free part of the balance
    w_coeff = Fraction(0)                 # coefficient of W in the balance (negative)
    for m in mult:
        const_part = const_part * balance_factor
        w_coeff = w_coeff * balance_factor - m

    # "Compute the exact first-year withdrawal W that leaves the required reserve."
    # Reserve equality with the unrounded exact W:  const_part + w_coeff * W = reserve
    W = (reserve - const_part) / w_coeff

    # sanity: re-run the balance path with the exact W
    bal = opening_capital
    for m in mult:
        bal = bal * balance_factor - W * m
    assert bal == reserve

    # Checkpoint: gross two-year value of the opening capital before withdrawals
    gross_two_year = opening_capital * balance_factor ** 2

    return {
        "final": W,
        "slots": {"two_year_gross_capital_checkpoint": gross_two_year},
    }
