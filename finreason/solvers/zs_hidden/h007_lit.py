"""h007 -- two-bond holding-period-return screen (literal transcription).

Sentence-by-sentence:
  1. "Compare two bonds over a common holding horizon and valuation date."  (context only)
  2. "Bond A has expected redemption cash R, aggregate coupon cash C, clean price P,
      settlement cost S, and modified duration D."
  3. Same sentence for Bond B.
  4. "Each settlement cost is all acquisition cash beyond the clean quote ... do not add
      those amounts again."  -> outlay = clean + settlement only (no extra accrued/fees).
  5. "Both durations use the same acquisition-date convention and basis."  -> compare D directly.
  6. Definitions (verbatim):
        total received cash      = redemption + aggregate coupons
        total acquisition outlay = clean price + settlement cost
        holding-period return    = (received - outlay) / outlay
  7. "A bond qualifies only if its exact holding-period return is at least the exact ratio T
      and its modified duration is at most M."   -> hpr >= T and D <= M  (both inclusive)
  8. "Return the qualifying bond with the higher exact return, choose Bond A on an exact tie,
      or return Neither when neither qualifies."
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h007"


def _bond_terms(name: str, text: str) -> dict:
    # Isolate the sentence that starts "Bond X has ..." and parse each named field from it.
    m = re.search(rf"{name} has (.*?)\.(?:\s|$)(?!\d)", text, flags=re.S)
    if m is None:
        raise ValueError(f"no terms sentence for {name}")
    s = m.group(1)

    def field(label: str) -> Fraction:
        return grab(rf"{label}(?: of)?(?: USD)?\s*\$?\s*{{N}}", s)

    return {
        "redemption": field(r"expected redemption cash"),
        "coupons": field(r"aggregate coupon cash"),
        "clean": field(r"clean price"),
        "settlement": field(r"settlement cost"),
        "mod_duration": field(r"modified duration"),
    }


def _return_threshold(text: str) -> Fraction:
    # "its exact holding-period return is at least the exact ratio T"
    m = re.search(rf"holding-period return is at least the exact ratio ({NUMBER})", text)
    if m:
        return F(m.group(1))
    # tolerance for a percent phrasing
    m = re.search(rf"holding-period return is at least (?:the exact )?({NUMBER}) ?(?:percent|%)", text)
    if m:
        return F(m.group(1)) / 100
    return grab(r"holding-period return is at least[^0-9\-]*{N}", text)


def _duration_cap(text: str) -> Fraction:
    # "its modified duration is at most M"
    return grab(r"its modified duration is at most {N}", text)


def solve(text: str, q: dict) -> dict:
    # Sentences 2-3: bond terms.
    bonds = {"Bond A": _bond_terms("Bond A", text), "Bond B": _bond_terms("Bond B", text)}

    # Sentence 7: qualification thresholds.
    t_ret = _return_threshold(text)
    d_cap = _duration_cap(text)

    results = {}
    for name, b in bonds.items():
        # Sentence 6: definitions, verbatim.
        total_received = b["redemption"] + b["coupons"]
        total_outlay = b["clean"] + b["settlement"]  # sentence 4: nothing else added
        hpr = (total_received - total_outlay) / total_outlay
        # Sentence 7: at least / at most -> inclusive comparisons, on exact values.
        qualifies = (hpr >= t_ret) and (b["mod_duration"] <= d_cap)
        results[name] = {"outlay": total_outlay, "hpr": hpr, "qualifies": qualifies}

    # Sentence 8: selection rule.
    a, bb = results["Bond A"], results["Bond B"]
    if a["qualifies"] and bb["qualifies"]:
        final = "Bond A" if a["hpr"] >= bb["hpr"] else "Bond B"  # exact tie -> Bond A
    elif a["qualifies"]:
        final = "Bond A"
    elif bb["qualifies"]:
        final = "Bond B"
    else:
        final = "Neither"

    return {
        "final": final,
        "slots": {
            "a_outlay_checkpoint": a["outlay"],
            "b_outlay_checkpoint": bb["outlay"],
        },
    }
