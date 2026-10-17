# Validation

Acceptance: Reproduce increment arithmetic, fractional milliseconds, per-side missing-clock resynchronization, ignored variations, and reject duplicate/leading clocks, malformed controls, wrong move numbers and result conflicts.

The behavior suite has 20 test methods, including malformed-input contracts. CI runs unit tests, compilation, wheel build and new-environment installed-command checks on Linux/Python 3.10, 3.12 and 3.14. A configured workflow does not prove success; inspect current Actions results. Preparation receipts are recorded in PREPARATION.json after execution. All possible inputs, production workloads and Windows/macOS are not certified. No performance benchmark was conducted.
