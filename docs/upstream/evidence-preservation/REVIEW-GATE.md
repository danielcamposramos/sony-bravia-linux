# Adversarial review gate

Use this short gate before a release, upstream post, or evidence refresh. A
checked box means the reviewer opened the cited material; it is not an author's
self-certification.

## Claims and evidence

- [ ] Classify each substantive claim as **measured**, **source-supported**,
  **inferred**, or **untested**. Keep the distinction in the public wording.
- [ ] Name the exact hardware, sink, connection path, mode, format, depth,
  software revision, and relevant configuration for every measured result.
- [ ] Link the reproducer and canonical raw log, and check that their revision
  and digest match the claim.
- [ ] Preserve negative results, superseded diagnoses, and corrections. Make
  the current conclusion prominent without erasing the route to it.
- [ ] Check every standard citation against the exact edition, section, and
  profile being claimed. Do not turn one profile or transport packing into a
  universal format rule.
- [ ] Generate or refresh artifact digests from the bytes being published, then
  verify them from the publication/staging location.

## Environment and safety

- [ ] State whether each build or test was native, Wine/Proton, containerized,
  virtualized, or source inspection only. Do not use "tested on Windows" for a
  Wine-only result.
- [ ] Exercise rollback and state restoration. Compare the relevant files,
  services, modules, display configuration, and user settings before and after
  success, failure, interruption, and uninstall paths.
- [ ] Attribute visible or audible observations explicitly to the human who
  made them; logs and automated probes must not be presented as observations.

## Independent challenge

- [ ] Give a second model or independent reviewer the diff, claim table, logs,
  and known uncertainties. Ask for contradictions, missing controls, unsafe
  cleanup, and over-broad wording—not a summary.
- [ ] Reproduce every actionable review finding against the actual tree.
  Record rejected findings and why; correct confirmed findings before posting.
- [ ] Finish with a human decision: exact outgoing diff/body reviewed, outward
  action authorized, and remaining untested scope stated beside the claim.
