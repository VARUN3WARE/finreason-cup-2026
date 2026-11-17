from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.transaction_analysis.multi_factor_transaction.advanced.v1"


def solve(text: str, q: dict) -> dict:
    total = grab(r"transfer of\s+{N}\s*USD", text)
    share1 = grab(r"sends\s+{N}\s*percent to Network 1", text) / 100
    fee1 = grab(r"Network 1 deducts\s+{N}\s*percent", text) / 100
    fixed2 = grab(r"Network 2 first deducts\s+{N}\s*USD", text)
    bonus2 = grab(r"applies an?\s+{N}\s*percent bonus", text) / 100
    part1 = total * share1
    part2 = total - part1  # remainder goes to Network 2
    net1 = part1 * (1 - fee1)
    after_fixed2 = part2 - fixed2
    net2 = after_fixed2 * (1 + bonus2)
    return {
        "final": net1 + net2,
        "slots": {
            "network_one_net_trace": net1,
            "network_two_after_fixed_trace": after_fixed2,
            "network_two_net_trace": net2,
        },
    }
