"""h042 -- primary/backup payment retry: expected net merchant proceeds.

Chain (exact expectations):
  primary failures  PF = N * (1 - p)
  backup successes  BS = PF * q          (q = conditional success of the single retry)
  terminal failures TF = PF * (1 - q)
  settled revenue   = (N * p + BS) * A
  primary fees      = N  * (rp * A + fp)  (every original attempt)
  backup fees       = PF * (rb * A + fb)  (every retry, success or failure)
  handling          = h1 * PF + h2 * TF   (h2 is the "additional" cost per both-fail order)
  net               = revenue - primary fees - backup fees - handling - batch fee
Checkpoints: retry-success fraction of original attempts = (1 - p) * q;
             backup fees; terminal-failure additional handling = h2 * TF.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h042"


def _rate(pattern: str, text: str) -> Fraction:
    """Number followed optionally by 'percent'/'%' -> ratio."""
    import re
    from finreason.nums import NUMBER

    rx = pattern.replace("{N}", f"({NUMBER})\\s*(percent|%)?")
    m = re.search(rx, text, flags=re.S)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    v = Fraction(m.group(1).replace(",", ""))
    if m.group(2):
        v /= 100
    return v


def solve(text: str, q: dict) -> dict:
    n = grab(r"has {N} original payment attempts", text)
    amt = grab(r"original payment attempts, each for {N}", text)
    p = _rate(r"primary processor succeeds with probability {N}", text)
    qb = _rate(r"conditional success probability is {N}", text)

    rp = _rate(r"primary charges {N}\s*(?:of the stated amount)", text)
    fp = grab(r"primary charges .*?fixed fee {N}", text)
    rb = _rate(r"backup charges {N}\s*(?:of the stated amount)", text)
    fb = grab(r"backup charges .*?fixed fee {N}", text)

    h1 = grab(r"incurs {N} for every primary failure", text)
    h2 = grab(r"additional {N} for every order where both attempts fail", text)
    batch = grab(r"pays {N} once for the batch", text)

    pf = n * (1 - p)          # primary failures = retries
    bs = pf * qb              # backup successes
    tf = pf * (1 - qb)        # both attempts fail

    revenue = (n * p + bs) * amt
    primary_fees = n * (rp * amt + fp)
    backup_fees = pf * (rb * amt + fb)
    primary_fail_handling = h1 * pf
    terminal_cost = h2 * tf

    net = revenue - primary_fees - backup_fees - primary_fail_handling - terminal_cost - batch

    return {
        "final": net,
        "slots": {
            "retry_success_fraction_checkpoint": (1 - p) * qb,
            "backup_processing_fees_checkpoint": backup_fees,
            "terminal_failure_cost_checkpoint": terminal_cost,
        },
    }
