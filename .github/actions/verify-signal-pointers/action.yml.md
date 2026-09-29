# Verify Signal Ledger pointers action

This composite action runs the canonical federation verifier from the Bravia
repository against the caller's checked-out workspace. Consumers pin the action
to a full commit SHA while their pointers follow the producer's append-only
ledger branch and pin individual semantic claim hashes.

The caller needs Python 3.11 or later and a normal `actions/checkout` step.
