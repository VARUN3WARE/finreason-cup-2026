from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.esg_investing.project_roi.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    inv = grab(r"initial investment of {N} USD", text)
    monthly = grab(r"saves {N} USD per month", text)
    opex = grab(r"incurs {N} USD of annual operating cost", text)
    receives = grab(r"receives {N} USD per year", text)
    years = grab(r"lasts {N} years", text)
    annual = monthly * 12 - opex + receives
    total = annual * years
    ratio = total / inv
    return {
        "final": ratio * 100,
        "slots": {
            "annual_net_savings_trace": annual,
            "total_net_savings_trace": total,
            "roi_ratio_trace": ratio,
        },
    }
