"""h080 -- two-program savings attribution (Shapley-style, equal weight on both orders).

Literal transcription of the question text, sentence by sentence.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h080"


def solve(text: str, q: dict) -> dict:
    # S1: "a procurement program alone would deliver {N} USD millions of savings,
    #      an IT program alone would deliver {N} USD millions, and implementing both
    #      would deliver {N} USD millions."
    procurement_only = grab(r"procurement program alone would deliver {N} USD million", text)
    it_only = grab(r"IT program alone would deliver {N} USD million", text)
    combined = grab(r"implementing both would deliver {N} USD million", text)

    # S2: "No program delivers zero savings." (consistency statement; nothing to compute)
    # S3: overlap statement: max(P, I) < C < P + I (descriptive; not used as a branch)

    # S4: "Attribute procurement savings by giving equal weight to its marginal
    #      contribution in both possible implementation orders:"
    #   - "its procurement-only savings when introduced first"
    marginal_first = procurement_only
    #   - "combined-program savings minus IT-only savings when introduced after IT"
    marginal_after_it = combined - it_only
    #   equal weight -> simple average of the two orders
    procurement_attributed = (marginal_first + marginal_after_it) / 2

    # S5: "What percentage of combined-program savings is attributed to procurement?"
    pct_of_combined = procurement_attributed / combined * 100

    return {
        "final": Fraction(pct_of_combined),
        "slots": {
            "procurement_marginal_after_it_checkpoint": Fraction(marginal_after_it),
        },
    }
