"""h019: maximum common stress activity allowed by capital, leverage and liquidity constraints.

k = minimum capital ratio + capital buffer ratio
cap_capital   = (EC - k*RWA) / (ec_loss + k*rwa_inc)
cap_leverage  = (T1 - lev_min*EXP) / (t1_loss + lev_min*exp_inc)
cap_liquidity = (HQLA - liq_min*NCO) / (hqla_loss + liq_min*nco_inc)
final = min(cap_capital, cap_leverage, cap_liquidity)   (literal "smallest of the three capacities")
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h019"


def _coef(pattern: str, text: str) -> Fraction:
    # coefficients are written like "by 3*x" / "by 0.5*x"
    return grab(pattern + r" by {N}\s*\*\s*x", text)


def solve(text: str, q: dict) -> dict:
    ec = grab(r"eligible capital {N}", text)
    t1 = grab(r"Tier 1 capital {N}", text)
    rwa = grab(r"risk-weighted assets {N}", text)
    exposure = grab(r"total exposure {N}", text)
    hqla = grab(r"high-quality liquid assets {N}", text)
    nco = grab(r"total net cash outflows {N}", text)

    min_cap = grab(r"minimum capital ratio {N}", text)
    buffer = grab(r"capital buffer ratio {N}", text)
    min_lev = grab(r"minimum leverage ratio {N}", text)
    min_liq = grab(r"minimum liquidity ratio {N}", text)

    ec_loss = _coef(r"eligible capital", text)
    t1_loss = _coef(r"Tier 1 capital", text)
    rwa_inc = _coef(r"risk-weighted assets", text)
    exp_inc = _coef(r"exposure", text)
    hqla_loss = _coef(r"HQLA", text)
    nco_inc = _coef(r"net cash outflows", text)

    k = min_cap + buffer

    cap_capital = (ec - k * rwa) / (ec_loss + k * rwa_inc)
    cap_leverage = (t1 - min_lev * exposure) / (t1_loss + min_lev * exp_inc)
    cap_liquidity = (hqla - min_liq * nco) / (hqla_loss + min_liq * nco_inc)

    final = min(cap_capital, cap_leverage, cap_liquidity)

    return {
        "final": final,
        "slots": {"combined_capital_requirement_ratio_checkpoint": k},
    }
