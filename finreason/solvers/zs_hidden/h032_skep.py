"""Hidden cluster h032 -- maximum management fee under Sharpe and Jensen-alpha floors.

AMBIGUITIES CONSIDERED AND RESOLUTIONS (all from the question text):

1. What the fee does.  "net return equals gross return minus the fee; it does not change
   volatility, beta, the market return, or the risk-free rate."  => R_net = G - f, every
   other input unchanged.  Fee f is a rate in the same (ratio) units as the returns.

2. Sharpe constraint.  Standard Sharpe = (R_net - rf) / sigma, with sigma the (unchanged)
   volatility and rf the stated risk-free rate.  "at least S" is NON-strict, so the bound
   f <= G - rf - S*sigma is attainable and the bound itself is the maximum.

3. Jensen's alpha constraint.  alpha = R_net - [rf + beta*(Rm - rf)].  "at least A" is
   NON-strict, so f <= G - rf - beta*(Rm - rf) - A, attainable.

4. Combining the constraints.  "maximum ... rate that satisfies both constraints" => the
   feasible set is f <= min(bound_sharpe, bound_alpha); the maximum is that min.  Which
   constraint binds is the branch that differs across instances.

5. Floor at zero?  The text never says the fee is non-negative or that an infeasible
   gross portfolio yields a zero fee.  "Test both constraints using the unrounded exact
   rate" only asks that both hold at the reported rate, which the min satisfies by
   construction even when negative.  One instance is engineered so the Sharpe bound is an
   exact -1.495% rounding tie, which only matters if that unfloored bound IS the answer.
   => no floor; a negative maximum fee is reported as a negative percentage.

6. Units.  Inputs are plain ratios (0.092 etc.); answer unit is "percent" => fee*100.
   The framework performs the half-up rounding to 2 dp (negative values included), so the
   solver returns the exact unrounded Fraction.

7. Checkpoint "market risk premium used by the alpha constraint", unit ratio.  The
   market risk premium is (Rm - rf), NOT beta*(Rm - rf) (that would be the portfolio's
   systematic premium) and not the gross or net excess return.  Returned as a ratio.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h032"


def solve(text: str, q: dict) -> dict:
    gross = grab(r"gross expected return\s+{N}", text)
    sigma = grab(r"volatility\s+{N}", text)
    beta = grab(r"beta\s+{N}", text)
    rm = grab(r"market return is\s+{N}", text)
    rf = grab(r"risk-free rate is\s+{N}", text)
    s_min = grab(r"Sharpe ratio of at least\s+{N}", text)
    a_min = grab(r"Jensen'?s alpha of at least\s+{N}", text)

    # Market risk premium used in Jensen's alpha: Rm - rf (ratio).
    mrp = rm - rf

    # Sharpe: (G - f - rf)/sigma >= S  <=>  f <= G - rf - S*sigma
    bound_sharpe = gross - rf - s_min * sigma
    # Alpha: (G - f) - rf - beta*(Rm - rf) >= A  <=>  f <= G - rf - beta*(Rm - rf) - A
    bound_alpha = gross - rf - beta * mrp - a_min

    fee = min(bound_sharpe, bound_alpha)  # exact, unfloored (see ambiguity 5)

    # Sanity: both constraints hold at the exact rate (non-strict).
    net = gross - fee
    assert (net - rf) / sigma >= s_min
    assert net - rf - beta * mrp >= a_min

    return {
        "final": fee * 100,  # percent
        "slots": {"market_premium_checkpoint": mrp},
    }
