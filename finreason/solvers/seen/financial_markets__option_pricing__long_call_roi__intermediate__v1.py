from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.financial_markets.option_pricing.long_call_roi.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    premium = grab(r"premium of USD {N}", text)
    strike = grab(r"strike price USD {N}", text)
    spot_t = grab(r"expires when the underlying is USD {N}", text)
    payoff = max(spot_t - strike, Fraction(0))
    net = payoff - premium
    roi = net / premium * 100
    return {
        "final": roi,
        "slots": {"call_payoff_trace": payoff, "net_profit_loss_trace": net},
    }
