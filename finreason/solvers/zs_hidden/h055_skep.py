"""h055 -- linear + convexity loss, capped dollar loss vs budget (skeptic / ambiguity-hunting pass).

Structure (all 3 instances):
    A portfolio worth W faces positive downside shock ratio S. Its linear loss sensitivity is L,
    and its convexity multiplier C applies to the square of the shock. Add the linear and
    convexity loss rates, convert the result to a gross dollar loss, and cap that loss at K.
    Compare the capped loss with budget B. Return within_budget when the capped loss does not
    exceed the budget and budget_breach otherwise.

Checkpoint: convexity_ratio_checkpoint (position 1) "Report the convexity loss ratio", unit ratio, 6 dp half-up.

AMBIGUITIES CONSIDERED AND HOW THEY WERE RESOLVED
-------------------------------------------------
A1  What quantity is the "convexity loss ratio"?
    Candidates: (a) the convexity loss RATE = C * S^2 (loss as a fraction of portfolio value, same
    scale as the "shock ratio"); (b) convexity loss / linear loss; (c) convexity loss / total loss.
    Resolution: (a).  The text names "the linear and convexity loss rates" as the two addends, the
    checkpoint is at position 1 (i.e. before the addition), its unit is "ratio" exactly like the
    "shock ratio" input, and (b)/(c) are comparisons the text never asks for.  The 6-dp spec also
    matches C*S^2 exactly (0.97345 * 0.2^2 = 0.038938).
A2  Is there a 1/2 factor on the convexity term (bond-convexity convention 1/2*C*dy^2)?
    Resolution: no.  "convexity multiplier C applies to the square of the shock" -> C * S^2 as worded.
A3  Linear loss rate = L * S (a sensitivity is per unit of shock), not L alone.  "linear loss
    sensitivity" + "shock" -> product; the text then speaks of the "linear ... loss rate".
A4  Sign of the shock: "positive downside shock ratio" -> S is a positive magnitude of a downside
    move; it is used as parsed (S^2 is sign-safe anyway).
A5  "convert the result to a gross dollar loss" -> (L*S + C*S^2) * W.  No netting of anything.
A6  "cap that loss at K": "that loss" is the gross DOLLAR loss (the thing just computed), so the cap
    is in dollars: capped = min(gross, K).  No floor at zero is stated, none applied.
A7  "within_budget when the capped loss does not exceed the budget": capped <= B -> within_budget,
    otherwise budget_breach.  A tie (capped == B) is within_budget.  Instance 2 is exactly this tie
    (2.45 capped to 2 vs budget 2), so exact Fractions matter.
A8  No intermediate rounding is stated anywhere -> nothing is rounded inside the computation; the
    checkpoint is returned unrounded and the framework applies 6-dp half-up.
A9  Units: every input is a plain ratio / dollar amount, no percents.  Defensively, a number that is
    immediately followed by "percent" or "%" would be divided by 100 (never triggers on these texts).
A10 The decision rule is read from the "Return X when <clause> and Y otherwise" sentence: the
    comparison in <clause> (non-strict forms such as "does not exceed" are tested before strict
    ones such as "exceeds") is attached to whichever token owns the clause, so an inverted phrasing
    ("Return budget_breach when ... exceeds ...") would still be decided correctly.  Unparseable
    phrasing falls back to the literal rule of these texts: within_budget iff capped <= budget.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, after

TEMPLATE_ID = "h055"

_CUR = r"(?:USD\s*|\$\s*)?"            # optional currency marker before a number
_LINK = r"(?:\s+(?:is|of|equal to|equals|at))?\s*(?:of\s*)?"   # optional "is"/"of" between label and number


def _num(text: str, patterns: list[str], fallback_phrase: str) -> Fraction:
    """Anchored number grab; tries each pattern, then falls back to 'first number after phrase'.

    A number directly followed by 'percent' or '%' is converted to a ratio (defensive only).
    """
    for pat in patterns:
        rx = pat.replace("{N}", f"({NUMBER})")
        m = re.search(rx, text, flags=re.S | re.I)
        if m:
            val = F(m.group(1))
            tail = text[m.end(1):m.end(1) + 10].lstrip()
            if tail.startswith("%") or tail.lower().startswith("percent"):
                val /= 100
            return val
    return after(text, fallback_phrase)


_WITHIN, _BREACH = "within_budget", "budget_breach"


def _within_predicate(text: str):
    """Predicate (capped, budget) -> True when the answer is within_budget.

    Reads 'Return X when <clause> and Y otherwise' and the comparison the clause expresses
    (these texts: X = within_budget, clause = 'does not exceed' -> capped <= budget).  The
    non-strict forms are tested before the strict ones so 'does not exceed' never matches 'exceeds'.
    Any unparseable phrasing falls back to the literal rule of these instances: capped <= budget.
    """
    m = re.search(r"Return\s+`?([A-Za-z_]+)`?\s+when\s+(.*?)\s+and\s+`?([A-Za-z_]+)`?\s+otherwise", text, flags=re.S | re.I)
    default = lambda c, b: c <= b  # noqa: E731
    if not m:
        return default
    tok_when, clause = m.group(1), m.group(2).lower()
    if re.search(r"not exceed|at most|no more than|no greater than|less than or equal|not (?:greater|more|larger) than|within", clause):
        pred = lambda c, b: c <= b  # noqa: E731
    elif re.search(r"at least|no less than|not less than|not below|greater than or equal|reaches|(?:equals|meets) or exceeds", clause):
        pred = lambda c, b: c >= b  # noqa: E731
    elif re.search(r"exceed|greater than|more than|larger than|above|over", clause):
        pred = lambda c, b: c > b  # noqa: E731
    elif re.search(r"below|less than|under|smaller than", clause):
        pred = lambda c, b: c < b  # noqa: E731
    else:
        return default
    if tok_when == _WITHIN:
        return pred
    if tok_when == _BREACH:
        return lambda c, b: not pred(c, b)
    return default


def solve(text: str, q: dict) -> dict:
    worth = _num(text, [rf"portfolio\s+worth{_LINK}{_CUR}{{N}}", rf"worth{_LINK}{_CUR}{{N}}"], "worth")
    shock = _num(text, [rf"shock\s+ratio{_LINK}{{N}}", rf"shock{_LINK}{{N}}"], "shock ratio")
    lin_sens = _num(text, [rf"linear\s+loss\s+sensitivity{_LINK}{{N}}", rf"linear[^.]*?sensitivity{_LINK}{{N}}"],
                    "linear loss sensitivity")
    conv_mult = _num(text, [rf"convexity\s+multiplier{_LINK}{{N}}", rf"convexity[^.]*?multiplier{_LINK}{{N}}"],
                     "convexity multiplier")
    cap = _num(text, [rf"cap\s+(?:that|the|this)?\s*(?:dollar\s+)?loss\s+at{_LINK}{_CUR}{{N}}", rf"cap[^.]*?at{_LINK}{_CUR}{{N}}"],
               "cap")
    budget = _num(text, [rf"with\s+(?:the\s+)?budget{_LINK}{_CUR}{{N}}", rf"budget{_LINK}{_CUR}{{N}}"], "budget")

    # A3: linear loss rate; A1/A2: convexity loss rate (ratio of portfolio value), no 1/2 factor.
    linear_rate = lin_sens * shock
    convexity_rate = conv_mult * shock * shock

    # A5: total loss rate -> gross dollar loss.
    total_rate = linear_rate + convexity_rate
    gross_loss = total_rate * worth

    # A6: cap the dollar loss.
    capped_loss = min(gross_loss, cap)

    # A7: "does not exceed" -> <= ; tie is within budget.
    within = _within_predicate(text)
    final = _WITHIN if within(capped_loss, budget) else _BREACH

    return {
        "final": final,
        "slots": {"convexity_ratio_checkpoint": convexity_rate},
    }
