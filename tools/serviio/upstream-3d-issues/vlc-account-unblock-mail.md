# VLC account-unblock mail — raw material, owner sends in his own words

**Status 2026-09-21: SENT — approved by the owner and mailed to
vlc-devel@videolan.org in his own words the same day.** Target:
vlc-devel@videolan.org. Purpose: unblock the code.videolan.org GitLab
account (held for administrator approval since registration), which is the
only gate in front of the prepared x264 MR (`vlc-mr.md` in this folder).
The list-archive link is still to be recorded once the mail shows up there;
the sent copy already sits in his Sent folder.

Doctrine notes (not for sending):

- Plain text. Keep it this short — list admins approve accounts, they do not
  review the campaign.
- No AI-disclosure line by design: this is an admin request, not a
  contribution, and every fact in it is his own (his account, his login
  experience). The HandBrake lesson applies to the MR itself, not to asking
  an admin to flip a switch.
- If the list holds non-member posts for moderation, that is fine — the
  moderators are exactly who this mail is for. Send from the address he
  prefers; no need to subscribe first, but he may if he wants.
- Two fields are now filled (username capitain_jack, same as his git
  account; email capitain_jack@yahoo.com; registration 2026-09-19 per the
  commit that day). The one field left for him: verify the exact wording the
  site shows when he signs in — the standard GitLab text is pre-filled below
  ("Your account is pending approval from your GitLab administrator and
  hence blocked."), but the ONLY authoritative string is the one in his
  browser; if it differs even slightly, replace it with what he sees.

---

Subject: code.videolan.org account pending administrator approval

Hello,

on 2026-09-19 I registered at code.videolan.org using GitHub sign-in, and the account has been waiting for administrator approval since then.
The username is capitain_jack, with the email capitain_jack@yahoo.com.
When I sign in, the site tells me exactly: "Your account is pending approval from your GitLab administrator and hence blocked."
No approval or confirmation email ever arrived, and the site itself offers no contact route for this, so I am asking here.

The reason for the account: I want to report and fix a small gap in the x264 encoder module.
The frame-packing SEI is parsed by the H.264 packetizer and reaches the encoder intact, but is discarded there by default, so a routine transcode turns a 3D stream flat.
I measured this on VLC 3.0.23 and have a patch against master ready, relating to issue #29582.

Could an administrator approve the account, or point me to the right route?

Thank you,
Daniel Ramos
