from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "h001"


def solve(text: str, q: dict) -> dict:
    ca = grab(r"current assets of {N}", text)
    cl = grab(r"current liabilities of {N}", text)
    purchase = grab(r"non-current-asset purchase of {N}", text)
    excess = grab(r"one plus the ratio {N}", text)
    required = 1 + excess
    ca_post = ca - purchase
    # (ca_post + B) / (cl + B) = required  ->  B = (ca_post - required*cl) / (required - 1)
    borrowing = (ca_post - required * cl) / (required - 1)
    return {"final": borrowing, "slots": {"post_purchase_assets_checkpoint": ca_post}}
