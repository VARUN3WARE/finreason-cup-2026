"""h062 -- FX round trip with entry/exit fee retention and a financing charge:
solve for the exit-quote threshold hitting a target net return (literal transcription)."""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h062"


def solve(text: str, q: dict) -> dict:
    # "Start with reporting-currency capital" -- normalise capital to 1 (result is scale-free).
    capital = Fraction(1)

    # "convert it into base currency at normalized entry quote E, expressed as
    #  reporting-currency units per base-currency unit"
    entry_quote = grab(r"normalized entry quote\s+{N}", text)
    base_before_fee = capital / entry_quote

    # "The entry conversion retains one minus fee ratio f1."
    entry_fee = grab(r"entry conversion retains one minus fee ratio\s+{N}", text)
    base_retained = base_before_fee * (1 - entry_fee)

    # "At exit, convert all retained base currency back ... at the normalized exit quote X
    #  ... and retain one minus fee ratio f2."
    exit_fee = grab(r"At exit,.*?retain one minus fee ratio\s+{N}", text)

    # "Then deduct a financing charge equal to c times the initial reporting-currency capital."
    carry = grab(r"financing charge equal to\s+{N}\s+times", text)
    financing_charge = carry * capital

    # "Determine the exact exit-quote threshold at which the net return equals R."
    target_return = grab(r"net return equals\s+{N}", text)

    # Net value = base_retained * X * (1 - f2) - financing_charge
    # Net return = net value / capital - 1 = R
    # => base_retained * X * (1 - f2) = capital * (1 + R) + financing_charge
    required_gross_value = capital * (1 + target_return) + financing_charge
    gross_growth = required_gross_value / capital  # return-and-carry gross growth multiple: 1 + R + c

    exit_quote = required_gross_value / (base_retained * (1 - exit_fee))

    # sanity check: plugging the threshold back reproduces the target net return
    net_value = base_retained * exit_quote * (1 - exit_fee) - financing_charge
    assert net_value / capital - 1 == target_return

    return {"final": exit_quote, "slots": {"gross_growth_checkpoint": gross_growth}}
