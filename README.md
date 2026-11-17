# HumanSlop at FinReason Cup 2026 (Tasks 1 and 3)

Code, prompts, generated solvers and analysis scripts for our IEEE BigData 2026 Cup paper:

> Varun Rao and Galaba Vamsi. *HumanSlop at FinReason Cup 2026 Tasks 1 and 3: Verified Program Synthesis for Exact
> Financial Reasoning and Executable Rule Semantics for XBRL Audit Verification.* IEEE BigData 2026, FinReason Cup.

Paper: [`paper/HumanSlop_FinReason2026_CameraReady.pdf`](paper/HumanSlop_FinReason2026_CameraReady.pdf).
Competition: <https://the-finai.github.io/IEEE-bigdata-cup/>.

## Results

| Task | Official test result | Development |
| --- | --- | --- |
| 1. Verifiable Financial Chain Reasoning | 11th of 27. 923 of 928 final answers; Combined FAC 0.995466, Hidden FAC 0.998016, Combined checkpoint 0.992614 | 1.000 final answers, 1.000 reasoning steps |
| 3. Financial Audit Verification (XBRL) | 11th of 23. ACC 96.03% (EER 1.91%, CER 2.06%) | ACC 98.38% (organizer baseline 33.09%) |

## What is here

| Path | What |
| --- | --- |
| `finreason/` | Task 1 package (Python 3.10 standard library plus the official toolkit's `finreason_task1`) |
| `finreason/data.py` | Loading, structural signatures, routing of each question to a seen template or a hidden cluster |
| `finreason/fmt.py`, `nums.py` | Exact rendering (finite decimal, irreducible `p/q`, half-up) and exact number parsing |
| `finreason/solvers/seen/` | 290 solvers, each admitted only after reproducing all 11 labeled instances of its template |
| `finreason/solvers/zs_proxy/` | 290 gold-blind solvers for the same templates (ablation and N-version cross-check) |
| `finreason/solvers/zs_hidden/` | 116 hidden clusters: lens solvers `<cid>_{lit,dom,skep,hand}.py`, adjudications `_adjA/_adjB/_final`, reviews `_rev*`/`_red`, jurors `_jury1..6` |
| `finreason/hidden.py`, `crosscheck.py`, `stage.py` | Field-level comparison, decisions, no-execution cross-checks, stage status |
| `finreason/metamorphic.py`, `ablation.py`, `ties.py`, `paper_stats.py` | Diagnostics and every number in the paper |
| `finreason/predict.py` | Builds, validates and packages predictions (`--strict` refuses fallback rows) |
| `workflows/01..09_*.js` | The multi-agent workflow scripts with their full prompts |
| `task3/` | Task 3 solver: XBRL parsing, DQC_0015 / DQC_0117 / DQC_0126 re-implemented from the official XULE source, scope-based routing |
| `work/` | Routing caches, decisions, cross-check reports, predictions, portal receipts, token cost log |
| `paper/` | LaTeX source, the camera-ready PDF and the submitted version |

Models used by the agents: Claude Opus 5.5, Sonnet 5.5 and Fable 5.1 (`claude-opus-5-5`, `claude-sonnet-5-5`,
`claude-fable-5-1`). The solvers they wrote are in this repository, so reproducing our submissions needs no model
access. Regenerating the solvers would not give byte-identical code.

## Setup

```bash
# Python 3.10 or newer. Our code uses only the standard library.
git clone https://github.com/The-FinAI/IEEE-bigdata-cup toolkit   # official toolkit and Task 1 data
```

Task 3 inputs are not stored here (about 90 MB each). Download the `development` and `test` splits of
[`YanAdjeNole/FinReason-Task3`](https://huggingface.co/datasets/YanAdjeNole/FinReason-Task3) to
`work/task3/development_inputs.jsonl` and `work/task3/test_inputs.jsonl`.

## Reproduce

Task 1:

```bash
python3 -m finreason.check all                          # library: 290/290 templates, 3190/3190 labeled instances
python3 -m finreason.eval_zs                            # gold-blind solvers scored against gold
python3 -m finreason.hidden finalize                    # decisions -> work/hidden_selection.json (348 hidden rows)
python3 -m finreason.predict test --strict --package    # -> work/pred_test.zip, identical to the submitted file
python3 -m finreason.crosscheck --cot work/hidden_cot.json   # no-execution agreement (also _fable, _sonnet)
python3 -m finreason.metamorphic                        # perturbation diagnostic
python3 -m finreason.ablation                           # stage-wise ablation, lens agreement, one-instance analysis
```

Task 3:

```bash
cd task3
python3 solve.py ../work/task3/test_inputs.jsonl ../work/task3/pred_test_v7.jsonl
python3 solve.py ../work/task3/development_inputs.jsonl ../work/task3/pred_development_v7.jsonl
# Upload format: one JSON object per line with "id", "extracted_value", "calculated_value".
```

Paper: compile `paper/main.tex` with `pdflatex`, `bibtex`, `pdflatex`, `pdflatex` (IEEEtran class).

## Integrity

Test answers come only from the automated pipeline. No human or agent labeled or edited a test answer, no step uses
case identifiers, the organizers' DQC message files or any external source of DQC findings, and development uploads
were used only to test general rules. Agent blindness rested on instructions and, for the gold-blind agents, a
transcript audit, not on filesystem sandboxing. See the paper's Limitations section.

## Data and third-party material

Competition data belongs to the FinReason Cup organizers and is distributed under their terms. The DQC rule logic in
`task3/` follows the XBRL US Data Quality Committee rules
(<https://github.com/DataQualityCommittee/dqc_us_rules>). The official DQC_0015 element-list and member-exclusion
spreadsheets are not redistributed here; `task3/resources/dqc_0015.json` is the list derived from them that the solver
reads.

## License

Our code is released under the MIT License (see `LICENSE`). It does not cover the competition data or XBRL US material.

## Citation

```bibtex
@inproceedings{rao2026humanslop,
  author    = {Rao, Varun and Vamsi, Galaba},
  title     = {{HumanSlop} at {FinReason Cup 2026} Tasks 1 and 3: Verified Program Synthesis for Exact Financial
               Reasoning and Executable Rule Semantics for {XBRL} Audit Verification},
  booktitle = {2026 IEEE International Conference on Big Data (BigData)},
  year      = {2026},
  address   = {Phoenix, Arizona, USA}
}
```
