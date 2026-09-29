# Evidence Ledger tool

This small Python 3.11+ tool validates the append-only Signal Ledger and
generates its human-readable diagnostic view.

- `ledger.py.source` is the commented SOURCE projection and the only code file
  partners edit.
- `ledger.py` is the generated machine-runtime projection.
- `ledger.py.md` is the human-readable contract.
- `tests/` contains the adversarial gates, including the visible-sink poison
  pill that must be rejected when presented as an instrument measurement.

Commands:

```text
python3 tools/evidence-ledger/ledger.py check
python3 tools/evidence-ledger/ledger.py sync
python3 tools/evidence-ledger/ledger.py.source compile
python3 -m unittest discover -s tools/evidence-ledger/tests -p 'test_*.py'
```
