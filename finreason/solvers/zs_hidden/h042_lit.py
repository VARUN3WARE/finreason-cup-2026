"""h042 -- primary processor + one backup retry; expected net merchant proceeds.

Literal transcription of the question, sentence by sentence.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h042"


def solve(text: str, q: dict) -> dict:
    # "A merchant has {N} original payment attempts, each for {A}."
    n_attempts = grab(r"merchant has {N} original payment attempts", text)
    amount = grab(r"original payment attempts, each for {N}", text)

    # "The primary processor succeeds with probability {p1}."
    p_primary = grab(r"primary processor succeeds with probability {N}", text)

    # "Every primary failure triggers exactly one backup retry, whose conditional success probability is {p2}."
    p_backup = grab(r"backup retry, whose conditional success probability is {N}", text)

    # "An order produces one settlement of the stated amount if either attempt succeeds and
    #  produces no revenue if both fail; no order is retried more than once."
    primary_failures = n_attempts * (1 - p_primary)          # expected number of primary failures
    retries = primary_failures                                # each primary failure -> exactly one retry
    retry_successes = retries * p_backup                      # settle through backup
    terminal_failures = retries * (1 - p_backup)              # both attempts fail
    primary_successes = n_attempts * p_primary
    settled_orders = primary_successes + retry_successes
    settled_revenue = settled_orders * amount

    # "The primary charges {r1} of the stated amount plus fixed fee {f1} on every original attempt,
    #  whether successful or failed."
    r1, f1 = (
        grab(r"primary charges {N} of the stated amount", text),
        grab(r"primary charges {N} of the stated amount plus fixed fee {N}", text, group=2),
    )
    primary_fees = n_attempts * (r1 * amount + f1)

    # "The backup charges {r2} of the stated amount plus fixed fee {f2} on every retry,
    #  whether successful or failed."
    r2, f2 = (
        grab(r"backup charges {N} of the stated amount", text),
        grab(r"backup charges {N} of the stated amount plus fixed fee {N}", text, group=2),
    )
    backup_fees = retries * (r2 * amount + f2)

    # "The merchant also incurs {h1} for every primary failure and an additional {h2} for every
    #  order where both attempts fail, and pays {S} once for the batch."
    h_primary_fail = grab(r"merchant also incurs {N} for every primary failure", text)
    h_terminal = grab(r"an additional {N} for every order where both attempts fail", text)
    batch_fee = grab(r"pays {N} once for the batch", text)

    primary_failure_handling = primary_failures * h_primary_fail
    terminal_failure_cost = terminal_failures * h_terminal

    # "Compute expected settled revenue and deduct all processing, handling, and subscription costs."
    net = (
        settled_revenue
        - primary_fees
        - backup_fees
        - primary_failure_handling
        - terminal_failure_cost
        - batch_fee
    )

    # Checkpoint 1: fraction of ORIGINAL attempts expected to settle through the backup retry.
    retry_success_fraction = retry_successes / n_attempts

    return {
        "final": Fraction(net),
        "slots": {
            "retry_success_fraction_checkpoint": Fraction(retry_success_fraction),
            "backup_processing_fees_checkpoint": Fraction(backup_fees),
            "terminal_failure_cost_checkpoint": Fraction(terminal_failure_cost),
        },
    }
