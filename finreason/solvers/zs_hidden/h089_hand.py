from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h089"


def solve(text: str, q: dict) -> dict:
    sof = grab(r"source-of-funds risk score\s+{N}", text)
    jur = grab(r"jurisdiction risk score\s+{N}", text)
    existing = grab(r"existing verified-control credit\s+{N}", text)
    ceiling = grab(r"residual-risk ceiling\s+{N}", text)

    combined = sof + jur
    # Need combined - existing - additional <= ceiling, additional >= 0.
    required = combined - existing - ceiling
    if required < 0:
        required = Fraction(0)

    return {"final": required, "slots": {"combined_risk_checkpoint": combined}}
