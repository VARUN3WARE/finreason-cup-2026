"""Hidden cluster h040 -- token burn, market-cap ceiling, maximum additional emission.

Structure (all three instances share it):
    "A token has S0 units outstanding and will burn B units. After the burn, the token is
    expected to trade at P USD per unit, and this price is assumed to remain unchanged when
    additional units are emitted. If total market capitalization must not exceed C USD, first
    compute the market cap of the current supply at that expected price, express it as a
    multiple of the ceiling, and use that multiple to recover the ceiling-compatible total
    supply. What is the maximum number of additional token units that may be emitted after
    the burn? Carry all arithmetic exactly, then report ... half-up ... nearest whole token."

Chain implemented (exact Fractions throughout, nothing rounded inside):
    S1   = S0 - B                       post-burn supply (the supply that exists when emission happens)
    cap  = S1 * P                       "market cap of the current supply at that expected price"
    m    = cap / C                      "express it as a multiple of the ceiling"  -> checkpoint
    T    = S1 / m  ( == C / P )         "use that multiple to recover the ceiling-compatible total supply"
    ans  = T - S1                       "maximum number of additional units that may be emitted after the burn"

AMBIGUITIES CONSIDERED AND RESOLUTIONS
1. Which supply is "the current supply"? (pre-burn S0 vs post-burn S1)
   -> S1 (post-burn). Evidence: the price used is explicitly the post-burn "expected price"
      ("at that expected price"), the emission happens "after the burn", and the chain
      "recover the ceiling-compatible total supply" / "additional units" only closes cleanly
      when total - current = additional, i.e. current = post-burn supply. Mixing a pre-burn
      supply with a post-burn price would be an incoherent benchmark. NOTE: the FINAL answer is
      independent of this choice (S/m == C/P for either S); only the checkpoint depends on it.
2. "Multiple of the ceiling": cap / C as a plain ratio (unit "multiple"), not a percent, not C/cap.
   -> m = cap / C. "express it [the market cap] as a multiple of the ceiling" = cap is m times C.
3. Recovering the total supply from the multiple: T = S1 / m (equivalently C / P). Computed
   literally as S1 / m to honour the stated chain; it is exactly C / P so no precision issue.
4. Floor at zero / sign: the text states no floor ("larger of ... and zero" is absent, whereas
   every seen template that floors says so explicitly). Instance 3 has cap > C (m > 1), so the
   formula gives a NEGATIVE emission allowance; we return it unfloored (-411.237 -> -411), exactly
   as the stated formula produces it. (This is the main residual risk: an answer key that clamps
   to 0 would differ on that one instance.)
5. Rounding: "Carry all arithmetic exactly, then report ... half-up to the nearest whole token" ->
   nothing is rounded inside; the unrounded Fraction is returned for the final and the checkpoint
   (framework applies 0 dp / 6 dp half-up). No whole-token flooring of the emission count: the
   text asks for half-up rounding of the exact value, not a floor.
6. Units: final is a token count ("dimensionless"); checkpoint is a plain multiple (6 dp).
7. Price / ceiling / counts may be rationals (e.g. 25761/13312) or decimals -- parsed exactly by
   finreason.nums.  Burn given as a percent of supply is supported defensively (not used here).
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import F, grab

TEMPLATE_ID = "h040"


def _parse(text: str) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    # S0: units outstanding before the burn.
    s0 = grab(r"has\s+{N}\s+(?:token\s+)?units\s+outstanding", text)
    # B: units burned (absolute count; defensive percent-of-supply form as a fallback).
    m_pct = re.search(r"burn(?:s|ed)?\s+(-?[\d,]+(?:\.\d+)?(?:/\d+)?)\s+percent", text, flags=re.S)
    if m_pct:
        burn = s0 * F(m_pct.group(1)) / 100
    else:
        burn = grab(r"burn(?:s|ed)?\s+{N}\s+(?:token\s+)?units", text)
    # P: expected post-burn price per unit, unchanged by emission.
    price = grab(r"trade\s+at\s+{N}\s+USD\s+per\s+(?:unit|token)", text)
    # C: market-cap ceiling.
    ceiling = grab(r"must\s+not\s+exceed\s+{N}\s+USD", text)
    return s0, burn, price, ceiling


def solve(text: str, q: dict) -> dict:
    s0, burn, price, ceiling = _parse(text)

    s1 = s0 - burn                     # post-burn supply ("current supply" at the emission decision)
    cap = s1 * price                   # market cap of the current supply at the expected price
    multiple = cap / ceiling           # that cap expressed as a multiple of the ceiling
    total = s1 / multiple              # ceiling-compatible total supply (== ceiling / price)
    additional = total - s1            # maximum additional units emitted after the burn (unfloored)

    return {
        "final": additional,
        "slots": {"ceiling_utilization_checkpoint": multiple},
    }
