"""h079 -- reverse EV bridge: target equity -> EV -> required normalized EBITDA -> reported EBITDA.

Literal transcription of the question, sentence by sentence.
"""
from fractions import Fraction

from finreason.nums import grab, F  # noqa: F401

TEMPLATE_ID = "h079"


def solve(text: str, q: dict) -> dict:
    # S1: "A buyer wants a target equity value of X."
    target_equity = grab(r"target equity value of (?:USD\s*)?{N}", text)

    # S2: "The company has total debt of D and cash of C, which are the only
    #      enterprise-value-to-equity-value adjustments in this scenario,
    #      and the buyer values normalized EBITDA at M."
    total_debt = grab(r"total debt of (?:USD\s*)?{N}", text)
    cash = grab(r"cash of (?:USD\s*)?{N}", text)
    multiple = grab(r"values normalized EBITDA at {N}", text)

    # S3: "Due diligence expects a recurring EBITDA deduction of R from the reported figure."
    #     => normalized EBITDA = reported EBITDA - deduction
    deduction = grab(r"recurring EBITDA deduction of (?:USD\s*)?{N}", text)

    # S4: "first bridge equity value to enterprise value using net debt"
    #     net debt = total debt - cash (debt and cash are the only adjustments; sign kept,
    #     so net cash reduces enterprise value)
    net_debt = total_debt - cash
    enterprise_value = target_equity + net_debt

    # "infer required normalized EBITDA" : EV = multiple * normalized EBITDA
    required_normalized_ebitda = enterprise_value / multiple

    # "then restore the deduction" : reported = normalized + deduction
    min_reported_ebitda = required_normalized_ebitda + deduction

    return {
        "final": min_reported_ebitda,
        "slots": {"net_debt_checkpoint": net_debt},
    }
