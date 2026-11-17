# FINANCE MODEL (h053): percentage-scaled HHI-style concentration of modeled exposures.
#
# Three nonoverlapping categories exhaust the exposure pool.  For category i:
#   V_i = covered volume (USD)
#   r_i = "decimal assessment ratio" -- a plain decimal ratio (0.5 means one half), NOT a percent
#   P_i = V_i * r_i                    modeled exposure (USD), pre-normalization
#   T   = P_1 + P_2 + P_3              total modeled exposure pool
#   s_i = P_i / T                      share of the pool
#   H   = s_1^2 + s_2^2 + s_3^2        HHI on a 0..1 scale (>= 1/3, < 1)
#   answer = 100 * H                   percent (unit "percent": 12.5 means 12.5%)
#
# Checkpoints (before normalization, USD, unrounded -- framework rounds half-up to 2 dp):
#   category_1_exposure_checkpoint = P_1
#   category_2_exposure_checkpoint = P_2
#
# Overrides / conventions noted:
#   - Not the 0-10,000 HHI scale: the text asks for 100H as a percent, so 100 * sum(s_i^2).
#   - Everything is exact Fraction arithmetic; only the final value is rounded (by the framework).
#   - The ratios may in principle differ per category, so each is parsed per category (not assumed 0.5).

import re
from fractions import Fraction

from finreason.nums import NUMBER, F

TEMPLATE_ID = "h053"


def _category(text: str, k: int):
    """Return (volume, ratio) for category k.

    Handles "Category 1 has covered volume 4096.004 USD and decimal assessment ratio 0.5"
    and the shortened form "Category 2 has 11794.812 USD and 0.5".
    """
    pat = (
        rf"Category\s+{k}\s+has\s+(?:covered\s+volume\s+)?({NUMBER})\s*USD\s+and\s+"
        rf"(?:decimal\s+assessment\s+ratio\s+)?({NUMBER})"
    )
    m = re.search(pat, text, flags=re.S)
    if m is None:
        raise ValueError(f"category {k} not found")
    return F(m.group(1)), F(m.group(2))


def solve(text: str, q: dict) -> dict:
    cats = [_category(text, k) for k in (1, 2, 3)]
    p = [v * r for v, r in cats]  # modeled exposure P_i = volume * assessment ratio
    total = sum(p, Fraction(0))
    shares = [pi / total for pi in p]
    h = sum((s * s for s in shares), Fraction(0))
    final = 100 * h  # percentage-scaled HHI-style score
    return {
        "final": final,
        "slots": {
            "category_1_exposure_checkpoint": p[0],
            "category_2_exposure_checkpoint": p[1],
        },
    }
