# FINANCE MODEL (h075)
#
# Quantity: the initial principal P0 that must be deposited at time 0 so that an account, compounding
# once per whole annual period at rate r (a ratio, 0.1 = 10%), holds exactly a target balance T after
# N whole periods, given one extra "later" contribution C.
#
# Timeline: the account runs from time 0 to time N. The later contribution C is deposited at a
# compounding boundary from which exactly K whole periods remain (i.e. at time N-K), and it earns the
# same rate r for those K periods.  So the contribution is worth C * (1+r)^K at time N, and its
# compound growth factor is g = (1+r)^K (this is the checkpoint "growth factor applied to the later
# contribution", unit "multiple", a plain ratio).
#
# Balance identity at the horizon:
#       T = P0 * (1+r)^N + C * (1+r)^K
# =>    P0 = (T - C*(1+r)^K) / (1+r)^N              (equivalently T/(1+r)^N - C/(1+r)^(N-K))
#
# How each given number enters:
#   T  ("must reach ... USD")                 -> target balance at the horizon
#   N  ("after N whole annual compounding periods") -> horizon, growth exponent of the initial principal
#   r  ("annual rate ratio")                  -> used as a ratio directly (NOT divided by 100)
#   C  ("later contribution of ... USD")      -> the single extra deposit
#   K  ("exactly K whole periods remain")     -> growth exponent of the contribution (FV factor (1+r)^K)
#
# Conventions / overrides:
#   - Exact compounding with integer exponents -> exact Fraction arithmetic, no rounding inside.
#   - Whole periods only; no fractional-period or simple-interest treatment.
#   - No floor at zero is stated, so the sign is preserved: if the contribution alone would already
#     overshoot the target, the required principal is negative (the formula is applied as worded).
#   - K may exceed N in the generated instances (contribution "before" time 0); the identity above
#     is unchanged because only the growth factors (1+r)^K and (1+r)^N matter.
#   - Final answer is returned unrounded; the framework applies half-up to 2 dp (USD).

from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F  # noqa: F401

TEMPLATE_ID = "h075"


def solve(text: str, q: dict) -> dict:
    target = grab(r"must reach {N} USD", text)
    n_periods = grab(r"USD after {N} whole annual compounding periods", text)
    r = grab(r"annual rate ratio {N}", text)
    contribution = grab(r"later contribution of {N} USD", text)
    k_remain = grab(r"exactly {N} whole periods remain", text)

    if n_periods.denominator != 1 or k_remain.denominator != 1:
        raise ValueError("period counts must be whole numbers")
    n_i = int(n_periods)
    k_i = int(k_remain)

    growth_c = (1 + r) ** k_i            # growth factor on the later contribution
    growth_p = (1 + r) ** n_i            # growth factor on the initial principal

    fv_contribution = contribution * growth_c
    principal = (target - fv_contribution) / growth_p

    return {
        "final": principal,
        "slots": {"later_contribution_growth_checkpoint": growth_c},
    }
