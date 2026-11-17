"""h081 -- two-strategy allocation: feasible weight interval + endpoint choice by expected value.

Structure (all three instances):
  capital C split w -> Strategy A, (1-w) -> Strategy B.
  P(downturn) = p_d, P(upside) = p_u = 1 - p_d.
  B: upside factor 1 + r_Bu, downturn factor 1 - l_Bd.
  A: upside factor 1 + r_Bu + inc_u, downturn factor 1 - (l_Bd + inc_d).
  Portfolio upside  V_up(w) = C * ((1 + r_Bu) + w * inc_u)      >= U   -> lower endpoint w_lo
  Portfolio downturn V_dn(w) = C * ((1 - l_Bd) - w * inc_d)      >= D   -> upper endpoint w_hi
  E_A = C * (p_u * (1 + r_Bu + inc_u) + p_d * (1 - l_Bd - inc_d)), E_B = C * (p_u * (1 + r_Bu) + p_d * (1 - l_Bd))
  E_A > E_B (strict)  -> choose w_hi ; otherwise (incl. exact tie) -> choose w_lo.
  Final = chosen w * 100 (percent, unrounded; framework rounds half-up to 2 dp).

AMBIGUITIES CONSIDERED AND RESOLVED (textual evidence in parentheses):
 A1. Returns/losses are decimal RATES (0.1 = 10%), not USD amounts and not percent numbers
     ("both resulting Strategy A rates remain below one"; "earns upside return 0.1"). A loss stated as a positive
     number is subtracted: downturn factor = 1 - loss. Robustness: if a number is followed by "%"/"percent" the
     solver divides by 100.
 A2. Probabilities are decimals; the upside probability is the exact complement 1 - p_d ("with the complementary
     probability assigned to the upside scenario"). Robustness: an "upside probability" phrasing is also accepted
     and complemented.
 A3. Strategy A's rates are ADDITIVE on B's rates ("the B upside return plus positive incremental return",
     "the B downturn loss plus positive incremental loss"), i.e. factor 1 - (l_Bd + inc_d), not (1-l_Bd)(1-inc_d).
 A4. Requirements are "at least" -> non-strict (>=), so each endpoint is the EQUALITY solution of the respective
     constraint, and the endpoint itself is feasible.
 A5. Which requirement gives which endpoint: the text states it explicitly (upside -> lower, downturn -> upper), and
     with positive incremental return/loss it is also mathematically forced (V_up increases in w, V_dn decreases).
     The solver derives the direction from the sign of the w-coefficient so it is faithful either way.
 A6. The ending values are linear weighted combinations with no interaction/leverage/fees/rebalancing (stated), so
     V(w) = C * (w * factor_A + (1 - w) * factor_B) -- no compounding, no per-period rebalancing.
 A7. Selection comparison: strictly greater -> upper endpoint; "otherwise, including an exact tie" -> lower endpoint.
     Compared on exact Fractions; the comparison reduces to sign(p_u * inc_u - p_d * inc_d) since C > 0.
     (Instance 2 is an exact tie -> lower endpoint.)
 A8. Checkpoint 1 "Strategy A's probability-weighted upside ending value" = p_u * C * (1 + r_Bu + inc_u), i.e. the
     upside TERM of E_A (all capital in A, as in the selection rule), in USD -- not the full expectation E_A (that
     would be called the probability-weighted ending value without "upside") and not weighted by w (w is not yet
     chosen at position 1).
 A9. Checkpoint 2 "Strategy B's ending value in the downturn" = C * (1 - l_Bd): all capital in B, downturn scenario,
     NOT probability-weighted, in USD.
 A10. Final answer is the selected EXACT weight expressed in percent (w * 100); rounding is left to the framework
     ("the displayed percentage is a reporting approximation, not the operative exact endpoint").
 A11. Feasibility: the text asserts 0 < w_lo <= w_hi < 1. The solver checks it, but since the answer spec is a plain
     decimal percent there is no alternative outcome; the selected endpoint is returned regardless (no clamping,
     because the operative endpoints are the ones "supplied" by the two requirements).
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, after, before, grab, grab_all, numbers  # noqa: F401

TEMPLATE_ID = "h081"

_PCT_TAIL = re.compile(r"^\s*(?:%|(?:percent|per cent|pct)\b)", re.I)


def _num(patterns: list[str], text: str, pct_aware: bool = True) -> Fraction:
    """First pattern (with {N} = number capture) that matches; '%'/'percent' right after the number -> /100."""
    for pat in patterns:
        rx = pat.replace("{N}", f"({NUMBER})")
        m = re.search(rx, text, flags=re.S | re.I)
        if m is not None:
            v = F(m.group(1))
            if pct_aware and _PCT_TAIL.match(text[m.end(1):]):
                v = v / 100
            return v
    raise ValueError(f"no pattern matched: {patterns!r}")


def _opt_num(patterns: list[str], text: str, pct_aware: bool = True) -> Fraction | None:
    try:
        return _num(patterns, text, pct_aware)
    except ValueError:
        return None


_MONEY = r"(?:USD\s*|US\$\s*|\$\s*)?"


def solve(text: str, q: dict) -> dict:
    # ---- parse -------------------------------------------------------------------------------------------------
    C = _num([rf"capital(?:\s+of)?\s+{_MONEY}{{N}}", rf"capital\D{{0,12}}{{N}}"], text, pct_aware=False)

    p_d = _opt_num([r"downturn probability(?:\s+(?:is|of|equals|=))?\s*{N}", r"probability of (?:a |the )?downturn\D{0,12}{N}"], text)
    if p_d is None:
        p_u_direct = _num([r"upside probability(?:\s+(?:is|of|equals|=))?\s*{N}", r"probability of (?:an? |the )?upside\D{0,12}{N}"], text)
        p_d = 1 - p_u_direct
    p_u = 1 - p_d

    r_Bu = _num([r"Strategy B earns(?: an?)? upside return(?: of)?\s*{N}", r"upside return(?: of)?\s*{N}"], text)
    _P = r"(?:\s*(?:%|percent|per cent|pct))?"  # optional percent token between the number and the anchor
    l_Bd = _num([rf"Strategy B earns.*?loses\s*{{N}}{_P}\s*in the downturn", rf"loses\s*{{N}}{_P}\s*in the downturn"], text)
    inc_u = _num([r"incremental (?:upside )?return(?: of)?\s*{N}"], text)
    inc_d = _num([r"incremental (?:downturn )?loss(?: of)?\s*{N}"], text)

    U = _num([rf"at least\s+{_MONEY}{{N}}\s+in the upside", rf"at least\s+{_MONEY}{{N}}\s+(?:in|under|during) (?:the )?upside"], text, pct_aware=False)
    D = _num([rf"at least\s+{_MONEY}{{N}}\s+in the downturn", rf"at least\s+{_MONEY}{{N}}\s+(?:in|under|during) (?:the )?downturn"], text, pct_aware=False)

    # ---- strategy factors (A3) ---------------------------------------------------------------------------------
    fB_up = 1 + r_Bu
    fB_dn = 1 - l_Bd
    fA_up = 1 + (r_Bu + inc_u)
    fA_dn = 1 - (l_Bd + inc_d)
    # text asserts both A rates (as magnitudes) are below one; it is a consistency statement, not an input.

    # ---- all-capital ending values and expectations (A7, A8, A9) ---------------------------------------------
    A_up, A_dn = C * fA_up, C * fA_dn
    B_up, B_dn = C * fB_up, C * fB_dn
    a_weighted_upside = p_u * A_up          # checkpoint 1
    E_A = p_u * A_up + p_d * A_dn
    E_B = p_u * B_up + p_d * B_dn

    # ---- feasibility interval (A4, A5, A6) --------------------------------------------------------------------
    # V_up(w) = C*(fB_up + w*(fA_up - fB_up)) >= U ; V_dn(w) = C*(fB_dn + w*(fA_dn - fB_dn)) >= D
    lowers: list[Fraction] = []
    uppers: list[Fraction] = []
    for req, f_a, f_b in ((U, fA_up, fB_up), (D, fA_dn, fB_dn)):
        coef = C * (f_a - f_b)
        if coef == 0:
            continue  # constraint independent of w (never the case here: incrementals are positive)
        w_star = (req - C * f_b) / coef
        (lowers if coef > 0 else uppers).append(w_star)
    # Text: the upside requirement supplies the lower endpoint, the downturn requirement the upper endpoint.
    w_lo = max(lowers) if lowers else Fraction(0)
    w_hi = min(uppers) if uppers else Fraction(1)
    feasible = (0 < w_lo) and (w_lo <= w_hi) and (w_hi < 1)  # asserted by the text; informational only (A11)
    _ = feasible

    # ---- endpoint selection (A7) ------------------------------------------------------------------------------
    w = w_hi if E_A > E_B else w_lo

    return {
        "final": w * 100,  # percent (A10)
        "slots": {
            "strategy_a_weighted_upside_checkpoint": a_weighted_upside,
            "strategy_b_downturn_checkpoint": B_dn,
        },
    }
