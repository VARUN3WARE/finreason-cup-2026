"""h011 -- net economic exposure (percent of shares outstanding) with a
delta-adjusted derivative-equivalent checkpoint.

Structure (identical wording across the 3 instances):
  "an investor has A direct long shares, B shares attributed through related
   holdings, and derivative notional equivalent to N shares with exposure delta d.
   The investor also has S shares of offsetting short exposure. The issuer has O
   shares outstanding. Multiply derivative reference shares by delta, add all long
   exposure, subtract the short hedge, divide the signed result by shares
   outstanding, and convert the ratio to a percentage."

AMBIGUITY HUNT -- points where analysts could disagree, and the resolution:

 1. What is the checkpoint "delta-adjusted derivative-equivalent shares"?
    -> N * d exactly ("Multiply derivative reference shares by delta"). Unit is
       a share count. Returned UNROUNDED; framework rounds half-up to 2 dp.
       Delta is given as a plain ratio ("exposure delta 0.4"), NOT a percent,
       so no /100 is applied to it.

 2. Does "add all long exposure" include the derivative equivalent?
    -> Yes: the instruction sequence is multiply (derivative) -> add ALL long
       exposure -> subtract short. Long exposure = direct A + related B +
       derivative-equivalent N*d. Whether one reads the derivative as "part of"
       the long exposure or as a separately added term, the sum is identical:
       A + B + N*d.

 3. Is delta applied to the short hedge?
    -> No. Delta is attached only to the derivative notional. The short exposure
       is already stated in shares ("S shares of offsetting short exposure") and is
       subtracted at face value.

 4. Sign handling / floor at zero?
    -> "divide the SIGNED result by shares outstanding": the sign is preserved;
       a net short position yields a negative percentage (this actually happens
       in instance t1_dtcq3nmm6o7sz5p3fnoa2). No floor at zero, no absolute value.

 5. Denominator.
    -> Exactly the issuer's shares outstanding O as stated. No dilution
       adjustment (derivative shares are NOT added to the denominator); the text
       says simply "divide ... by shares outstanding".

 6. Percent vs ratio.
    -> "convert the ratio to a percentage" and answer unit "percent": final =
       ratio * 100 (e.g. 2.19 means 2.19%). Returned unrounded.

 7. Independent rounding.
    -> "Report the derivative-equivalent shares independently using half-up
       rounding ... and report the net economic exposure percentage using
       independent half-up rounding": the ROUNDED checkpoint is never fed into
       the final computation; the exact N*d is used downstream. Both values are
       returned exact and the framework rounds each one.

 8. Number formats: notional shares and short shares may be non-integers
    (63.7575, 144.8); all values are parsed as exact Fractions.
"""

from __future__ import annotations

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h011"


def solve(text: str, q: dict) -> dict:
    direct_long = grab(r"has\s+{N}\s+direct long shares", text)
    related_long = grab(r"{N}\s+shares attributed through related holdings", text)
    deriv_notional = grab(r"derivative notional equivalent to\s+{N}\s+shares", text)
    delta = grab(r"exposure delta\s+{N}", text)
    short_shares = grab(r"has\s+{N}\s+shares of offsetting short exposure", text)
    shares_out = grab(r"issuer has\s+{N}\s+shares outstanding", text)

    # Step 1: delta-adjusted derivative-equivalent shares (checkpoint, exact).
    deriv_equiv = deriv_notional * delta

    # Step 2: add all long exposure (direct + related + derivative-equivalent).
    long_exposure = direct_long + related_long + deriv_equiv

    # Step 3: subtract the short hedge (face value, no delta) -- keep the sign.
    net_signed = long_exposure - short_shares

    # Step 4: divide by shares outstanding, convert ratio to percent.
    net_pct = net_signed / shares_out * Fraction(100)

    return {
        "final": net_pct,
        "slots": {"derivative_equivalent_checkpoint": deriv_equiv},
    }
