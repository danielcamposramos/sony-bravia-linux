# Sony KDL-46HX855 sink behavior notes — discovered during the stereo work

Owner-observed behaviors of the 2012 set as an HDMI 1.4 3D sink. Each entry
carries its evidence tag and the run that proved it. The EX725 column is
"untested" unless a note says otherwise.

## "Turn off 3D" on a signaled stereo stream shows ONE EYE as proper 2D [proven — Daniel, HX855, 2026-09-21]

While a source sends a stereo frame with the correct HDMI VSIF announcement
(here: the nvidia-drm VSIF-injection runs 13/14), choosing the TV's "turn off
3D" path does NOT fall back to showing the raw doubled picture (both eyes
side-by-side or stacked, as an unaware sink would). The set decodes the
packing and displays a **single eye, full screen, flat** — a clean 2D
version of the 3D content with no remote gymnastics.

Why it matters: a 3D-encoded broadcast/media stays watchable in proper 2D
for anyone who does not want the glasses at that moment, with no source-side
change. For the campaign this is a user-facing argument that HDMI 1.4 3D
signaling is a *feature with a graceful 2D fallback*, not a trap.

EX725: untested. [qualified] Sony shared the X-Reality 3D handling across
the 2011/2012 generation, but verify on the box before citing it there.

## Inactive HDMI inputs keep HPD dark [proven — 2026-09-21 probes]

A cable on a non-selected input reports `disconnected` (no EDID) until the
input is selected with the remote; it flips to `connected` the instant the
IR switch happens. Test harnesses must either have the input pre-selected
or poll for HPD (run-nvidia-test.sh does the latter) — and probe results on
a dark input are meaningless, not negative.

## Two independent HDMI links can hold the set in 3D simultaneously [proven — run 8/10 window, 2026-09-20]

With the AMD feed on one input and NVIDIA feed on a second, switching inputs
during a stereo mode showed both inputs in 3D state at once. [qualified]
Simultaneous 3D on the HX855 + EX725 from the two GPUs is the logical next
step but has not been run on two physical sets.

## TaB announcement requires the 3D_Ext_Data byte [proven — runs 13/14, 2026-09-21]

A 5-byte HDMI 3D VSIF (spec-minimal for TaB per HDMI 1.4b, which mandates
the extension byte only for SBS-half) is ignored by this sink: no
auto-engagement, picture still correct on manual engage. The same stream
with the zero 3D_Ext_Data byte appended (6-byte body, matching the DRM
core's VSIF helper and Adrian Betschart's amd-gfx v3 2/3) auto-engages.
Same behavior Adrian found behind his JVC projector — second sink family
corroborating that 3D_Ext_Data should be sent for TaB.
