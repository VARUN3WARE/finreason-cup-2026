from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.accounting_and_financial_reporting.depreciation_and_amortization.impairment_with_value_in_use.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    cost = grab(r"historical cost (?:of )?(?:USD )?{N}", text)
    acc_dep = grab(r"accumulated depreciation (?:of )?(?:USD )?{N}", text)
    fvlcd = grab(r"fair value less costs (?:of disposal |to sell )?(?:is |of )?(?:USD )?{N}", text)
    viu = grab(r"value in use (?:is |of )?(?:USD )?{N}", text)
    carrying = cost - acc_dep  # trace_1
    recoverable = max(fvlcd, viu)  # trace_2
    loss = max(Fraction(0), carrying - recoverable)
    return {"final": loss, "slots": {"trace_1": carrying, "trace_2": recoverable}}
