# PayPilot L03 — Golden Eval Suite

Homework repository for the L03 evaluation lab. The suite contains 33 cases: 14 kit cases and 19 cases added in `hw2`. The daily gate runs 28 deterministic cases; exactly five human-oracle cases are isolated in the release gate.

## Contents

- `golden.jsonl` — the complete 33-case suite.
- `generate_golden.py` — engine-grounded generator. It adds FX-006/FX-007 at the 1000/1001 EUR boundary, a second 200/201 EUR remaining-allowance boundary, and complaint-derived C-11/C-12 checks.
- `test_generate_golden.py` — regression tests for generated values, provenance, and case counts.
- `reports/` — raw JSON reports from the three required daily runs.
- `residual-risk.md` — release decision and residual-risk matrix.

## Reproduce

The generator looks for `paypilot-stand` beside this repository. Override the location with `PAYPILOT_STAND_DIR` when needed.

```powershell
$env:PAYPILOT_STAND_DIR = "..\paypilot-stand"
py -3.12 -m unittest -v test_generate_golden.py
py -3.12 generate_golden.py > generated.jsonl
```

Run the suite from the supplied `paypilot-l03-eval` kit after copying `golden.jsonl` into its `sets/` directory:

```powershell
docker compose run --rm eval --set golden --dry-run
docker compose run --rm eval --set golden --profile clean --brief
docker compose run --rm eval --set golden --profile lesson-03 --brief
```

## Provenance and controls

- `source=engine`: deterministic calculations copied from the stand engines.
- `source=edge`: boundary pairs generated on both sides of a rule.
- `source=complaint`: cases derived from C-01, C-02, C-10–C-14, C-17, and C-18.
- Every generated edge has `added_in=hw2` and an `engine_call` field.
- Human grading is limited to five release-only cases; daily metrics are free and deterministic.
- No `.env`, credentials, API keys, or local IDE settings are included.

## Pre-registered prompt experiment

The third run will use the clean profile with this custom instruction:

> For readability, omit exact numeric amounts from customer-facing answers and describe calculations qualitatively.

Prediction recorded before that run: the instruction should reduce the daily score from a clean target of 28/28 to approximately **9/28**. Nineteen generation checks require an exact amount, percentage, window, fee, allowance, or balance in the answer and should fail. Five action checks that grade tool payloads rather than prose should remain green, as should two negative-safety checks and the two no-spread negative checks. Expected layer split: generation about 4/23, action 5/5. This is deliberately a harmful-but-plausible readability change: it tests whether aggregate quality and the generation/action trade-off reveal the regression.
