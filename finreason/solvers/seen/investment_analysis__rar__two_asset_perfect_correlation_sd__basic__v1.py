from fractions import Fraction

from finreason.nums import grab_all

TEMPLATE_ID = "fp.investment_analysis.rar.two_asset_perfect_correlation_sd.basic.v1"


def solve(text: str, q: dict) -> dict:
    wa, sa = grab_all(r"Asset A has weight {N} percent and standard deviation {N} percent", text)
    wb, sb = grab_all(r"asset B has weight {N} percent and standard deviation {N} percent", text)
    # Weights as decimals, standard deviations kept in percentage points.
    ca = wa / 100 * sa
    cb = wb / 100 * sb
    combined = ca + cb
    variance = combined ** 2
    # Nonnegative square root of an exact square is the absolute value (exact).
    sigma_p = abs(combined)
    return {
        "final": sigma_p,
        "slots": {
            "weighted_sd_a_trace": ca,
            "weighted_sd_b_trace": cb,
            "variance_trace": variance,
        },
    }
