"""h106 -- order of two actions (capex-first vs reduction-first) over two equal operating periods.

FINANCE MODEL (written before the code)
=======================================
Quantity: the asset-turnover effect of the ORDER in which two balance-sheet actions are taken.
  turnover = net sales / total assets, measured over two equal-length operating periods, then
  normalised by the common pre-action turnover T0 = S0 / A0.  The answer is
      100 * (N_reduction_first - N_capex_first)         [percent of baseline turnover]
  i.e. the difference of the two normalised factors (each a multiple of baseline turnover)
  expressed as a percentage of baseline turnover.

Givens and how each enters
  R  = "net total-asset base that remains after a true reduction of D"   -> retained base.
  D  = the true reduction (a real decline of the asset base) -> pre-action base A0 = R + D
       (the base BEFORE either action; it is the only place D is used: it fixes T0 = S0/A0
       and the capex-first period-one assets).
  C  = modernization's net capitalized addition to total assets (already net, so it adds to
       the asset base one-for-one).
  u  = 0.5 = modernization raises run-rate net sales by 0.5.  A plain decimal is a fraction
       (50 %), NOT 0.5 percent: sales multiplier m = 1 + u = 1.5.
  d  = 0.2 = the reduction lowers run-rate net sales by 0.2: sales multiplier r = 1 - d = 0.8.
  "the two sales effects compound" -> multiplicative, not additive: both-actions factor
       m * r (= 1.2 here), never 1 + u - d.
  S0 = baseline run-rate net sales per period (not given; cancels in every normalised factor).

Timeline (each effect starts at its action date and persists; the first action takes place at
the start of period one, the second at the start of period two):
  capex-first      : P1 sales = S0*m        , P1 assets = A0 + C      (capex done, reduction not yet)
                     P2 sales = S0*m*r      , P2 assets = R + C       (both done)
  reduction-first  : P1 sales = S0*r        , P1 assets = R           (reduction done, capex not yet)
                     P2 sales = S0*m*r      , P2 assets = R + C       (both done)
  -> period two is IDENTICAL across orders: sales factor m*r (checkpoint 1) and total-asset base
     R + C (checkpoint 2); only period one differs.

Turnover per order = (mean of the two period sales) / (mean of the two period asset bases)
                   = (sum of sales) / (sum of assets)            [equal-length periods]
  T_cap = S0*(m + m*r)  / ((A0 + C) + (R + C))
  T_red = S0*(r + m*r)  / (R + (R + C))
Normalised factor N = T / T0 = T * A0 / S0   (S0 cancels):
  N_cap = (m + m*r) * A0 / (A0 + R + 2C)
  N_red = (r + m*r) * A0 / (2R + C)
Final = 100 * (N_red - N_cap), exact Fraction, unrounded (framework rounds half-up to 2 dp).

Overrides of standard conventions: none beyond the explicit ones above (compounding of the two
sales effects, sums-over-sums turnover, normalisation by the common pre-action turnover).
No intermediate rounding anywhere: every quantity is an exact rational.
"""
from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F  # noqa: F401

TEMPLATE_ID = "h106"


def _rate(pattern: str, text: str) -> Fraction:
    """Rate expressed as a plain decimal fraction (0.5 -> 1/2); honours an explicit 'percent'."""
    rx = pattern.replace("{N}", r"(-?\d+(?:\.\d+)?(?:/\d+)?)") + r"(\s*(?:percent|%))?"
    m = re.search(rx, text, flags=re.S)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    value = F(m.group(1))
    return value / 100 if m.group(2) else value


def solve(text: str, q: dict) -> dict:
    # --- parse (anchored on the surrounding words) ---------------------------------------
    retained = grab(r"{N} is the net total-asset base that remains", text)       # R
    reduction = grab(r"after a true reduction of {N}", text)                       # D
    addition = grab(r"{N} is the modernization program's net capitalized addition", text)  # C
    uplift = _rate(r"[Mm]odernization raises run-rate net sales by {N}", text)     # u
    drag = _rate(r"reduction lowers run-rate net sales by {N}", text)              # d

    # --- model ---------------------------------------------------------------------------
    pre_action = retained + reduction                 # A0: base before either action
    m = 1 + uplift                                    # modernization sales multiplier
    r = 1 - drag                                      # reduction sales multiplier
    both = m * r                                      # compounded; common period-two factor

    final_assets = retained + addition                # common period-two asset base

    # capex-first: modernization (sales x m, assets A0 + C) then reduction (sales x m r, assets R + C)
    sales_cap = m + both
    assets_cap = (pre_action + addition) + final_assets
    # reduction-first: reduction (sales x r, assets R) then modernization (sales x m r, assets R + C)
    sales_red = r + both
    assets_red = retained + final_assets

    # normalise by baseline turnover S0 / A0  ->  multiply sums-ratio by A0 / S0 (S0 cancels)
    norm_cap = (sales_cap / assets_cap) * pre_action
    norm_red = (sales_red / assets_red) * pre_action

    final = (norm_red - norm_cap) * 100               # percent of baseline turnover

    return {
        "final": final,
        "slots": {
            "combined_sales_effect_checkpoint": both,
            "shared_second_period_asset_base_checkpoint": final_assets,
        },
    }
