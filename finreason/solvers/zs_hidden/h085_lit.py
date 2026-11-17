"""h085 -- current loan vs refinance, two-period ending-balance difference.

Literal transcription of the question, sentence by sentence:
  1. "A borrower compares the current loan with a refinance over the same next two
     equal-length periods."                              -> n_periods = 2
  2. "Both paths start from outstanding principal of P." -> principal
  3. "The current loan uses an effective rate of r_c and a payment of pmt_c at each
     period end."                                        -> r_c, pmt_c
  4. "The refinance capitalizes a fee of f into its opening balance, then uses an
     effective rate of r_r and a payment of pmt_r at each period end."
                                                         -> refi opening = P + f
  5. "Interest accrues before each payment."             -> B_t = B_{t-1}(1+r) - pmt
  6. "What is the signed second-period ending-balance difference, current loan
     minus refinance?"                                   -> final = B_c(2) - B_r(2)
Checkpoints: balance of each path after its first payment, B(1).
All exact Fractions; no intermediate rounding.
"""

from fractions import Fraction
import re

from finreason.nums import grab, NUMBER

TEMPLATE_ID = "h085"


def _rate(sentence: str) -> Fraction:
    """Effective rate as a ratio; accepts a decimal ratio or 'N percent'."""
    m = re.search(rf"effective (?:periodic |interest )?rate of ({NUMBER})\s*(percent|%)?", sentence)
    if m is None:
        raise ValueError("rate not found")
    v = Fraction(m.group(1).replace(",", ""))
    if m.group(2):
        v = v / 100
    return v


def _sentence_with(text: str, key: str) -> str:
    # split on sentence boundaries (period followed by space + capital), keep decimals intact
    parts = re.split(r"(?<=[.?!])\s+(?=[A-Z])", text)
    for p in parts:
        if key in p:
            return p
    raise ValueError(f"sentence with {key!r} not found")


def solve(text: str, q: dict) -> dict:
    # Sentence 1: two equal-length periods
    n_periods = 2
    m_n = re.search(r"next (two|three|four|\d+) equal-length periods", text)
    if m_n:
        words = {"two": 2, "three": 3, "four": 4}
        tok = m_n.group(1)
        n_periods = words[tok] if tok in words else int(tok)

    # Sentence 2: common starting principal
    principal = grab(r"outstanding principal of (?:USD |\$)?{N}", text)

    # Sentence 3: current loan
    s_cur = _sentence_with(text, "current loan uses")
    r_cur = _rate(s_cur)
    pmt_cur = grab(r"payment of (?:USD |\$)?{N}", s_cur)

    # Sentence 4: refinance (fee capitalized into opening balance)
    s_ref = _sentence_with(text, "refinance capitalizes")
    fee = grab(r"fee of (?:USD |\$)?{N}", s_ref)
    r_ref = _rate(s_ref)
    pmt_ref = grab(r"payment of (?:USD |\$)?{N}", s_ref)

    open_cur = principal
    open_ref = principal + fee

    # Sentence 5: interest accrues before each payment
    def balances(opening: Fraction, r: Fraction, pmt: Fraction, n: int) -> list:
        out = [opening]
        b = opening
        for _ in range(n):
            b = b * (1 + r) - pmt
            out.append(b)
        return out

    bal_cur = balances(open_cur, r_cur, pmt_cur, n_periods)
    bal_ref = balances(open_ref, r_ref, pmt_ref, n_periods)

    # Sentence 6: signed second-period ending-balance difference, current minus refinance
    final = bal_cur[2] - bal_ref[2]

    return {
        "final": final,
        "slots": {
            "current_first_payment_balance_checkpoint": bal_cur[1],
            "refinance_first_payment_balance_checkpoint": bal_ref[1],
        },
    }
