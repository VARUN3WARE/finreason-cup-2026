from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.investment_analysis.roi.mutual_fund_total_roi.advanced.v1"


def solve(text: str, q: dict) -> dict:
    shares = grab(r"buys {N} fund shares", text)
    buy = grab(r"fund shares at USD {N} each", text)
    sell = grab(r"sells them at USD {N} each", text)
    dps = grab(r"receives USD {N} per share per year", text)
    years = grab(r"per share per year for {N} years?", text)
    fee = grab(r"annual fee of {N} percent", text)
    initial = shares * buy
    proceeds = shares * sell
    dividends = shares * dps * years
    fees = initial * fee / 100 * years
    net = proceeds - initial + dividends - fees
    roi = net / initial * 100
    return {"final": roi, "slots": {
        "total_dividends_trace": dividends,
        "total_fees_trace": fees,
        "net_profit_trace": net,
    }}
