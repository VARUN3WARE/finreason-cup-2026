"""h088 -- merchant batch net settlement (literal transcription).

Sentence by sentence:
1. "gross sales before chargebacks of G across N transactions"
2. "The processor charges rate r on those gross sales plus f per transaction."
   -> variable fee = r * G ; fixed fees = f * N
3. "Chargebacks included in the gross-sales amount total C, of which fraction p is recovered."
   -> unrecovered chargeback loss = C * (1 - p)
4. "The processor also withholds reserve R."
5. net settlement = G - variable fee - fixed fees - unrecovered chargebacks - reserve
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h088"


def solve(text: str, q: dict) -> dict:
    # Sentence 1
    gross = grab(r"gross sales before chargebacks of {N}", text)
    n_tx = grab(r"across {N} transactions", text)
    # Sentence 2
    rate = grab(r"charges rate {N} on those gross sales", text)
    per_tx = grab(r"plus {N} per transaction", text)
    variable_fee = rate * gross
    fixed_fees = per_tx * n_tx
    # Sentence 3
    chargebacks = grab(r"Chargebacks included in the gross-sales amount total {N}", text)
    recovered_frac = grab(r"of which fraction {N} is recovered", text)
    unrecovered = chargebacks * (1 - recovered_frac)
    # Sentence 4
    reserve = grab(r"withholds reserve {N}", text)
    # Sentence 5
    net = gross - variable_fee - fixed_fees - unrecovered - reserve
    return {
        "final": Fraction(net),
        "slots": {
            "variable_fee_checkpoint": Fraction(variable_fee),
            "fixed_fee_checkpoint": Fraction(fixed_fees),
            "chargeback_loss_checkpoint": Fraction(unrecovered),
        },
    }
