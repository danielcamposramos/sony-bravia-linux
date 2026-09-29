# Signal Ledger validator contract

The validator keeps five boundaries machine-checkable:

1. `basis` describes where a claim comes from; `epistemic` describes whether
   it is supported, inferred or untested; `domain` describes the layer.
2. Only a supported, named human observation may assert `visible-sink`
   behavior. A driver log cannot become a picture or OSD observation.
3. Measurement and observation records are repository-relative artifacts with
   recomputed SHA-256 hashes.
4. Inferences cite premises, stay inside one domain and lose authority when a
   premise is corrected or superseded.
5. Claim files are append-only. Corrections and replacements are new graph
   edges, so the historical record remains inspectable.

Entry hashes are SHA-256 over compact, key-sorted JSON made from parsed TOML.
Unicode is NFC-normalized; relationship arrays are sorted; comments and TOML
layout therefore do not change the semantic hash. The generated Markdown view
contains no wall-clock timestamp and must reproduce byte-for-byte in CI.

Premises on inferred claims are authority-bearing. Premises on a supported
human observation are context links: they connect the driver state to the test
window, but a later correction to that driver interpretation cannot erase what
the observer physically saw.

Federation pins individual semantic entry hashes rather than a whole-ledger
hash, avoiding churn when unrelated claims are appended. Sister repositories
store only verified pointers and generated views; this Bravia ledger remains
the canonical claim authority.
