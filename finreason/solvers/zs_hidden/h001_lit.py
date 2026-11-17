"""Cluster h001 -- literal transcription solver.

Structure: current assets / current liabilities, a cash-funded non-current-asset
purchase reduces current assets, required current ratio = 1 + ratio, and the
maximum short-term borrowing B added to BOTH cash (current assets) and current
liabilities such that the ratio exactly meets the requirement:
    (CA_post + B) / (CL + B) = R   =>   B = (CA_post - R * CL) / (R - 1)
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h001"


def solve(text: str, q: dict) -> dict:
    # "A company has current assets of X and current liabilities of Y in USD millions."
    current_assets = grab(r"current assets of {N}", text)
    current_liabilities = grab(r"current liabilities of {N}", text)

    # "It plans a cash-funded non-current-asset purchase of P, which reduces current
    #  assets by the purchase amount."
    purchase = grab(r"non-current-asset purchase of {N}", text)
    post_purchase_assets = current_assets - purchase

    # "The required current ratio is one plus the ratio r."
    ratio_add = grab(r"required current ratio is one plus the ratio {N}", text)
    required_ratio = Fraction(1) + ratio_add

    # "Determine the maximum additional short-term borrowing that can be added to both
    #  cash and current liabilities while exactly meeting the required current ratio."
    #   (CA_post + B) / (CL + B) = R
    borrowing = (post_purchase_assets - required_ratio * current_liabilities) / (required_ratio - 1)

    # sanity: the ratio is exactly met
    assert (post_purchase_assets + borrowing) / (current_liabilities + borrowing) == required_ratio

    return {
        "final": borrowing,
        "slots": {"post_purchase_assets_checkpoint": post_purchase_assets},
    }
