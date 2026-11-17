from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.investment_analysis.rar.two_asset_perfect_correlation_sd.basic.v1"


def solve(text: str, q: dict) -> dict:
    # Weights converted from percent to ratios; standard deviations kept in percent.
    wa = grab(r"(?i)asset A has weight {N} percent", text) / 100
    sa = grab(r"(?i)asset A has weight {N} percent and standard deviation {N} percent", text, group=2)
    wb = grab(r"(?i)asset B has weight {N} percent", text) / 100
    sb = grab(r"(?i)asset B has weight {N} percent and standard deviation {N} percent", text, group=2)
    ca = wa * sa
    cb = wb * sb
    variance = (ca + cb) ** 2  # percent-squared units
    sigma = abs(ca + cb)  # exact nonnegative square root of a perfect rational square
    return {
        "final": sigma,
        "slots": {
            "weighted_sd_a_trace": ca,
            "weighted_sd_b_trace": cb,
            "variance_trace": variance,
        },
    }
