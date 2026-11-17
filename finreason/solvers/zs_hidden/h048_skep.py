"""Hidden cluster h048 -- recovery rate needed after a revenue downturn.

Structure (identical wording across the 3 instances):
    "A company starts with revenue R0 and then experiences a downturn ratio d.
     It must reach target revenue T after recovery. Assuming the target exceeds
     the post-downturn revenue, compute the required recovery rate as the
     additional revenue needed divided by post-downturn revenue, and report
     that rate as a percentage."

AMBIGUITY HUNT -- resolutions with textual evidence
---------------------------------------------------
A1. "downturn ratio d": fraction LOST (post = R0 * (1 - d)) vs fraction RETAINED
    (post = R0 * d).  Resolved as fraction lost.  Evidence: the word "downturn"
    names the decline, and instance 2 (R0 = 6803/66 ~ 103.08, d = 0.01,
    T = 103) is only sensible under this reading -- post = 102.045 sits just
    below the target, exactly the near-miss the sentence "Assuming the target
    exceeds the post-downturn revenue" is guarding.  Under "retained", post
    would be 1.03 and the rate ~9900 %, making that premise vacuous.  Instances
    1 and 3 (d = 0.5) give the same post under either reading.
A2. Base of the recovery rate: the text says "divided by post-downturn revenue"
    -- NOT the starting revenue.  rate = (T - post) / post.
A3. "additional revenue needed" = T - post.  The premise "Assuming the target
    exceeds the post-downturn revenue" makes this positive; no floor/clamp is
    stated, so none is applied (all 3 instances satisfy the premise anyway).
A4. Units: final "report that rate as a percentage" and the answer_spec unit is
    `percent` -> return rate * 100 (unrounded; framework rounds half-up 2dp).
    Checkpoint "revenue immediately after the downturn" is in USD -> return
    post itself (unrounded; framework rounds half-up 2dp).
A5. No intermediate rounding: "use exact arithmetic through all intermediate
    steps, round only the final value".  The displayed 2-dp checkpoint is never
    fed back into the rate.
A6. Parsing: R0 may be rational ("6803/66"); the NUMBER capture handles that.
    d is a plain ratio in all 3 instances ("0.5", "0.01"); a defensive branch
    divides by 100 only if the text literally says "downturn ratio X percent".
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h048"


def solve(text: str, q: dict) -> dict:
    r0 = grab(r"starts with revenue\s+{N}", text)
    d = grab(r"downturn ratio\s+{N}", text)
    if re.search(r"downturn ratio\s+-?[\d.,/]+\s*(?:percent|%)", text):
        d = d / 100  # A6: only if explicitly stated as a percent (not the case here)
    target = grab(r"target revenue\s+{N}", text)

    # A1: downturn ratio is the fraction of revenue lost.
    post = r0 * (Fraction(1) - d)

    # A2/A3: additional revenue needed over post-downturn revenue.
    additional = target - post
    rate = additional / post

    # A4: percent units for the final; USD for the checkpoint.
    return {
        "final": rate * 100,
        "slots": {"post_downturn_checkpoint": post},
    }
