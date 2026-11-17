import re

from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.kyc.customer_type.basic.v1"


def _split_ids(chunk: str) -> list[str]:
    return [p for p in re.split(r"\s*,\s*(?:and\s+)?|\s+and\s+", chunk.strip()) if p]


def solve(text: str, q: dict) -> dict:
    nature = re.search(r"The account nature is (\w+)\.", text).group(1)
    holders = grab(r"number of account holders is {N}", text)

    # Mapping parsed from the text (identifier lists can be permuted across instances).
    family = cls = None
    rx = r"The identifiers? ([\w ,]+?) belongs? to (\w+) and maps? to (\w+)\."
    for ids, fam, c in re.findall(rx, text):
        if nature in _split_ids(ids):
            family, cls = fam, c
            break
    if family is None:
        raise ValueError(f"identifier {nature!r} not mapped")

    # "one holder is single_holder and more than one holder is multiple_holders"
    holder_cfg = "multiple_holders" if holders > 1 else "single_holder"

    return {
        "final": cls,
        "slots": {"legal_form_family": family, "holder_configuration": holder_cfg},
    }
