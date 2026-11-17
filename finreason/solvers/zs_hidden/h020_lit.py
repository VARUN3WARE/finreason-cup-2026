"""h020 -- fictional enforcement remedy: cooperation credit that exhausts the remedy cap.

Literal transcription of the question, sentence by sentence.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h020"


def solve(text: str, q: dict) -> dict:
    # "The maximum total remedy is X USD, of which Y USD is fixed interest."
    max_total_remedy = grab(r"maximum total remedy is {N} USD", text)
    fixed_interest = grab(r"of which {N} USD is fixed interest", text)

    # "A gain-based penalty equals realized gain G USD multiplied by M,
    #  while the alternative statutory floor is S USD."
    realized_gain = grab(r"realized gain {N} USD", text)
    multiplier = grab(r"realized gain [^ ]+ USD multiplied by {N}", text)
    gain_based_penalty = realized_gain * multiplier
    statutory_floor = grab(r"alternative statutory floor is {N} USD", text)

    # "The pre-credit penalty base is the greater of those two amounts."
    pre_credit_base = max(gain_based_penalty, statutory_floor)

    # "A cooperation credit ratio c reduces that base to (1 - c) times the pre-credit amount."
    # credited_penalty(c) = (1 - c) * pre_credit_base

    # "What cooperation credit percentage makes the credited penalty plus fixed interest
    #  equal the maximum total remedy?"
    #   (1 - c) * base + fixed_interest = max_total_remedy
    # Cap amount available for penalty = max total remedy - fixed interest.
    penalty_cap = max_total_remedy - fixed_interest
    c = Fraction(1) - penalty_cap / pre_credit_base
    credit_pct = c * 100

    return {
        "final": credit_pct,
        "slots": {"penalty_cap_checkpoint": penalty_cap},
    }
