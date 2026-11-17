from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h096"


def solve(text: str, q: dict) -> dict:
    alloc = grab(r"high-risk allocation of {N}", text)
    appetite = grab(r"risk-appetite ratio {N}", text)
    buffer = grab(r"diversification buffer ratio {N}", text)
    reserve = grab(r"keeps {N} outside the allocable capital pool", text)

    # Buffer is applied to the allocation target before the risk-appetite ratio.
    buffered = alloc * (1 + buffer)
    # Risk appetite: high-risk allocation may be at most `appetite` share of the allocable pool,
    # so the minimum allocable pool is buffered / appetite; reserve sits outside that pool.
    allocable = buffered / appetite
    total = allocable + reserve
    return {"final": Fraction(total), "slots": {"buffered_target_checkpoint": Fraction(buffered)}}
