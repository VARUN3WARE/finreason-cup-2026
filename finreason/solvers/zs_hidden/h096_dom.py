# FINANCE MODEL (h096)
# Quantities:
#   A  = high-risk allocation the firm must support (USD)
#   b  = diversification buffer ratio (0.2)  -> target is increased by b BEFORE the risk-appetite ratio is applied
#   r  = risk-appetite ratio: the fraction of the allocable capital pool that may be committed to the high-risk
#        allocation (so pool = high-risk need / r)
#   R  = reserve kept OUTSIDE the allocable capital pool (additive, NOT scaled by r)
#
# Chain:
#   1. buffered target  T = A * (1 + b)                       (checkpoint: buffered_target_checkpoint, USD)
#   2. minimum allocable pool needed to fund T at risk-appetite r:  P = T / r
#   3. total capital required = P + R   (reserve sits outside the pool, so it is added unscaled)
#
# Conventions / overrides noted:
#   - "increases the allocation target by ratio 0.2" is read as multiplication by (1 + 0.2), not 1/(1-0.2).
#   - "risk-appetite ratio" is a capacity fraction of the pool, hence division (minimum capital to fund T).
#   - Reserve is outside the pool: added after the division.
#   - No intermediate rounding; the framework half-up-rounds the final answer and the checkpoint to 2 dp.
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h096"


def solve(text: str, q: dict) -> dict:
    A = grab(r"high-risk allocation of {N}", text)
    r = grab(r"risk-appetite ratio {N}", text)
    b = grab(r"diversification buffer ratio {N}", text)
    R = grab(r"keeps {N} outside the allocable capital pool", text)

    target = A * (1 + b)
    pool = target / r
    total = pool + R

    return {"final": total, "slots": {"buffered_target_checkpoint": target}}
