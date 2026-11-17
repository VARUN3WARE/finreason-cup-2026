from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.social_impact_investing.combined_cost_tax_savings.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    op_cost = grab(r"operating cost (?:of )?(?:USD )?{N}", text)
    red = grab(r"reduces it by {N} percent", text) / 100
    expenses = grab(r"[Pp]roject expenses (?:are|of) (?:USD )?{N}", text)
    credit_rate = grab(r"tax credit (?:of|equal to) {N} percent", text) / 100
    op_savings = op_cost * red
    tax_credit = expenses * credit_rate
    return {
        "final": op_savings + tax_credit,
        "slots": {"operating_savings_trace": op_savings, "tax_credit_trace": tax_credit},
    }
