"""h115 -- one capped Newton-Raphson rate update on the NPV of a two-year taxed investment.

FINANCE MODEL (written before the code; every override of convention is flagged)
--------------------------------------------------------------------------------
Quantity computed: the trial rate after ONE safeguarded Newton-Raphson step on f(r) = NPV(r), reported
as an annual percentage.  It is explicitly NOT an exact IRR and NOT an iterated / adaptive solution.

Inputs (investor's point of view):
  I0   cash required at time 0                       ("requires X at time 0")
  B    tax basis, unchanged all the way to the sale   ("unchanged tax basis X"; the year-1
       distribution does NOT reduce it -> B enters the year-2 gain exactly as given)
  D    AFTER-TAX distribution at end of year 1        (already net of tax -> taken as-is, no
       further tax, no basis effect)
  P    gross sale price at end of year 2
  c    selling costs, PROPORTIONAL to gross price     ("fraction c of gross price")
  tau  capital-gains tax rate
  r0   annual effective trial rate (decimal, 0.12 = 12 %)
  cap  fixed ABSOLUTE rate-step cap in rate units (0.04 = 4 percentage points, not relative)

Year-2 sale waterfall:
  net sale proceeds   N     = P * (1 - c)                 <- checkpoint 1 ("after selling costs,
                                                              before gain tax")
  gain                G     = N - B                        (measured AFTER selling costs, as the
                                                              text defines it)
  capital-gains tax   T     = tau * max(G, 0)              ("positive gain": no tax / no refund
                                                              when G <= 0)
  after-tax proceeds  S     = N - T                        (cash actually received at t = 2)

Cash flows:  t=0: -I0      t=1: +D      t=2: +S
NPV with annual effective compounding (standard convention, no override):
  f(r)  = -I0 + D/(1+r) + S/(1+r)^2
  f'(r) = -D/(1+r)^2 - 2*S/(1+r)^3          (negative for D,S > 0 -> "negative derivative";
                                                |f'| is its magnitude)
Newton step (text: "positive correction using the negative-derivative magnitude"):
  raw = f(r0) / |f'(r0)|        (= -f/f' because f' < 0, so it is ADDED to the rate; it is
                                  positive whenever NPV(r0) > 0, i.e. true IRR > r0)
Cap ("add the smaller of the raw correction and cap to the trial rate"):
  step = min(raw, cap)
  r1   = r0 + step
Answer = 100 * r1 percent (unrounded exact Fraction; the framework rounds half-up to 2 dp).
  The result is reported once -- no second iteration, no IRR claim.

Notes on resolved ambiguities:
  * "capital-gains tax equals tau of the positive gain measured as net sale proceeds after
    selling costs minus tax basis" -> gain uses N (after selling costs), not gross price.
  * The cap is absolute (rate units), compared directly with raw (also in rate units).
  * Everything is rational, so all arithmetic is exact Fraction arithmetic (no floats, no
    irrational operations); the half-up tie (e.g. 15.005 -> 15.01) is therefore decided exactly.
"""

from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F  # noqa: F401

TEMPLATE_ID = "h115"


def solve(text: str, q: dict) -> dict:
    # ---- parse (anchored on surrounding words) --------------------------------------------
    i0 = grab(r"requires {N} at time 0", text)
    basis = grab(r"unchanged tax basis {N}", text)
    dist = grab(r"after-tax distribution {N} at the end of year 1", text)
    price = grab(r"is sold for {N}", text)
    cost_frac = grab(r"selling costs equal the fraction {N} of gross price", text)
    tax_rate = grab(r"capital-gains tax equals {N} of the positive gain", text)
    r0 = grab(r"trial rate {N}", text)
    cap = grab(r"rate-step cap {N}", text)

    # ---- year-2 sale waterfall ------------------------------------------------------------
    net_proceeds = price * (1 - cost_frac)          # after proportional selling costs, before tax
    gain = net_proceeds - basis                     # basis unchanged by the year-1 distribution
    tax = tax_rate * (gain if gain > 0 else Fraction(0))
    after_tax_sale = net_proceeds - tax

    # ---- NPV and its derivative at the trial rate ----------------------------------------
    g = 1 + r0
    npv = -i0 + dist / g + after_tax_sale / g**2
    d_npv = -dist / g**2 - 2 * after_tax_sale / g**3
    magnitude = abs(d_npv)                          # negative-derivative magnitude

    # ---- one Newton-Raphson correction with absolute step cap -----------------------------
    raw = npv / magnitude                           # = -npv / d_npv (d_npv < 0)
    step = raw if raw < cap else cap                # smaller of raw correction and cap
    new_rate = r0 + step

    return {
        "final": new_rate * 100,                    # annual percentage
        "slots": {"net_sale_proceeds_after_cost_checkpoint": net_proceeds},
    }
