import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "fp.finance_regulation.kyc.customer_risk_rating.advanced.v1"

_WORDS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5}


def _account_points(text: str) -> dict[str, Fraction]:
    m = re.search(r"Account points are (.*?)\.(?:\s|$)", text)
    if m is None:
        raise ValueError("account points not found")
    return {k: F(v) for k, v in re.findall(rf"(\w+)\s*=\s*({NUMBER})", m.group(1))}


def _volume_points(volume: Fraction, text: str) -> Fraction:
    m = re.search(r"Volume points are (.*?)\.(?:\s|$)", text)
    if m is None:
        raise ValueError("volume bands not found")
    sentence = m.group(1)
    bands = []
    rx = (
        rf"({NUMBER}) for volume "
        rf"(?:above USD ({NUMBER}) and at most USD ({NUMBER})"
        rf"|at most USD ({NUMBER})"
        rf"|above USD ({NUMBER}))"
    )
    for pts, lo_mid, hi_mid, hi_only, lo_only in re.findall(rx, sentence):
        lo = F(lo_mid) if lo_mid else (F(lo_only) if lo_only else None)  # strict lower bound
        hi = F(hi_mid) if hi_mid else (F(hi_only) if hi_only else None)  # inclusive upper bound
        bands.append((F(pts), lo, hi))
    if not bands:
        raise ValueError("no volume bands parsed")
    for pts, lo, hi in bands:
        if (lo is None or volume > lo) and (hi is None or volume <= hi):
            return pts
    raise ValueError(f"volume {volume} matches no band")


def solve(text: str, q: dict) -> dict:
    residency = grab(r"residency risk points are {N}", text)
    acct = re.search(r"The account type is (\w+)\.", text).group(1)
    volume = grab(r"transaction volume in whole USD is {N}", text)

    acct_pts = _account_points(text)[acct]
    vol_pts = _volume_points(volume, text)

    # Escalation: bonus applies exactly when account type matches AND volume strictly above threshold.
    em = re.search(
        rf"Add an? ([\w-]+?)-point escalation bonus exactly when account type is (\w+) "
        rf"and volume is (above|at least) USD ({NUMBER})",
        text,
    )
    if em is None:
        raise ValueError("escalation rule not found")
    word = em.group(1).lower()
    bonus_value = Fraction(_WORDS[word]) if word in _WORDS else F(word)
    e_acct, e_cmp, e_thr = em.group(2), em.group(3), F(em.group(4))
    vol_ok = volume > e_thr if e_cmp == "above" else volume >= e_thr
    bonus = bonus_value if (acct == e_acct and vol_ok) else Fraction(0)

    total = residency + acct_pts + vol_pts + bonus

    low_max = grab(r"low_risk for a total at most {N}", text)
    high_min = grab(r"high_risk for a total of at least {N}", text)
    if total <= low_max:
        final = "low_risk"
    elif total >= high_min:
        final = "high_risk"
    else:
        final = "medium_risk"

    return {
        "final": final,
        "slots": {
            "volume_risk_points": vol_pts,
            "escalation_bonus": bonus,
            "total_risk_points": total,
        },
    }
