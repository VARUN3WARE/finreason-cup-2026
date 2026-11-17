from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.financial_markets.option_pricing.one_period_binomial_call.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    spot = grab(r"spot price USD {N}", text)
    strike = grab(r"strike USD {N}", text)
    u = grab(r"up multiplier {N}", text)
    d = grab(r"down multiplier {N}", text)
    r = grab(r"risk-free rate {N} percent", text) / 100
    s_up = spot * u
    s_down = spot * d
    c_up = max(s_up - strike, Fraction(0))
    c_down = max(s_down - strike, Fraction(0))
    qu = ((1 + r) - d) / (u - d)
    value = (qu * c_up + (1 - qu) * c_down) / (1 + r)
    return {
        "final": value,
        "slots": {
            "up_payoff_trace": c_up,
            "down_payoff_trace": c_down,
            "up_probability_trace": qu,
        },
    }
