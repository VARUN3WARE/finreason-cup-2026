"""h028 -- stylized acquisition: full-year run-rate EPS accretion / dilution (percent).

Structure (all three instances share it):
  * Acquirer predeal common shares have aggregate reference equity value E at one fixed
    contractual share price P  ->  predeal share count N0 = E / P.
  * Upfront base consideration B (excluding earnout); cash fraction c of B is paid in cash,
    the remainder (1 - c) * B in common shares at price P.
  * Fully realized earnout X, incremental to B, settled entirely in shares at the same P.
  * Every deal share is outstanding for the full year (no weighting).
  * Entire upfront cash leg c * B is debt-funded at annual pre-tax rate r.
  * Standalone after-tax net income: acquirer A, target T.  Target NI excludes the recurring
    annual pre-tax synergies S.  Tax rate t: after-tax synergies = S(1-t), after-tax interest
    = c*B*r*(1-t) (full tax shield usable).
  * Ignore amortization, deal costs, share weighting, price reaction, anything else.

Since every share is priced at the same P, P cancels everywhere:
  deal shares / predeal shares = ((1-c)*B + X) / P  /  (E / P) = ((1-c)*B + X) / E
  pro forma NI      = A + T + S(1-t) - c*B*r*(1-t)
  pro forma EPS / standalone EPS = (NI_pf / (N0 * (1 + k))) / (A / N0) = NI_pf / (A * (1 + k))
  accretion % = (NI_pf / (A * (1 + k)) - 1) * 100

AMBIGUITIES CONSIDERED AND HOW THEY WERE RESOLVED
-------------------------------------------------
1. "0.5 is paid in cash": absolute amount or fraction of the base consideration?
   -> Fraction. The template writes every rate as a plain decimal ("interest rate 0.1",
      "tax rate 0.2"), the sentence is about *how* the consideration is split ("0.5 is paid in
      cash and the remainder in common shares"), and 0.5 is constant across all three instances
      exactly like the other structural rates while the money amounts vary. An absolute cash leg
      of 0.5 against a 99 consideration would be nonsensical. A trailing "percent"/"%" is
      honoured (divided by 100) for robustness.
2. Which shares count as "new deal shares" for the checkpoint ratio?
   -> Base-consideration share leg PLUS earnout shares. The text says the earnout is "settled
      entirely in common shares at the same unchanged price, and every deal share is outstanding
      for the full year" -- earnout shares are deal shares. The checkpoint denominator is the
      predeal common-share base, i.e. N0 = E/P, so the ratio is ((1-c)B + X)/E (P cancels).
      Unit "ratio": plain ratio, not percent.
3. Does the earnout affect earnings?  -> No. Only the share count; "ignore ... all other share or
   earnings changes". It is incremental to B, so it does not reduce the base share leg either.
4. Checkpoint 2 "annual pre-tax interest on the debt-funded upfront cash leg": pre-tax, not
   after-tax; on the cash leg c*B only (earnout and share leg are not debt-funded)  -> c*B*r.
   Unit usd_million: the question's money figures are unit-less and the spec interprets them in
   USD millions, so the value is returned in the same units as the text (no scaling).
5. Target net income T is already after-tax and excludes synergies -> added in full; synergies
   added after tax S(1-t); interest subtracted after tax c*B*r*(1-t) (full shield usable).
6. Base of the comparison: the acquirer's *standalone* EPS = A / N0 (not combined NI / N0).
7. Sign convention: positive = accretion; result = (EPS_pf / EPS_standalone - 1) * 100 in percent.
8. No rounding anywhere inside the computation (nothing is said to be rounded to whole shares
   or cents); exact Fractions throughout, the framework rounds each result independently.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h028"


def _rate(pattern: str, text: str) -> Fraction:
    """Grab a rate written either as a decimal (0.1) or as 'N percent' / 'N%'.

    ``{N}`` marks the number; ``{P}`` marks where an optional 'percent'/'%' may follow it.
    If the pattern has no ``{P}``, the optional percent marker is appended at the end.
    """
    if "{P}" not in pattern:
        pattern = pattern + "{P}"
    rx = pattern.replace("{N}", f"({NUMBER})").replace("{P}", r"(\s*(?:percent|%))?")
    m = re.search(rx, text, flags=re.S)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    v = F(m.group(1))
    if m.group(2):
        v = v / 100
    return v


def solve(text: str, q: dict) -> dict:
    # --- inputs -----------------------------------------------------------------------------
    E = grab(r"aggregate reference equity value {N}", text)            # predeal equity value
    B = grab(r"[Uu]pfront base consideration is {N}", text)             # base consideration
    c = _rate(r"{N}{P} (?:is|was) paid in cash", text)                 # cash fraction of B
    X = grab(r"earnout with settlement value {N}", text)                # earnout, all in shares
    r = _rate(r"annual pre-tax interest rate (?:of )?{N}", text)        # debt rate
    A = grab(r"net income is {N} for the acquirer", text)               # acquirer after-tax NI
    T = grab(r"and {N} for the target", text)                           # target after-tax NI
    S = grab(r"pre-tax synergies of {N}", text)                         # pre-tax synergies
    t = _rate(r"[Tt]ax rate (?:of |is )?{N}", text)                     # tax rate

    if not (0 <= c <= 1):
        raise ValueError(f"cash fraction {c} outside [0, 1]; text may state an absolute amount")

    # --- shares (price P cancels) ------------------------------------------------------------
    cash_leg = c * B
    share_consideration = (1 - c) * B + X
    deal_share_ratio = share_consideration / E          # new deal shares / predeal shares

    # --- earnings ----------------------------------------------------------------------------
    pretax_interest = cash_leg * r
    ni_pro_forma = A + T + S * (1 - t) - pretax_interest * (1 - t)

    # --- EPS accretion / dilution ------------------------------------------------------------
    # EPS_pf / EPS_standalone = (NI_pf / (N0 (1+k))) / (A / N0) = NI_pf / (A (1+k))
    accretion_pct = (ni_pro_forma / (A * (1 + deal_share_ratio)) - 1) * 100

    return {
        "final": accretion_pct,
        "slots": {
            "deal_share_issuance_checkpoint": deal_share_ratio,
            "pretax_interest_checkpoint": pretax_interest,
        },
    }
