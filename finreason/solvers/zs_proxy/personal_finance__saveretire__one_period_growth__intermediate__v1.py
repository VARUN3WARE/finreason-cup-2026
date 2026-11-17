from finreason.nums import grab

TEMPLATE_ID = "fp.personal_finance.saveretire.one_period_growth.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    start = grab(r"Starting savings in USD (?:are|is) {N}", text)
    contrib = grab(r"End-of-period contribution in USD (?:is|are) {N}", text)
    ratio = grab(r"One-period return ratio (?:is|are) {N}", text)
    pre = start + contrib  # per the stated rule: savings plus contribution, then return
    ret = pre * ratio
    return {
        "final": pre + ret,
        "slots": {"pre_return_balance_usd": pre, "return_amount_usd": ret},
    }
