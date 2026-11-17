"""h056: two-factor linear loss + joint interaction + concentration square; capital = max(modeled, external)."""

from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "h056"


def solve(text: str, q: dict) -> dict:
    value = grab(r"portfolio worth (?:USD\s*)?\$?{N}", text)
    s1, s2 = grab_all(r"factor shock ratios {N} and {N}", text)
    b1, b2 = grab_all(r"loss sensitivities {N} and {N}", text)
    k = grab(r"product of both shocks and {N}", text)
    c = grab(r"concentration ratio {N}", text)
    ext = grab(r"external stress loss (?:of\s*)?(?:USD\s*)?\$?{N}", text)

    linear = s1 * b1 + s2 * b2          # sum of both linear factor loss rates
    joint = s1 * s2 * k                  # joint interaction loss ratio
    conc = c * c                         # concentration square
    rate = linear + joint + conc         # modeled loss rate
    modeled = value * rate               # modeled loss (USD)
    capital = max(modeled, ext)          # larger of modeled and external stress loss

    return {"final": Fraction(capital), "slots": {"joint_ratio_checkpoint": joint}}
