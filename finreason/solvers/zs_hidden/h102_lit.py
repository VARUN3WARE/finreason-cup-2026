"""h102 -- literal transcription solver.

Structure (sentence by sentence):
  S1 "Over one annual period, a DeFi user already has P1 USD earning yield ratio y1."
  S2 "A second pool offers yield ratio y2."
  S3 "The protocol charges a fixed annual fee of FEE USD that does not depend on the
      added principal."
  S4 "Determine the additional stake required in the second pool to deliver a net
      annual reward of TARGET USD."
  S5 "Report the result in USD using half-up rounding to two decimal places."

Net annual reward (one year) = existing reward + second-pool reward on the added stake
                               - fixed fee (charged once, independent of the stake).
Solve  P1*y1 + y2*X - FEE = TARGET  for X.
"""

from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "h102"


def solve(text: str, q: dict) -> dict:
    # S1: one annual period; the existing position and its yield ratio (a plain ratio, 0.1 = 10%).
    period_years = Fraction(1)  # "Over one annual period"
    existing_principal, existing_yield_ratio = grab_all(
        r"already has {N} USD earning yield ratio {N}", text
    )

    # S2: the second pool's yield ratio (plain ratio).
    second_yield_ratio = grab(r"second pool offers yield ratio {N}", text)

    # S3: fixed annual fee, independent of the added principal (charged once for the year).
    fixed_annual_fee = grab(r"fixed annual fee of {N} USD", text) * period_years

    # S4: target net annual reward.
    target_net_reward = grab(r"net annual reward of {N} USD", text)

    # Checkpoint 1: reward supplied by the existing position over the one-year period.
    existing_reward = existing_principal * existing_yield_ratio * period_years

    # Net reward as a function of the added stake X:
    #   net(X) = existing_reward + second_yield_ratio * X * period_years - fixed_annual_fee
    # Required X such that net(X) = target_net_reward.
    reward_needed_from_second_pool = target_net_reward + fixed_annual_fee - existing_reward
    additional_stake = reward_needed_from_second_pool / (second_yield_ratio * period_years)

    # Sanity: the solved stake reproduces the target net reward exactly.
    assert (
        existing_reward + second_yield_ratio * additional_stake * period_years - fixed_annual_fee
        == target_net_reward
    )

    # S5: framework applies half-up rounding to 2 dp (final) and 4 dp (checkpoint).
    return {
        "final": additional_stake,
        "slots": {"existing_reward_checkpoint": existing_reward},
    }
