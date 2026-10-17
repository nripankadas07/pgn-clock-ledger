# pgn-clock-ledger

Reconstruct per-ply clock differences from a bounded annotated PGN mainline without hiding missing evidence.

For: Chess study authors auditing recorded clock annotations in a short standard-start game. Missing annotations or an unexplained clock increase should not silently become zero thinking time.

## Quickstart

Python 3.10 or newer; no runtime packages or network access. The wheel build needs setuptools from the normal Python package registry.

```sh
git clone https://github.com/nripankadas07/pgn-clock-ledger.git
cd pgn-clock-ledger
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/pgn-clock-ledger example.pgn
```

Exit 0 with elapsed milliseconds [3000,2000,3000,5000]; known totals are white 6000 and black 7000 under the stated increment convention.

Windows equivalents use `.venv\Scripts\python.exe` and `.venv\Scripts\pgn-clock-ledger.exe`; Windows/macOS are not executed by this release’s Linux CI.

## Contract

One UTF-8 PGN, mandatory simple integer TimeControl base+increment, standard initial position and alternating SAN-like mainline labels. Brace [%clk H:MM:SS[.fff]] annotations are exact milliseconds. Assumption: each annotation is after its move and that move’s increment, including the first captured move. elapsed = previous same-side clock + increment - current clock. Missing evidence invalidates the next same-side difference until a new baseline is captured. An increase exceeding increment is a finding with no elapsed value. Balanced variations, semicolon comments and NAGs do not contribute clock evidence; header/body result agreement is enforced.

JSON goes to stdout. Exit 0 means a valid report without findings; exit 1 means a valid report with the documented findings; exit 2 means invalid input or an I/O failure, with an error on stderr and no partial report. `--help` describes options. Review outputs before sharing them; they may contain input identifiers.

## Limits

128 KiB, 64 headers, 10,000 plies, variation depth 32, token length 64; base 1–86400 seconds and increment 0–3600. No multi-stage/delay controls, FEN starts, variants, multiple games or sub-millisecond clocks. Move labels are not checked for chess legality. No engine, cheating, flag, network lag or actual-thinking-time inference; totals cover only computed evidence.

## Verify

```sh
python3 -m unittest -v test_behavior
python3 -m compileall -q .
python3 -m pip wheel --no-deps --wheel-dir dist .
python3 -m venv /tmp/pgn-clock-ledger-check
/tmp/pgn-clock-ledger-check/bin/python -m pip install --no-deps dist/*.whl
python3 verify_installed.py /tmp/pgn-clock-ledger-check/bin/python
```

Installed-command checks run outside the checkout. See [validation](VALIDATION.md), [research](RESEARCH.md), [contributing](CONTRIBUTING.md), [support](SUPPORT.md) and [security](SECURITY.md).

Original implementation and invented fixtures developed with AI assistance. MIT license. No production adoption, competitor feature-absence or performance-superiority claim.
