"""Customer type taxonomy: account-nature identifier -> legal-form family and customer class."""
import re

from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.kyc.customer_type.basic.v1"


def _taxonomy(text: str) -> dict:
    out = {}
    pat = re.compile(r"The identifiers? ([a-z_, ]+?) (?:belong|belongs) to ([a-z_]+) and (?:map|maps) to ([a-z_]+)")
    for ids, fam, cls in pat.findall(text):
        for ident in re.split(r",\s*(?:and\s+)?|\s+and\s+", ids):
            ident = ident.strip()
            if ident:
                out[ident] = (fam, cls)
    return out


def solve(text: str, q: dict) -> dict:
    nature = re.search(r"The account nature is ([a-z_]+)", text).group(1)
    holders = grab(r"number of account holders is {N}", text)
    fam, cls = _taxonomy(text)[nature]
    config = "single_holder" if holders == 1 else "multiple_holders"
    return {"final": cls, "slots": {"legal_form_family": fam, "holder_configuration": config}}
