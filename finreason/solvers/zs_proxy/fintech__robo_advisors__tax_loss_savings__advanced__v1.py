from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.fintech.robo_advisors.tax_loss_savings.advanced.v1"


def solve(text: str, q: dict) -> dict:
    shares = grab(r"{N} shares have cost basis", text)
    basis = grab(r"cost basis {N} USD per share", text)
    price = grab(r"current price {N} USD per share", text)
    rate = grab(r"marginal tax rate is {N} percent", text) / 100
    loss_ps = max(basis - price, Fraction(0))
    eligible = loss_ps * shares
    return {
        "final": eligible * rate,
        "slots": {
            "loss_per_share_trace": loss_ps,
            "eligible_loss_trace": eligible,
            "tax_ratio_trace": rate,
        },
    }
