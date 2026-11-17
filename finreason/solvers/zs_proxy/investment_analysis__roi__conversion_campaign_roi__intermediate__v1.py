from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.investment_analysis.roi.conversion_campaign_roi.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    imps = grab(r"receives {N} impressions", text)
    ctr = grab(r"click-through rate of {N} percent", text)
    conv = grab(r"conversion rate of {N} percent", text)
    aov = grab(r"average revenue of USD {N} per sale", text)
    spend = grab(r"costs USD {N}", text)
    clicks = imps * ctr / 100
    sales = clicks * conv / 100
    revenue = sales * aov
    roi = (revenue - spend) / spend * 100
    return {"final": roi, "slots": {
        "expected_clicks_trace": clicks,
        "expected_sales_trace": sales,
        "campaign_revenue_trace": revenue,
    }}
