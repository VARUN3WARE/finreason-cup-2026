"""Hidden cluster h102: additional stake in a second DeFi pool to reach a net annual reward.

One annual period, simple (non-compounded) yield:
    existing reward       = existing principal * existing yield ratio        (checkpoint)
    net annual reward     = existing reward + added stake * second-pool yield ratio - fixed fee
The fixed annual fee does not depend on the added principal, so it is a flat deduction.
Setting the net annual reward equal to the target and solving for the added stake:
    added stake = (target + fee - existing reward) / second-pool yield ratio
All values exact (Fraction); the framework applies the half-up rounding of each result_spec.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h102"


def solve(text: str, q: dict) -> dict:
    principal = grab(r"already has (?:a principal of )?(?:USD )?{N}(?: USD)?", text)
    r_existing = grab(r"earning (?:a )?yield ratio(?: of)? {N}", text)
    r_second = grab(r"second pool offers (?:a )?yield ratio(?: of)? {N}", text)
    fee = grab(r"fixed annual fee of (?:USD )?{N}", text)
    target = grab(r"net annual reward of (?:USD )?{N}", text)

    existing_reward = principal * r_existing                 # reward supplied by the existing position
    required_from_second = target + fee - existing_reward    # reward the second pool must supply
    added_stake = required_from_second / r_second

    return {
        "final": Fraction(added_stake),
        "slots": {"existing_reward_checkpoint": Fraction(existing_reward)},
    }
