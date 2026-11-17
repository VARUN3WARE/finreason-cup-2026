"""h076: signed Tier 1 adjustment x satisfying combined-capital and leverage constraints.

x = max(combined_ratio * RWA - (Tier1 + Tier2),  min_leverage * exposure - Tier1)
combined_ratio = minimum capital ratio + capital buffer ratio (exact).
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h076"

_PRE = r"(?:\s+(?:of|is|was|=|at))?\s*(?:USD\s*)?(?:\$\s*)?"


def _g(label: str, text: str) -> Fraction:
    return grab(label + _PRE + r"{N}", text)


def solve(text: str, q: dict) -> dict:
    t1 = _g(r"eligible Tier 1 capital", text)
    t2 = _g(r"eligible Tier 2 capital", text)
    rwa = _g(r"risk-weighted assets", text)
    exposure = _g(r"total exposure", text)
    min_cap = _g(r"minimum capital ratio", text)
    buffer = _g(r"capital buffer ratio", text)
    min_lev = _g(r"minimum leverage ratio", text)

    combined = min_cap + buffer
    capital_gap = combined * rwa - (t1 + t2)
    leverage_gap = min_lev * exposure - t1
    x = max(capital_gap, leverage_gap)

    return {
        "final": x,
        "slots": {"combined_capital_requirement_ratio_checkpoint": combined},
    }
