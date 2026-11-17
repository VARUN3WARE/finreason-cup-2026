"""Customer risk rating: residency + account + volume points + offshore escalation bonus."""
import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "fp.finance_regulation.kyc.customer_risk_rating.advanced.v1"


def _account_points(text: str) -> dict:
    m = re.search(r"Account points are (.*?)\.\s", text)
    seg = m.group(1) if m else ""
    pts = {k: F(v) for k, v in re.findall(r"([a-z_]+)=(" + NUMBER + r")", seg)}
    if not pts:
        pts = {"savings": Fraction(1), "business": Fraction(3), "offshore": Fraction(4)}
    return pts


def _volume_points(vol: Fraction, text: str) -> Fraction:
    # Bands as stated: 1 for <= 10000; 2 for >10000 and <=25000; 3 for >25000 and <=50000; 4 for >50000.
    try:
        p1, b1 = (grab(r"Volume points are {N} for volume at most USD {N}", text, g) for g in (1, 2))
        p2 = grab(r"{N} for volume above USD [\d,]+ and at most USD {N}", text, 1)
        b2 = grab(r"{N} for volume above USD [\d,]+ and at most USD {N}", text, 2)
        m = re.findall(r"(" + NUMBER + r") for volume above USD (" + NUMBER + r") and at most USD (" + NUMBER + r")", text)
        p3, b3 = F(m[1][0]), F(m[1][2])
        m4 = re.search(r"and (" + NUMBER + r") for volume above USD (" + NUMBER + r")\.", text)
        p4 = F(m4.group(1))
    except (ValueError, IndexError, AttributeError):
        p1, b1, p2, b2, p3, b3, p4 = map(Fraction, (1, 10000, 2, 25000, 3, 50000, 4))
    if vol <= b1:
        return p1
    if vol <= b2:
        return p2
    if vol <= b3:
        return p3
    return p4


def solve(text: str, q: dict) -> dict:
    residency = grab(r"residency risk points are {N}", text)
    acct = re.search(r"The account type is ([a-z_]+)", text).group(1)
    vol = grab(r"transaction volume in whole USD is {N}", text)

    acct_pts = _account_points(text)[acct]
    vol_pts = _volume_points(vol, text)

    try:
        esc_threshold = grab(r"account type is offshore and volume is above USD {N}", text)
    except ValueError:
        esc_threshold = Fraction(25000)
    try:
        esc_amount = Fraction({"one": 1, "two": 2, "three": 3}[
            re.search(r"Add a (\w+)-point escalation bonus", text).group(1)])
    except (AttributeError, KeyError):
        esc_amount = Fraction(1)
    bonus = esc_amount if (acct == "offshore" and vol > esc_threshold) else Fraction(0)

    total = residency + acct_pts + vol_pts + bonus

    try:
        low_max = grab(r"low_risk for a total at most {N}", text)
    except ValueError:
        low_max = Fraction(5)
    try:
        high_min = grab(r"high_risk for a total of at least {N}", text)
    except ValueError:
        high_min = Fraction(9)
    if total >= high_min:
        final = "high_risk"
    elif total <= low_max:
        final = "low_risk"
    else:
        final = "medium_risk"

    return {
        "final": final,
        "slots": {"volume_risk_points": vol_pts, "escalation_bonus": bonus, "total_risk_points": total},
    }
