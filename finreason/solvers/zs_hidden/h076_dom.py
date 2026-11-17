# FINANCE MODEL (h076): Tier 1 adjustment x needed to satisfy both a risk-based capital
# constraint (with buffer) and a leverage constraint.
#
#   combined_ratio = minimum_capital_ratio + capital_buffer_ratio          (checkpoint, ratio)
#   Total eligible capital = Tier1 + Tier2.  A Tier 1 adjustment x raises Tier 1 AND total
#   capital by x; Tier 2, RWA and exposure are fixed.
#   Risk-based constraint:  (Tier1 + Tier2 + x) / RWA >= combined_ratio
#        => x >= combined_ratio * RWA - (Tier1 + Tier2)           (stated in the text)
#   Leverage constraint:    (Tier1 + x) / total_exposure >= minimum_leverage_ratio
#        => x >= minimum_leverage_ratio * total_exposure - Tier1  (stated in the text)
#   x = max(capital gap, leverage gap)  -- "the larger gap", sign preserved (no floor at zero):
#        x > 0 : issuance required; x = 0 : exactly binding; x < 0 : withdrawal of -x permitted.
#   Units: all USD millions; ratios are plain decimal ratios (0.08 = 8%), no percent conversion.
#   Checkpoint is the exact unrounded combined ratio (framework rounds to 6 dp half-up);
#   the exact unrounded value is used downstream. Final x rounded half-up to 2 dp by framework.
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h076"


def solve(text: str, q: dict) -> dict:
    t1 = grab(r"eligible Tier 1 capital\s+{N}", text)
    t2 = grab(r"eligible Tier 2 capital\s+{N}", text)
    rwa = grab(r"risk-weighted assets\s+{N}", text)
    expo = grab(r"total exposure\s+{N}", text)
    min_ratio = grab(r"minimum capital ratio\s+{N}", text)
    buffer_ratio = grab(r"capital buffer ratio\s+{N}", text)
    lev_ratio = grab(r"minimum leverage ratio\s+{N}", text)

    combined = min_ratio + buffer_ratio
    capital_gap = combined * rwa - (t1 + t2)
    leverage_gap = lev_ratio * expo - t1
    x = max(capital_gap, leverage_gap)

    return {
        "final": x,
        "slots": {"combined_capital_requirement_ratio_checkpoint": combined},
    }
