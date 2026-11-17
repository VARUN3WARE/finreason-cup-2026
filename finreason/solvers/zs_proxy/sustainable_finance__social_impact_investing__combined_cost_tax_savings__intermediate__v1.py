from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.social_impact_investing.combined_cost_tax_savings.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    op_cost = grab(r"operating cost {N} USD", text)
    red_pct = grab(r"reduces it by {N} percent", text)
    expenses = grab(r"[Pp]roject expenses are {N} USD", text)
    credit_pct = grab(r"tax credit of {N} percent", text)
    savings = op_cost * red_pct / 100
    credit = expenses * credit_pct / 100
    return {"final": savings + credit,
            "slots": {"operating_savings_trace": savings, "tax_credit_trace": credit}}
