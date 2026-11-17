"""h054 -- quick-ratio convexity premium of an inventory sale under two recovery states.

Literal transcription of the question text, sentence by sentence.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h054"


def solve(text: str, q: dict) -> dict:
    # "Quick assets before the sale, excluding inventory, are X USD"
    qa_pre = grab(r"Quick assets before the sale, excluding inventory, are {N} USD", text)
    # "inventory carrying amount X USD is sold"
    inv = grab(r"inventory carrying amount {N} USD is sold", text)
    # "fraction f of net proceeds remains as cash in quick assets and the complementary
    #  fraction immediately repays current liabilities at par"
    f_cash = grab(r"fraction {N} of net proceeds remains as cash", text)
    f_repay = 1 - f_cash
    # "The low recovery rate is rL and the high rate is that low rate plus positive spread s"
    r_low = grab(r"low recovery rate is {N}", text)
    spread = grab(r"plus positive spread {N}", text)
    r_high = r_low + spread
    # "The high state occurs with probability p"
    p_high = grab(r"high state occurs with probability {N}", text)
    p_low = 1 - p_high
    # "the scenario gives X USD, the liabilities remaining after high-state repayment;
    #  the same implied pre-sale liabilities apply in both states"
    liab_after_high = grab(r"the scenario gives {N} USD, the liabilities remaining after high-state repayment", text)

    # Net proceeds per state = recovery rate x carrying amount sold
    proceeds_low = r_low * inv
    proceeds_high = r_high * inv

    retained_low = f_cash * proceeds_low
    retained_high = f_cash * proceeds_high
    repay_low = f_repay * proceeds_low
    repay_high = f_repay * proceeds_high

    # Implied pre-sale liabilities (same in both states)
    liab_pre = liab_after_high + repay_high

    # Post-sale quick assets and liabilities per state
    qa_low = qa_pre + retained_low
    qa_high = qa_pre + retained_high
    liab_low = liab_pre - repay_low
    liab_high = liab_pre - repay_high  # == liab_after_high

    # "Compute each state's post-sale quick ratio."
    qr_low = qa_low / liab_low
    qr_high = qa_high / liab_high

    # "subtract the quick ratio formed from probability-weighted post-sale quick assets and
    #  liabilities from the probability-weighted average of the two state quick ratios"
    avg_qr = p_low * qr_low + p_high * qr_high
    exp_qa = p_low * qa_low + p_high * qa_high
    exp_liab = p_low * liab_low + p_high * liab_high
    qr_of_expectations = exp_qa / exp_liab
    gap = avg_qr - qr_of_expectations

    # "Report its percentage-point equivalent"
    final = gap * 100

    return {
        "final": final,
        "slots": {
            "low_state_retained_cash_checkpoint": retained_low,
            "incremental_retained_cash_checkpoint": retained_high - retained_low,
            "incremental_repayment_checkpoint": repay_high - repay_low,
        },
    }
