"""h029 -- rolling whale threshold: required next transfer (literal transcription)."""

from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "h029"


def solve(text: str, q: dict) -> dict:
    # "A wallet has two prior transfers of {A} USD and {B} USD in the current monitoring window."
    prior_1, prior_2 = grab_all(r"two prior transfers of {N} USD and {N} USD", text)
    prior_total = prior_1 + prior_2

    # "Its base rolling whale threshold is {T} USD"
    base_threshold = grab(r"base rolling whale threshold is {N} USD", text)

    # "... and is increased by risk-adjustment ratio {r}."
    ratio = grab(r"increased by risk-adjustment ratio {N}", text)
    adjustment_factor = Fraction(1) + ratio  # multiplicative factor applied to the base
    adjusted_threshold = base_threshold * adjustment_factor

    # "What next transfer amount would make the rolling total exceed the adjusted
    #  threshold by exactly {E} USD?"
    excess = grab(r"exceed the adjusted threshold by exactly {N} USD", text)
    target_rolling_total = adjusted_threshold + excess
    required_transfer = target_rolling_total - prior_total

    return {
        "final": required_transfer,
        "slots": {"threshold_adjustment_factor_checkpoint": adjustment_factor},
    }
