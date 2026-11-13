# Tree of Thoughts with DeepSeek: five-task reproduction

Adapted from [the official Tree of Thoughts repository](https://github.com/princeton-nlp/tree-of-thought-llm), commit `8050e67d0e3a0fddc424d7fa5801538722a4c4cc`. See [original README](README.upstream.md) and LICENSE.

## Scope and baseline

Five fixed Game of 24 test indices, 901–905 (zero-based). DeepSeek replaces the original GPT-4 backend; request model `deepseek-chat`, observed response model `deepseek-flash`. Intermediate states are evaluated with arithmetic reasoning followed by a label. Final-answer judging uses a label-only instruction. Beam width 5; 3 evaluations per candidate; temperature 0.7; maximum output tokens 1000. No replay was used in these five trials.

Changes include the provider adapter, output-format instructions, syntactic proposal filtering, and termination of failed single-number branches. These adaptations mean this is not an exact replication of the original model setup.

## Install

Tested on macOS ARM64 with Python 3.13. Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-deepseek.txt
cp .env.example .env
```

Edit `.env` locally to insert your DeepSeek API key. Never commit it. The experiment runner also queries the provider balance endpoint for a CNY spending guard.

## Run

```bash
python -u run_baseline.py
```

The included `results/baseline` contains the completed experiment. To run a NEW paid experiment, first move that folder to a different name; the runner refuses to overwrite an existing manifest. It runs five tasks sequentially, records per-call API logs and per-task JSON, and saves `summary.json`. Each task has a 600-call/500k-token guard. A balance check every roughly ten calls stops the batch near a CNY 10 account-balance decrease (not an exact billing ledger). CTRL+C stops the process. Calls cost money.

## Observed results

| Index | Numbers | Solved | Seconds | Calls |
|---|---|---|---|---|
|901|1 2 4 7|Yes|246.7|180|
|902|2 5 8 11|Yes|611.0|294|
|903|3 4 4 13|Yes|284.9|202|
|904|6 7 8 9|Yes|568.7|275|
|905|1 11 11 13|Yes|254.0|181|

Solved means at least one retained final expression passes the authors' `Game24Task.test_output` checker. It does not mean all candidates are correct. This is 5/5 on five selected tasks, one trial each, not an estimate of the original 100-task benchmark score or stochastic variance. Total wall time approximately 32.8 minutes.

## Reproducibility records

`results/baseline/result-*.json` includes complete search candidates, scores and selected paths. `summary.json` contains timings and token counts. `manifest.json` fixes indices/configuration and original source hashes; account balances are omitted from the public copy. `executed-code/` preserves the exact model and search source used in the run. Current runnable files have path/config changes for a standalone checkout; the prompt and search settings remain the same. Large per-call logs remain local.

## Label-only ablation

Run `python -u run_baseline.py --condition label_only` for the same five indices with the intermediate-state evaluator restricted to a bare label. Results go to `results/label_only`; baseline results are preserved. All other model, search, judging and budget settings are shared. This removes explicit output reasoning, not necessarily unobserved internal reasoning. Each condition has one fresh run per task; sampling variation remains a confound.
