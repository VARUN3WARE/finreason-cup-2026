"""h050 -- two-plan transfer pricing comparison (literal transcription).

Sentence by sentence:
1. "A customer expects monthly transfer volume V and N transfers per month for M months."
2. "Plan A charges proportional transfer rate rA, fee fA per transfer, monthly subscription sA,
    and one-time setup fee uA."
3. "Plan B charges rB, fB, sB, and one-time setup fee uB."   (same order as Plan A)
4. "Each setup fee is charged exactly once at account opening, not once per month or transfer."
5. "Plan A savings relative to Plan B, defined as Plan B total cost minus Plan A total cost."
6. Report the signed savings (no flooring at zero).

Checkpoints: horizon volume = V * M (USD); horizon count = N * M (transfers).
"""

from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "h050"


def solve(text: str, q: dict) -> dict:
    # Sentence 1
    monthly_volume = grab(r"monthly transfer volume {N}", text)
    transfers_per_month = grab(r"{N} transfers per month", text)
    months = grab(r"transfers per month for {N} months?", text)

    # Sentence 2 -- Plan A
    rate_a, fee_a, sub_a, setup_a = grab_all(
        r"Plan A charges proportional transfer rate {N},\s*fee {N} per transfer,\s*"
        r"monthly subscription {N},\s*and one-time setup fee {N}",
        text,
    )

    # Sentence 3 -- Plan B (same order: rate, per-transfer fee, monthly subscription, setup)
    rate_b, fee_b, sub_b, setup_b = grab_all(
        r"Plan B charges {N},\s*{N},\s*{N},\s*and one-time setup fee {N}",
        text,
    )

    # Horizon quantities
    horizon_volume = monthly_volume * months
    horizon_count = transfers_per_month * months

    # Sentence 4 -- setup fee charged exactly once
    def total_cost(rate: Fraction, fee: Fraction, sub: Fraction, setup: Fraction) -> Fraction:
        proportional = rate * horizon_volume
        per_transfer = fee * horizon_count
        subscription = sub * months
        return proportional + per_transfer + subscription + setup

    total_a = total_cost(rate_a, fee_a, sub_a, setup_a)
    total_b = total_cost(rate_b, fee_b, sub_b, setup_b)

    # Sentence 5 -- savings = Plan B total cost minus Plan A total cost (signed)
    savings = total_b - total_a

    return {
        "final": savings,
        "slots": {
            "horizon_volume_checkpoint": horizon_volume,
            "horizon_count_checkpoint": horizon_count,
        },
    }
