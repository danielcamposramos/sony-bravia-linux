# Signal Ledger federation contract

Consumer repositories store only immutable pointers: upstream repository and
branch, claim ID, canonical semantic hash, expected authority reason, and an
explicit supersession policy. Claim bodies remain canonical in the producing
repository.

The verifier reads the upstream ledger at its current append-only branch,
recomputes every upstream semantic hash, derives correction/supersession state,
then checks each local pointer. This provides two properties at once:

- unrelated upstream appends do not invalidate existing pointers;
- a changed claim, correction, supersession or authority-state change cannot
  silently flow into a consumer.

The generated consumer view is deterministic. `SUPPORTED` and deliberately
`UNTESTED` claims are both valid pointer targets when declared exactly;
corrected or superseded targets fail unless a historical consumer explicitly
opts into them.
