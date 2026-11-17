from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.financial_markets.option_pricing.one_period_binomial_call.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    spot = grab(r"spot price (?:of )?USD\s*{N}", text)
    strike = grab(r"strike (?:price )?(?:of )?USD\s*{N}", text)
    u = grab(r"up multiplier\s*{N}", text)
    d = grab(r"down multiplier\s*{N}", text)
    r = grab(r"risk-free rate (?:of )?{N}\s*percent", text) / 100
    s_up = spot * u
    s_down = spot * d
    c_up = max(s_up - strike, Fraction(0))
    c_down = max(s_down - strike, Fraction(0))
    q_up = ((1 + r) - d) / (u - d)
    call = (q_up * c_up + (1 - q_up) * c_down) / (1 + r)
    return {
        "final": call,
        "slots": {
            "up_payoff_trace": c_up,
            "down_payoff_trace": c_down,
            "up_probability_trace": q_up,
        },
    }
