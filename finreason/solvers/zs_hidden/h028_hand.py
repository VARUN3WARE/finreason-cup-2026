from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h028"


def solve(text: str, q: dict) -> dict:
    # Predeal equity value at the fixed price P: predeal shares = V / P.
    equity = grab(r"aggregate reference equity value {N}", text)
    base = grab(r"Upfront base consideration is {N}", text)
    cash_frac = grab(r"excluding the earnout; {N} is paid in cash", text)
    earnout = grab(r"earnout with settlement value {N}", text)
    rate = grab(r"annual pre-tax interest rate {N}", text)
    ni_acq = grab(r"net income is {N} for the acquirer", text)
    ni_tgt = grab(r"for the acquirer and {N} for the target", text)
    syn = grab(r"recurring annual pre-tax synergies of {N}", text)
    tax = grab(r"With tax rate {N}", text)

    cash = base * cash_frac
    stock_upfront = base - cash
    # All deal shares (upfront stock leg + earnout shares) issued at the same price P.
    deal_share_ratio = (stock_upfront + earnout) / equity

    interest = cash * rate  # pre-tax, USD million
    pro_forma_ni = ni_acq + ni_tgt + syn * (1 - tax) - interest * (1 - tax)

    # EPS ratio: (NI_pf / (N*(1+ratio))) / (NI_acq / N)
    accretion = (pro_forma_ni / (ni_acq * (1 + deal_share_ratio)) - 1) * 100

    return {
        "final": Fraction(accretion),
        "slots": {
            "deal_share_issuance_checkpoint": Fraction(deal_share_ratio),
            "pretax_interest_checkpoint": Fraction(interest),
        },
    }
