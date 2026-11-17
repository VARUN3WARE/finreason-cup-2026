"""h017: joint vs alternative stress scenario capital adequacy check.

joint rate  = m_shock*m_sens + c_shock*c_sens + k * m_shock * c_shock
alt rate    = mult * shock**2
loss_i      = portfolio_value * rate_i
remaining   = available_capital - max(joint_loss, alt_loss)
capital_pass iff remaining >= minimum ("meets the minimum").
"""
from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "h017"


def solve(text: str, q: dict) -> dict:
    value = grab(r"portfolio worth {N}", text)
    capital = grab(r"available capital {N}", text)
    minimum = grab(r"retain at least {N}", text)
    m_shock, m_sens = grab_all(r"market shock ratio {N} with sensitivity {N}", text)
    c_shock, c_sens = grab_all(r"credit shock ratio {N} with sensitivity {N}", text)
    k = grab(r"their product times {N}", text)
    alt_shock = grab(r"alternative scenario, shock ratio {N}", text)
    alt_mult = grab(r"squared and multiplied by {N}", text)

    joint_rate = m_shock * m_sens + c_shock * c_sens + k * m_shock * c_shock
    alt_rate = alt_mult * alt_shock ** 2

    joint_loss = value * joint_rate
    alt_loss = value * alt_rate
    loss = max(joint_loss, alt_loss)
    remaining = capital - loss

    final = "capital_pass" if remaining >= minimum else "capital_fail"
    return {"final": final, "slots": {"joint_rate_checkpoint": Fraction(joint_rate)}}
