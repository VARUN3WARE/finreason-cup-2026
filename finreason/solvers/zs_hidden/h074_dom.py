"""h074 -- green / conventional two-tranche bond financing, maximum total principal under a repayment cap.

FINANCE MODEL
-------------
Let P be the total financing principal (USD).
  s   = green share of total principal (given: "receives share s"); conventional share = 1 - s ("remaining principal").
  rg  = green annual yield ratio (a plain ratio, e.g. 0.05 = 5% p.a.), ng = number of annual compounding periods.
  rc  = conventional annual yield ratio, nc = its number of annual periods.
Standard annual compounding: maturity factor of a tranche = (1 + r) ** n   (multiple of principal at maturity).
  Fg = (1 + rg) ** ng        <- slot "green_maturity_factor_checkpoint" ("full-term compound factor for the green tranche")
  Fc = (1 + rc) ** nc
Text defines: total maturity repayment = (green principal share) * Fg + (conventional principal share) * Fc
  -- read as per-unit-of-total-principal weights s and (1 - s), i.e. blended factor B = s*Fg + (1-s)*Fc,
  so Repayment(P) = P * B   (linear in P).
Constraint: Repayment(P) = cap exactly  =>  P_max = cap / B  (the "maximum" principal is the one meeting the cap with
equality since Repayment is increasing in P).
Overrides / conventions: none; yields are ratios (not percents); no rounding inside the chain; framework rounds the
final value half-up to 2 dp (USD) and the checkpoint half-up to 8 dp (multiple).
"""
from fractions import Fraction

from finreason.nums import grab, F  # noqa: F401

TEMPLATE_ID = "h074"


def solve(text: str, q: dict) -> dict:
    s = grab(r"green tranche receives share {N}", text)
    rg, ng = None, None
    # green tranche: yield ratio and periods (first "yield ratio ... compounds for ... periods" after the green tranche)
    rg = grab(r"green tranche receives share.*?earns annual yield ratio {N}", text)
    ng = grab(r"green tranche receives share.*?compounds for {N} annual periods", text)
    rc = grab(r"conventional tranche,\s*which earns annual yield ratio {N}", text)
    nc = grab(r"conventional tranche,.*?compounds for {N} annual periods", text)
    cap = grab(r"cap {N}", text)

    assert ng.denominator == 1 and nc.denominator == 1
    fg = (1 + rg) ** int(ng)
    fc = (1 + rc) ** int(nc)
    blended = s * fg + (1 - s) * fc
    principal = cap / blended
    return {"final": principal, "slots": {"green_maturity_factor_checkpoint": fg}}
