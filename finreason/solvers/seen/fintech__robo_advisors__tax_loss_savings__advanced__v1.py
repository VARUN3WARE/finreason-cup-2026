from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.fintech.robo_advisors.tax_loss_savings.advanced.v1"


def solve(text: str, q: dict) -> dict:
    shares = grab(r"{N}\s*shares have cost basis", text)
    basis = grab(r"cost basis {N}", text)
    price = grab(r"current price {N}", text)
    tax = grab(r"marginal tax rate is {N}\s*percent", text) / 100
    # Loss per share floored at zero (gains produce no loss).
    loss_ps = max(basis - price, Fraction(0))
    eligible = loss_ps * shares
    return {
        "final": eligible * tax,
        "slots": {
            "loss_per_share_trace": loss_ps,
            "eligible_loss_trace": eligible,
            "tax_ratio_trace": tax,
        },
    }
