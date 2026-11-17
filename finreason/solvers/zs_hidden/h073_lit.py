"""h073 -- breakeven quoted purchase price for a target simple total return (literal transcription).

Sentence by sentence:
  * gross terminal sale proceeds G, holding-period dividend cash D (per share)
  * selling incurs exit cost X; buying incurs entry cost E on top of the quote Q
  * complete acquisition outlay A = Q + E
  * total return = (net terminal receipts - A) / A
    net terminal receipts N = G - X + D  (dividend cash is the only other receipt; ignoring
    reinvestment/discounting, it is received alongside the after-exit-cost sale proceeds)
  * target ratio t (0.20 = 20%): solve (N - A)/A = t  ->  A = N/(1+t)  ->  Q = N/(1+t) - E
  * carry exactly; framework rounds half up to cents.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h073"


def solve(text: str, q: dict) -> dict:
    # "An investor expects gross terminal sale proceeds G and holding-period dividend cash D."
    gross_proceeds = grab(r"gross terminal sale proceeds {N}", text)
    dividend_cash = grab(r"holding-period dividend cash {N}", text)
    # "Selling incurs exit cost X, while buying incurs entry cost E in addition to the quoted purchase price."
    exit_cost = grab(r"exit cost {N}", text)
    entry_cost = grab(r"entry cost {N}", text)
    # "For target ratio t, where 0.20 means 20%"
    target = grab(r"target ratio {N}", text)

    # Net terminal receipts: sale proceeds after exit cost plus the holding-period dividend cash.
    net_receipts = gross_proceeds - exit_cost + dividend_cash

    # (net_receipts - outlay) / outlay = target  =>  outlay = net_receipts / (1 + target)
    if 1 + target == 0:
        raise ValueError("target ratio of -1 has no binding price")
    outlay = net_receipts / (1 + target)
    # Complete acquisition outlay is the quote plus entry cost.
    quote = outlay - entry_cost

    return {"final": Fraction(quote), "slots": {"net_receipts_checkpoint": Fraction(net_receipts)}}
