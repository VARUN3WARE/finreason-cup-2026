"""h022 -- target sellers' post-earnout ownership of acquirer common-share base (literal transcription)."""
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h022"


def solve(text: str, q: dict) -> dict:
    # "the acquirer's predeal common shares have aggregate reference equity value {N} at one fixed contractual share price"
    predeal_value = grab(r"predeal common shares have aggregate reference equity value {N}", text)
    # One fixed contractual share price; any positive price cancels in the ownership ratio.
    price = Fraction(1)
    predeal_shares = predeal_value / price

    # "Upfront base consideration is {N}, excluding the earnout"
    base = grab(r"Upfront base consideration is {N}", text)
    # "{N} of that base is paid in cash and the remainder in acquirer common shares"
    cash_fraction = grab(r"{N} of that base is paid in cash", text)
    upfront_cash = base * cash_fraction
    upfront_stock = base - upfront_cash          # usd_million checkpoint
    upfront_shares = upfront_stock / price

    # Sellers retain all upfront shares through the measurement date.
    seller_upfront_shares = upfront_shares

    # "A fully realized earnout with settlement value {N}, incremental to the base consideration,
    #  is also settled entirely in common shares at the same unchanged price."
    earnout_value = grab(r"earnout with settlement value {N}", text)
    earnout_shares = earnout_value / price

    # No other issuance, repurchase, disposal, option exercise, conversion, or price adjustment.
    seller_shares = seller_upfront_shares + earnout_shares
    total_shares = predeal_shares + upfront_shares + earnout_shares

    ownership_pct = seller_shares / total_shares * 100

    return {
        "final": ownership_pct,
        "slots": {"upfront_stock_consideration_checkpoint": upfront_stock},
    }
