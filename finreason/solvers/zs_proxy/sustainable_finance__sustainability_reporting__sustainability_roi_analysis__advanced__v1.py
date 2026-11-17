from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.sustainability_reporting.sustainability_roi_analysis.advanced.v1"


def solve(text: str, q: dict) -> dict:
    inv = grab(r"initial investment (?:of )?(?:USD )?{N}", text)
    energy = grab(r"annual energy savings (?:of )?(?:USD )?{N}", text)
    waste = grab(r"annual waste savings (?:of )?(?:USD )?{N}", text)
    tax = grab(r"tax credit of {N}\s*percent", text) / 100
    extra = grab(r"extra operational saving of {N}\s*percent", text) / 100
    years = grab(r"period is {N}\s*years?", text)
    base = energy + waste
    # both additions apply independently (not compounded) to the combined base
    total_annual = base + base * tax + base * extra
    net = total_annual * years - inv
    roi = net / inv * 100
    return {
        "final": roi,
        "slots": {
            "base_annual_savings_trace": base,
            "total_annual_savings_trace": total_annual,
            "net_period_benefit_trace": net,
        },
    }
