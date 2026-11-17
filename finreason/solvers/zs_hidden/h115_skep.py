"""h115 -- one cap-limited Newton-Raphson step toward the after-tax IRR of a two-year investment.

Structure of the question
    t=0 : pay I0 (the "investment requires I0 at time 0")
    t=1 : receive the after-tax distribution D (does not change the tax basis)
    t=2 : sell for gross price P; selling costs s*P; gain tax t*max(0, P(1-s) - B); keep the rest
    NPV(r) = -I0 + D/(1+r) + CF2/(1+r)^2 evaluated at the trial rate r0, then ONE Newton step
    delta = NPV(r0)/|NPV'(r0)|, limited by an absolute cap c, reported as (r0 + step)*100 percent.

AMBIGUITY RESOLUTIONS (listed before coding, each tied to the wording)
 A1  Basis vs cost. The gain is "net sale proceeds after selling costs minus tax basis" and the basis
     is stated separately ("unchanged tax basis B"), so the gain uses B, NOT the time-0 cost I0.
     The year-1 distribution is "after-tax" and paid "without changing that basis" -> it carries no
     tax of its own and leaves B untouched.
 A2  Selling costs are "the fraction s of gross price": s is a plain ratio (0.1 = 10 %) applied to the
     gross price P, so net proceeds N = P*(1-s). The checkpoint asks for exactly this quantity
     ("net sale proceeds after proportional selling costs and before gain tax"), in USD, unrounded.
 A3  Gain tax: t is a ratio ("0.2 of the positive gain"); "positive gain" is a floor at zero, so
     tax = t*max(0, N-B). (All three instances have N > B; the floor is implemented regardless.)
 A4  Year-2 cash flow used in the NPV is what the investor keeps: CF2 = N - tax. CF1 = D, CF0 = -I0.
 A5  "Annual effective trial rate" r0 with cash flows at the ends of years 1 and 2 -> whole-year
     discounting, NPV(r) = -I0 + D/(1+r) + CF2/(1+r)^2, computed exactly with Fractions.
 A6  "Newton-Raphson correction using the negative-derivative magnitude": NPV'(r) =
     -D/(1+r)^2 - 2*CF2/(1+r)^3 is negative; the raw correction is delta = NPV(r0)/|NPV'(r0)|
     = -NPV/NPV', i.e. the ordinary Newton step in the rate. It is "positive" because NPV(r0) > 0
     in every instance (checked), so the step moves the rate upward toward the IRR.
 A7  "Fixed absolute rate-step cap c ... add the smaller of the raw correction and cap": the cap is
     an absolute step in rate units (0.04 = four percentage points), not a relative one; step =
     min(delta, c). For robustness a (never-occurring) negative delta is clipped by magnitude,
     step = max(delta, -c), which is the natural reading of an *absolute* step cap.
 A8  Exactly one step ("Do not iterate again"); the result is (r0 + step)*100 in percent, returned
     unrounded -- the framework applies half-up rounding to 2 dp. The derivative is evaluated at r0
     (not at the updated rate) because it belongs to the single correction being formed.
 A9  Branch outcomes differ across the cluster: instances 1 and 2 take the raw Newton step, while
     instance 3's raw step (~0.0652) exceeds its cap 0.05005, giving exactly 0.15005 -> 15.005 % ->
     15.01 after half-up rounding; exact arithmetic makes that tie certain.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h115"


def solve(text: str, q: dict) -> dict:
    # --- inputs (all anchored on surrounding words) ---------------------------------------------
    i0 = grab(r"requires {N} at time 0", text)                                  # time-0 outlay
    basis = grab(r"unchanged tax basis {N}", text)                              # tax basis B
    dist = grab(r"after-tax distribution {N} at the end of year 1", text)      # year-1 cash flow
    price = grab(r"sold for {N}", text)                                         # gross sale price P
    s = grab(r"selling costs equal the fraction {N} of gross price", text)     # selling-cost ratio
    t = grab(r"capital-gains tax equals {N} of the positive gain", text)       # gain-tax ratio
    r0 = grab(r"annual effective trial rate {N}", text)                         # trial rate (ratio)
    cap = grab(r"rate-step cap {N}", text)                                      # absolute step cap

    # --- year-2 sale: proportional selling costs, then tax on the positive gain (A1-A4) ----------
    net_proceeds = price * (1 - s)                     # checkpoint: after costs, before gain tax
    gain = net_proceeds - basis
    tax = t * gain if gain > 0 else Fraction(0)        # "positive gain" -> floor at zero
    cf2 = net_proceeds - tax                           # cash actually received at end of year 2

    # --- exact NPV and its derivative at the trial rate (A5, A6) --------------------------------
    v = 1 + r0
    npv = -i0 + dist / v + cf2 / v**2
    neg_deriv_mag = dist / v**2 + 2 * cf2 / v**3      # |NPV'(r0)|, NPV'(r0) itself is negative
    delta = npv / neg_deriv_mag                        # raw Newton-Raphson correction (positive)

    # --- one cap-limited step (A7, A8) ----------------------------------------------------------
    if delta >= 0:
        step = min(delta, cap)                         # "the smaller of the raw correction and cap"
    else:                                              # not exercised: absolute cap on the magnitude
        step = max(delta, -cap)
    new_rate = r0 + step

    return {
        "final": new_rate * 100,                       # annual percentage, unrounded
        "slots": {"net_sale_proceeds_after_cost_checkpoint": net_proceeds},
    }
