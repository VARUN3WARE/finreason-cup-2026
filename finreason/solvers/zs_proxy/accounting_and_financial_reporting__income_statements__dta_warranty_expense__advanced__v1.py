from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.accounting_and_financial_reporting.income_statements.dta_warranty_expense.advanced.v1"


def solve(text: str, q: dict) -> dict:
    expense = grab(r"recognizes {N}\s*USD of warranty expense", text)
    deductible = grab(r"Only {N}\s*USD is deductible", text)
    rate = grab(r"tax rate expected when the difference reverses is {N}\s*percent", text) / 100
    temp_diff = expense - deductible
    dta = temp_diff * rate
    return {
        "final": dta,
        "slots": {
            "temporary_difference_trace": temp_diff,
            "tax_rate_ratio_trace": rate,
        },
    }
