# FINANCE MODEL (h062): break-even / target exit FX quote for a round-trip currency position
#
# Setup
#   C   = initial reporting-currency capital (cancels out of every ratio; any C > 0 gives the same answer)
#   q0  = normalized entry quote, reporting-currency units PER base-currency unit (given, may be a rational)
#   q1  = normalized exit quote, same convention (the unknown, to be solved for)
#   f0  = entry fee ratio (given as "one minus fee ratio {f0}")  -> retained fraction at entry = 1 - f0
#   f1  = exit fee ratio                                          -> retained fraction at exit  = 1 - f1
#   k   = financing charge as a multiple of initial capital C (deducted in reporting currency at the end)
#   R   = target net return (on initial capital C)
#
# Cash flow
#   1. Entry: C reporting units buy C / q0 base units (quote is reporting per base, so base = reporting / quote).
#      After the entry fee, retained base = (C / q0) * (1 - f0).
#   2. Exit: all retained base is sold at q1 (reporting per base): proceeds = (C / q0) * (1 - f0) * q1,
#      after the exit fee: (C / q0) * (1 - f0) * q1 * (1 - f1).
#   3. Financing charge: subtract k * C.
#      Terminal reporting wealth W = C * (1 - f0)(1 - f1) q1 / q0  -  k * C.
#   4. Net return = (W - C) / C = (1 - f0)(1 - f1) q1 / q0 - k - 1.
#
# Solve for threshold:  net return = R
#   (1 - f0)(1 - f1) q1 / q0 = 1 + R + k
#   => checkpoint "return-and-carry gross growth multiple" G = 1 + R + k
#      (the gross multiple on capital that must be earned to cover capital, target return and the carry/financing)
#   => q1 = G * q0 / ((1 - f0)(1 - f1))                                  [final answer, ratio]
#
# Interpretations / overrides noted
#   * "retains one minus fee ratio 0.02" is read as: retained fraction = 1 - 0.02 (fee ratio 0.02), i.e. "one minus
#     [fee ratio 0.02]". The alternative (retained fraction literally 0.02) gives absurd exit quotes (hundreds vs an
#     entry quote near 1) so it is rejected.
#   * Net return is measured on initial capital after the financing charge: (W - C)/C. Fees are multiplicative on the
#     converted amounts (not additive on capital). No compounding/time value (single period, no rates).
#   * Everything is exact Fraction arithmetic; the framework applies half-up rounding to 6 dp.

from fractions import Fraction

from finreason.nums import grab, F  # noqa: F401

TEMPLATE_ID = "h062"


def solve(text: str, q: dict) -> dict:
    q0 = grab(r"entry quote {N}", text)
    f0 = grab(r"entry conversion retains one minus fee ratio {N}", text)
    f1 = grab(r"exit.*?retain one minus fee ratio {N}", text)
    k = grab(r"financing charge equal to {N} times", text)
    target = grab(r"net return equals {N}", text)

    gross_growth = 1 + target + k                      # required gross growth multiple on capital
    retained = (1 - f0) * (1 - f1)                     # combined fee retention across entry and exit
    exit_quote = gross_growth * q0 / retained          # reporting units per base unit

    return {
        "final": Fraction(exit_quote),
        "slots": {"gross_growth_checkpoint": Fraction(gross_growth)},
    }
