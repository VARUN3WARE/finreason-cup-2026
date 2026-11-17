from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.esg_investing.project_roi.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    inv = grab(r"initial investment of\s+{N}\s+USD", text)
    monthly = grab(r"saves\s+{N}\s+USD per month", text)
    opcost = grab(r"incurs\s+{N}\s+USD of annual operating cost", text)
    credit = grab(r"receives\s+{N}\s+USD per year", text)
    years = grab(r"lasts\s+{N}\s+years?", text)
    annual_net = monthly * 12 - opcost + credit
    total_net = annual_net * years
    ratio = total_net / inv
    return {
        "final": ratio * 100,
        "slots": {
            "annual_net_savings_trace": annual_net,
            "total_net_savings_trace": total_net,
            "roi_ratio_trace": ratio,
        },
    }
