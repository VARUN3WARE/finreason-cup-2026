"""h018 -- literal transcription: three-stage share issuance, pro forma EPS floor, pick option."""
from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "h018"


def solve(text: str, q: dict) -> dict:
    # "A company has current common EPS {N} and requires pro forma EPS of at least {N}."
    eps0 = grab(r"current common EPS {N}", text)
    floor = grab(r"pro forma EPS of at least {N}", text)
    # "each financing option completes exactly {N} sequential common-share issuance stages"

    import re
    m = re.search(r"completes exactly (\w+) sequential", text)
    words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6}
    tok = m.group(1)
    stages = words[tok] if tok in words else int(tok)
    # Option A
    add_a = grab(r"Option A adds total earnings of {N} per current share", text)
    r_a = grab(r"per-stage share-base increase is {N}", text)
    # cumulative share multiple is (1 + the ratio)^stages
    exp_a = int(grab(r"cumulative share multiple is \(1 \+ the ratio\)\^{N}", text))
    mult_a_one = 1 + r_a
    mult_a = mult_a_one ** exp_a
    # Option B
    add_b = grab(r"Option B analogously adds {N} per current share", text)
    r_b = grab(r"uses per-stage increase {N}", text)
    exp_b = int(grab(r"for cumulative multiple \(1 \+ the ratio\)\^{N}", text))
    assert exp_a == stages and exp_b == stages
    mult_b = (1 + r_b) ** exp_b
    # pro forma EPS = (current earnings per current share + added earnings per current share) / share multiple
    eps_a = (eps0 + add_a) / mult_a
    eps_b = (eps0 + add_b) / mult_b
    qa = eps_a >= floor
    qb = eps_b >= floor
    if qa and qb:
        final = "option_a" if eps_a >= eps_b else "option_b"
    elif qa:
        final = "option_a"
    elif qb:
        final = "option_b"
    else:
        final = "neither_option"
    return {"final": final, "slots": {"a_one_stage_share_multiple_checkpoint": mult_a_one}}
