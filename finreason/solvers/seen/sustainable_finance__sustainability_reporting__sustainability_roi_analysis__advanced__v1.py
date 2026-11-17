from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.sustainability_reporting.sustainability_roi_analysis.advanced.v1"


def solve(text: str, q: dict) -> dict:
    invest = grab(r"initial investment {N} USD", text)
    energy = grab(r"annual energy savings {N} USD", text)
    waste = grab(r"annual waste savings {N} USD", text)
    tax = grab(r"tax credit of {N} percent", text) / 100
    extra = grab(r"extra operational saving of {N} percent", text) / 100
    years = grab(r"period is {N} years?", text)
    base = energy + waste
    # Tax credit and operational saving each apply independently to the base (additive, not compounded).
    total_annual = base + base * tax + base * extra
    net = total_annual * years - invest
    roi = net / invest * 100
    return {
        "final": roi,
        "slots": {
            "base_annual_savings_trace": base,
            "total_annual_savings_trace": total_annual,
            "net_period_benefit_trace": net,
        },
    }
