# v0.2 test results

Structured results only. No model message text is published, because run outputs can contain account details; the v0.1 policy is unchanged.

| File | What |
|---|---|
| `canary.txt` | Output of `skills/counsel/canary.py`: 4 agents × 5 probes, verdict from transcript tool calls. **CANARY PASS, 20/20, USD 0.241** |
| `simulation.json` | Every run of the final rules simulation (case, rep, valid, invalid reason, verdict, cost) plus a summary of rounds 1–2. **34/34 valid runs pass, 0 P0** |

Scenarios: `tests/scenarios.json` · Pass criteria (pre-registered): `tests/rubric.md` · Narrative, deviations and costs: [TESTING.md](../../TESTING.md)

Reproduce:

```bash
python3 skills/counsel/canary.py                 # ~USD 0.25
python3 tests/build-agents.py
python3 tests/rules-sim-run.py 3 2.00            # 11 cases × 3, cap USD 2.00
python3 tests/test_quotecheck.py
```
