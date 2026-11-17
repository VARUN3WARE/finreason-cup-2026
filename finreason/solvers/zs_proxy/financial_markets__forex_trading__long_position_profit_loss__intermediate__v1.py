from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.financial_markets.forex_trading.long_position_profit_loss.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    units = grab(r"buys {N} base-currency units", text)
    open_px = grab(r"units at USD {N} per unit", text)
    close_px = grab(r"closes the long position at USD {N} per unit", text)
    pip = grab(r"One pip is a quote change of USD {N} per unit", text)
    change = close_px - open_px                 # signed quote movement (USD per unit)
    pips = change / pip                         # signed pip difference
    pip_value = pip * units                     # USD per pip
    pl = pips * pip_value
    return {
        "final": pl,
        "slots": {
            "quote_change_trace": change,
            "pip_difference_trace": pips,
            "pip_value_trace": pip_value,
        },
    }
