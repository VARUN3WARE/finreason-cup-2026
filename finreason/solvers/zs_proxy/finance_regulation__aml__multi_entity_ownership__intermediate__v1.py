"""Multi-entity ownership: aggregate = A + B + C; largest = max(A, B, C);
review (final) = aggregate >= aggregate threshold OR largest >= single-entity threshold."""

import re

from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.aml.multi_entity_ownership.intermediate.v1"


def _tok(b: bool) -> str:
    return "true" if b else "false"


def solve(text: str, q: dict) -> dict:
    entities = []
    for m in re.finditer(r"Entity (\w+) ownership percent is", text):
        entities.append(grab(r"Entity " + re.escape(m.group(1)) + r" ownership percent is {N}", text))
    if len(entities) < 1:
        raise ValueError("no entities parsed")
    agg_thr = grab(r"aggregate threshold percent is {N}", text)
    single_thr = grab(r"single-entity threshold percent is {N}", text)
    aggregate = sum(entities[1:], entities[0])
    largest = max(entities)
    final = aggregate >= agg_thr or largest >= single_thr
    return {
        "final": _tok(final),
        "slots": {"aggregate_ownership_percent": aggregate, "largest_entity_percent": largest},
    }
