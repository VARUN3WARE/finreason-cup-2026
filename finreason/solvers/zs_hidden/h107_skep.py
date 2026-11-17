"""h107 -- closed FX round-trip routes: Route A (three legs) vs Route B (two legs).

Chain: gross multiplier (product of leg rates) -> gross USD proceeds = capital * multiplier
       -> apply the route's single proportional fee once -> subtract the route's fixed USD cost
       -> exact terminal value -> hurdle test -> selection.

AMBIGUITIES HUNTED AND RESOLVED (evidence in brackets)
------------------------------------------------------
1. Direction of each quoted rate.  Every leg is quoted as units RECEIVED per unit GIVEN
   ["USD to X ... 0.5 is X per USD", "... 1.6 is USD per Y" on the Y->USD leg], so the
   gross multiplier is the plain product of the quoted rates.  The code still parses the
   path (USD -> X -> Y -> USD) and the two currency names of every quote, and would invert a
   quote only if it were stated the other way round; any unit mismatch raises instead of
   silently guessing.
2. "Gross multiplier" = product of the leg rates only, i.e. terminal USD per starting USD
   BEFORE fee and fixed cost [slot unit "ratio"; "gross" vs. the net terminal value].  It does
   NOT include the starting capital.
3. Proportional fee "0.1" is a proportion (10 %), not a percent figure [same convention as the
   hurdle "0.08"/"0" and the whole question uses bare ratios].  It is applied ONCE to the
   final USD proceeds of the closed route: net = capital * multiplier * (1 - fee)
   ["apply its single aggregate proportional fee ... once to final USD proceeds"].
   Not fee/(1+fee), not applied per leg, not applied to profit only.
4. Order of fee vs fixed cost: fee first, then the fixed USD cost is subtracted
   ["... to final USD proceeds, then subtract fixed USD cost"].  terminal = net - fixed.
5. Mapping of the "p or q" pairs: first value -> Route A, second value -> Route B, i.e. the
   order in which the routes are introduced ["each closed route ... its ... fee 0.1 or 0.1",
   "fixed USD cost 13 or 21"].
6. Hurdle test.  "qualifies only if its exact terminal value meets return hurdle h on starting
   capital" is a RETURN hurdle: (terminal - capital) / capital >= h, i.e.
   terminal >= capital * (1 + h).  The alternative "terminal >= h * capital" would make
   hurdle 0 (instance 2) a vacuous test and would leave the "No trade" token unreachable
   in this cluster, whereas the return reading yields exactly one instance per enum token.
   "meets" is non-strict (>=), evaluated on exact Fractions.
7. Selection is on the exact (unrounded) TERMINAL VALUE of qualifying routes only
   ["Select the qualifying route with the higher exact terminal value"], never on the
   multiplier.  Both qualify and exactly equal -> Route A.  One qualifies -> that one.
   Neither -> "No trade".
8. Nothing is rounded inside the computation ("exact terminal value"); checkpoints are the
   unrounded multipliers and the framework applies the 8-decimal half-up rendering.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab, grab_all

TEMPLATE_ID = "h107"

_CUR = r"[A-Za-z]+"
_SENTENCE_END = re.compile(r"\.\s+[A-Z]")  # a period followed by a new sentence (not a decimal point)
_PATH_RE = re.compile(rf"follows\s+((?:{_CUR}\s+to\s+)+{_CUR})\s*:")
_LEG_RE = re.compile(rf"({NUMBER})\s+is\s+({_CUR})\s+per\s+({_CUR})")


def _route_sentence(text: str, label: str) -> str:
    """The sentence 'Route <label> follows ...' up to (not including) the next sentence."""
    start = text.index(f"Route {label} follows")
    m = _SENTENCE_END.search(text, start)
    return text[start : m.start() if m else len(text)]


def _gross_multiplier(text: str, label: str) -> Fraction:
    """Product of the leg rates along the closed route, each oriented as received-per-given."""
    sentence = _route_sentence(text, label)
    pm = _PATH_RE.search(sentence)
    if pm is None:
        raise ValueError(f"route path not found for Route {label}")
    path = [c.strip() for c in re.split(r"\s+to\s+", pm.group(1))]
    legs = _LEG_RE.findall(sentence[pm.end() :])
    if len(legs) != len(path) - 1:
        raise ValueError(f"Route {label}: {len(legs)} quotes for {len(path) - 1} legs")
    if path[0] != path[-1]:
        raise ValueError(f"Route {label} is not a closed route: {path}")
    mult = Fraction(1)
    for (frm, to), (rate_s, num_cur, den_cur) in zip(zip(path, path[1:]), legs):
        rate = F(rate_s)
        if num_cur == to and den_cur == frm:
            mult *= rate  # quoted as 'to' per 'frm' -> multiply directly
        elif num_cur == frm and den_cur == to:
            mult *= 1 / rate  # quoted the other way round -> invert
        else:
            raise ValueError(f"Route {label}: quote {num_cur} per {den_cur} does not fit leg {frm}->{to}")
    return mult


def solve(text: str, q: dict) -> dict:
    capital = grab(r"Starting with USD capital {N}", text)
    mult_a = _gross_multiplier(text, "A")
    mult_b = _gross_multiplier(text, "B")
    fee_a, fee_b = grab_all(r"proportional fee {N} or {N}", text)
    fixed_a, fixed_b = grab_all(r"fixed USD cost {N} or {N}", text)
    hurdle = grab(r"return hurdle {N} on starting capital", text)

    # Exact terminal values: fee applied once to gross USD proceeds, then the fixed cost.
    terminal_a = capital * mult_a * (1 - fee_a) - fixed_a
    terminal_b = capital * mult_b * (1 - fee_b) - fixed_b

    # Return hurdle on starting capital: (terminal - capital) / capital >= hurdle  (non-strict).
    required = capital * (1 + hurdle)
    qual_a = terminal_a >= required
    qual_b = terminal_b >= required

    if qual_a and qual_b:
        final = "Route A" if terminal_a >= terminal_b else "Route B"  # exact tie -> Route A
    elif qual_a:
        final = "Route A"
    elif qual_b:
        final = "Route B"
    else:
        final = "No trade"

    return {
        "final": final,
        "slots": {
            "a_gross_multiplier_checkpoint": mult_a,
            "b_gross_multiplier_checkpoint": mult_b,
        },
    }
