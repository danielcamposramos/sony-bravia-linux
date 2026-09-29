# Signal Ledger data

This folder is the canonical, append-only claim registry for the repository.
The first pilot records the HDMI Deep Color result while keeping instrument
measurements, human-visible behavior, normative citations, inferences and
untested scope separate.

- `ledger.toml` is the deterministic manifest and per-entry hash index.
- `claims/` contains one immutable TOML file per claim.
- Corrections and replacements are new claims with `corrects` or `supersedes`
  edges; an existing claim file is never rewritten after publication.
- The generated human view lives at
  `docs/reference/evidence-ledger/claims.md`.

Run `python3 tools/evidence-ledger/ledger.py check` before publishing.
