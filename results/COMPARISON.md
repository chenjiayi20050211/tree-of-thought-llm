# Baseline versus label-only evaluation

Five prespecified tasks (indices 901–905), one fresh trial per task per condition. Task 900 was used for debugging and is excluded. No API response replay in either formal condition.

| Index | Numbers | Baseline solved | Label-only solved | Baseline seconds | Label-only seconds | Baseline tokens | Label-only tokens |
|---|---|---|---|---|---|---|---|
| 901 | 1 2 4 7 | True | False | 246.7 | 184.8 | 89239 | 64642 |
| 902 | 2 5 8 11 | True | False | 611.0 | 290.3 | 200157 | 94459 |
| 903 | 3 4 4 13 | True | False | 284.9 | 263.6 | 103236 | 92211 |
| 904 | 6 7 8 9 | True | False | 568.7 | 243.2 | 180605 | 82654 |
| 905 | 1 11 11 13 | True | False | 254.0 | 259.3 | 91171 | 83737 |

Baseline: 5/5 solved; 1965.36 seconds; 1132 API calls; 664408 tokens.
Label-only: 0/5 solved; 1241.19 seconds; 1072 API calls; 417703 tokens.

Label-only used 37.1% fewer tokens and 36.8% less wall time, but produced no accepted solution on these five tasks. All trials completed; failures are not interrupted runs. Token use is not monetary cost.

Only the system instruction for intermediate-state evaluation changes: arithmetic reasoning followed by a final label versus a bare label. The user prompt examples, model request, temperature, token limit, candidate generation, beam width 5, three evaluation samples, output filtering, and final-answer judge are shared. The baseline final-answer judge is label-only in both conditions.

Success is any retained final answer passing the authors' Game24Task.test_output checker. This does not certify every intermediate step or imply all candidates were correct. The checker was rerun on all ten saved trials.

Limitations: small fixed sample; one trial per condition; sequential collection; stochastic model calls; latency subject to service/network variation. This is a DeepSeek-adapted reproduction of the workflow, not a replication of the original GPT-4 benchmark score. No general causal effect size or variance is established.

Source code for the ablation is commit a5c8ffe. Per-task search traces and usage are in result JSON files; large per-call logs remain local. Manifest account balances are removed from published records.
