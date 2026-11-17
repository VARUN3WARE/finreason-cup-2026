"""Cluster h061 -- revenue required to achieve a target after-tax income.

Question shape (all 3 instances):
    "A company has a variable COGS rate ratio of v, fixed operating costs of FC,
     interest expense of I, and an income tax rate ratio of t. Determine the
     revenue required to achieve after-tax income of NI. Report the result in
     USD millions."
    Checkpoint (position 1): "Determine the after-tax retention ratio"  -> ratio, 6 dp half-up.
    Final: revenue, usd_million, 2 dp half-up.

AMBIGUITY HUNT -- points where analysts could disagree, and how each is resolved:

 A1. Units of the money inputs (fixed costs, interest, target income). No unit is attached to
     them; the only unit mentioned is "Report the result in USD millions". Resolution: every
     money input is already in USD millions (the same unit as the answer), so no scaling is
     applied. Reading them as plain USD would give a revenue of ~0.0001 million -> "0.00",
     which is clearly not the intended problem.

 A2. "variable COGS rate ratio" -- percent or ratio? The word "ratio" and the values (0.2, 0.45)
     make it a plain fraction of revenue: COGS = v * Revenue. Contribution ratio = 1 - v.
     (Defensive fallback: a value > 1, or one followed by "percent"/"%", is divided by 100.)

 A3. "income tax rate ratio" -- same reasoning: plain fraction (0.3999995, 0.4, 0.2499997).

 A4. "after-tax retention ratio" (the checkpoint). Could be confused with the dividend
     retention ratio (1 - payout), but no payout/dividend data exists, and the wording
     "after-tax retention" names the share of pre-tax income kept after tax: 1 - t.
     Unit "ratio" -> plain fraction, NOT percent. It is returned UNROUNDED (e.g. 0.6000005);
     the framework rounds it half-up to 6 dp (0.6000005 -> 0.600001; a banker's-rounding
     implementation would wrongly give 0.600000). The rounded checkpoint is NEVER fed
     downstream; the exact (unrounded) retention is used for the revenue computation.

 A5. Is interest tax-deductible, i.e. is tax applied to EBT (after interest) or to EBIT?
     Standard financial-accounting treatment and the textbook "revenue for target net income"
     formula: tax is levied on pre-tax income = EBIT - interest. So
         NI = (Revenue*(1 - v) - FC - I) * (1 - t)
         Revenue = (NI / (1 - t) + FC + I) / (1 - v).
     (Taxing EBIT and subtracting interest afterwards is non-standard and is not used.)

 A6. Are "fixed operating costs" separate from interest? Yes -- interest is a non-operating
     (financing) expense and is listed separately, so it is NOT inside fixed operating costs.
     Both are added back on the way from net income to revenue.

 A7. Is there any intermediate rounding (whole units, cents)? No sentence asks for it, and the
     answer format says "use exact arithmetic through all intermediate steps". Everything stays
     an exact Fraction; only the framework rounds the displayed values.

 A8. Sign / floor conventions: none stated. The revenue is reported as computed (it is positive
     in all instances since NI, FC, I > 0 and 0 < v, t < 1).

 A9. Order of operations: gross-up NI by (1 - t) FIRST, then add fixed costs and interest, then
     divide by the contribution ratio (1 - v). Adding costs before the gross-up would wrongly
     tax-shield the costs twice.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import F, grab, NUMBER

TEMPLATE_ID = "h061"

# Optional currency decoration between "of" and the number (robustness only; the three
# instances contain none of it).
_CUR = r"(?:USD\s*|\$\s*)?"


def _rate(label_patterns: list[str], text: str) -> Fraction:
    """Grab a rate that is normally a plain ratio; convert if it is clearly a percent."""
    for pat in label_patterns:
        rx = pat.replace("{N}", f"({NUMBER})")
        m = re.search(rx, text, flags=re.S | re.I)
        if m is None:
            continue
        val = F(m.group(1))
        tail = text[m.end(): m.end() + 12]
        if re.match(r"\s*(?:percent|%)", tail, flags=re.I) or val > 1:
            val = val / 100
        return val
    raise ValueError(f"rate not found for {label_patterns!r}")


def _amount(label_patterns: list[str], text: str) -> Fraction:
    for pat in label_patterns:
        try:
            return grab(pat, text)
        except ValueError:
            continue
    raise ValueError(f"amount not found for {label_patterns!r}")


def solve(text: str, q: dict) -> dict:
    # --- parse (all anchored on the surrounding words; no instance values hard-coded) ---
    v = _rate(
        [
            rf"variable\s+COGS\s+rate\s+ratio\s+of\s+{_CUR}{{N}}",
            rf"variable\s+(?:COGS|cost)[^.,;]*?\s+of\s+{_CUR}{{N}}",
        ],
        text,
    )
    fixed = _amount(
        [
            rf"fixed\s+operating\s+costs?\s+of\s+{_CUR}{{N}}",
            rf"fixed\s+costs?\s+of\s+{_CUR}{{N}}",
        ],
        text,
    )
    interest = _amount(
        [
            rf"interest\s+expenses?\s+of\s+{_CUR}{{N}}",
            rf"interest\s+of\s+{_CUR}{{N}}",
        ],
        text,
    )
    t = _rate(
        [
            rf"income\s+tax\s+rate\s+ratio\s+of\s+{_CUR}{{N}}",
            rf"tax\s+rate[^.,;]*?\s+of\s+{_CUR}{{N}}",
        ],
        text,
    )
    target_ni = _amount(
        [
            rf"after-tax\s+income\s+of\s+{_CUR}{{N}}",
            rf"net\s+income\s+of\s+{_CUR}{{N}}",
            rf"after-tax\s+(?:profit|earnings)\s+of\s+{_CUR}{{N}}",
        ],
        text,
    )

    # --- compute (exact Fractions throughout; see A4/A5/A9) ---
    retention = 1 - t                       # after-tax retention ratio (checkpoint, unrounded)
    contribution = 1 - v                    # share of revenue left after variable COGS
    pre_tax_income = target_ni / retention  # EBT needed
    ebit = pre_tax_income + interest        # add back interest (A5/A6)
    revenue = (ebit + fixed) / contribution # cover fixed operating costs, then gross up for COGS

    return {
        "final": revenue,                   # USD millions (A1)
        "slots": {"retention_ratio_checkpoint": retention},
    }
