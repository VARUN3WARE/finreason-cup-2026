"""Hidden cluster h112 -- DeFi liquidity position: fee yield, impermanent loss, optional hedge.

Structure (one common annual period, every ratio is a fraction of position capital):
    fee income (USD)        = capital * fee_yield_ratio
    unhedged IL (USD)       = capital * il_ratio                      <- "the exact unhedged loss"
    covered loss ratio      = hedge_coverage * il_ratio               <- checkpoint (ratio of capital)
    hedged residual IL      = capital * (il_ratio - covered ratio)    = (1 - coverage) * unhedged IL
    hedge cost (USD)        = hedge_cost_ratio * capital              (only when activated)
    activate hedge          <=> unhedged IL (USD) > risk limit (USD)  (STRICT)
    selected net (USD)      = fee income - unhedged IL                          (not activated)
                            = fee income - hedged residual IL - hedge cost      (activated)

AMBIGUITIES CONSIDERED AND HOW EACH WAS RESOLVED
1. Base of the ratios. "fee-yield ratio" / "impermanent-loss ratio" / "costs 0.05 of capital":
   all are ratios of position capital, converted to USD by multiplying by capital. The fee ratio
   is applied to the original capital, not to capital net of the loss (nothing in the text says
   fees accrue on a reduced base).
2. "that loss" in "An optional hedge covers 0.8 of that loss" is the impermanent loss. The hedge
   therefore removes coverage * IL and leaves (1 - coverage) * IL; coverage is NOT a cap, a
   deductible, or a payout independent of the loss size.
3. Hedge cost: "only when activated, costs 0.05 of capital" -> hedge_cost_ratio * capital, charged
   only in the activated branch; the unhedged branch pays nothing ("pay no hedge cost").
4. Trigger quantity: "the exact unhedged loss" is the impermanent loss in USD without any hedge,
   NOT the net result (fees minus loss) and NOT a rounded figure. It is compared with the risk
   limit, which is stated in USD, so the comparison is capital*il_ratio  vs  limit (both USD).
5. Comparison: "strictly exceeds" -> strict '>' ; equality leaves the position unhedged.
6. "selected net profit or loss" = the branch the rule selects, NOT max(hedged, unhedged).
   (Instance 3 makes the hedged branch worse than the unhedged one, but the rule still requires
   activation because the loss exceeds the limit -- we follow the rule.)
7. Net result "excluding return of the original capital": fee income minus loss (minus hedge
   cost when activated); sign preserved (negative if a net loss).
8. Checkpoint "covered impermanent loss as a ratio of position capital" = coverage * il_ratio,
   i.e. (coverage * IL in USD) / capital. It is a property of the hedge computed at position 1,
   BEFORE the activation branch, so it is reported whether or not the hedge is activated (it is
   not zeroed in the unhedged branch). Instance 2 (0.333335 * 0.3 = 0.1000005) is an engineered
   half-up tie at exactly 6 decimals, which confirms this product is the intended quantity.
9. Rounding: nothing is rounded inside the computation; exact Fractions are returned and the
   framework applies half-up rounding (2 dp USD final, 6 dp ratio checkpoint).
10. Period: "one common annual period" -> single period, no compounding / annualisation.
"""

from __future__ import annotations

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h112"


def _parse(text: str) -> dict[str, Fraction]:
    capital = grab(r"capital\s+of\s+{N}\s*USD", text)
    fee_yield = grab(r"fee-?\s*yield\s+ratio\s+(?:of\s+)?{N}", text)
    il_ratio = grab(r"impermanent-?\s*loss\s+ratio\s+(?:of\s+)?{N}", text)
    coverage = grab(r"hedge\s+covers\s+{N}\s+of\s+(?:that|the)\s+loss", text)
    hedge_cost_ratio = grab(r"costs\s+{N}\s+of\s+(?:the\s+)?capital", text)
    risk_limit = grab(r"risk\s+limit\s+of\s+{N}\s*USD", text)
    return {
        "capital": capital,
        "fee_yield": fee_yield,
        "il_ratio": il_ratio,
        "coverage": coverage,
        "hedge_cost_ratio": hedge_cost_ratio,
        "risk_limit": risk_limit,
    }


def solve(text: str, q: dict) -> dict:
    p = _parse(text)
    capital = p["capital"]

    # USD amounts over the single common period.
    fee_income = capital * p["fee_yield"]
    unhedged_loss = capital * p["il_ratio"]  # "the exact unhedged loss" (USD)

    # Checkpoint: covered impermanent loss as a ratio of position capital (branch-independent).
    covered_loss_ratio = p["coverage"] * p["il_ratio"]
    covered_loss_usd = capital * covered_loss_ratio

    # Hedged branch quantities.
    residual_loss = unhedged_loss - covered_loss_usd  # = (1 - coverage) * unhedged_loss
    hedge_cost = p["hedge_cost_ratio"] * capital

    # Rule: activate the hedge only if the exact unhedged loss STRICTLY exceeds the risk limit.
    activate = unhedged_loss > p["risk_limit"]

    if activate:
        net = fee_income - residual_loss - hedge_cost
    else:
        net = fee_income - unhedged_loss  # no hedge cost

    return {
        "final": net,
        "slots": {"covered_loss_ratio_checkpoint": covered_loss_ratio},
    }
