"""h011 -- net economic exposure percentage (literal transcription)."""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h011"


def solve(text: str, q: dict) -> dict:
    # "an investor has {N} direct long shares"
    direct_long = grab(r"has {N} direct long shares", text)
    # "{N} shares attributed through related holdings"
    attributed = grab(r"{N} shares attributed through related holdings", text)
    # "derivative notional equivalent to {N} shares with exposure delta {N}"
    deriv_ref_shares = grab(r"derivative notional equivalent to {N} shares", text)
    delta = grab(r"exposure delta {N}", text)
    # "The investor also has {N} shares of offsetting short exposure."
    short_hedge = grab(r"{N} shares of offsetting short exposure", text)
    # "The issuer has {N} shares outstanding."
    shares_out = grab(r"issuer has {N} shares outstanding", text)

    # "Multiply derivative reference shares by delta"
    deriv_equiv = deriv_ref_shares * delta
    # "add all long exposure"
    total_long = direct_long + attributed + deriv_equiv
    # "subtract the short hedge" (signed result, no floor)
    signed_net = total_long - short_hedge
    # "divide the signed result by shares outstanding"
    ratio = signed_net / shares_out
    # "convert the ratio to a percentage"
    pct_exposure = ratio * 100

    return {
        "final": Fraction(pct_exposure),
        "slots": {"derivative_equivalent_checkpoint": Fraction(deriv_equiv)},
    }
