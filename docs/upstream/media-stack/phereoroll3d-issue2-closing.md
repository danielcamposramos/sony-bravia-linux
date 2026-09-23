Thank you, that was very much useful! And I will keep it shorter this time, the thing is that this subject is vast and extensive...

Taking your corrections first. I maintain a public list of stereoscopy resources and it was wrong about two of your projects: it presented StereoWebViewer as a current tool and PhotoRoll3D as work in progress. Both are fixed now, pointing at threejs-StereoscopicEffects as the maintained path and noting that Stereopix uses it. I also corrected the Phereo entry with the specific facts you gave, the lost window between 2019 and 2022 and the broken search, instead of the vague note I had. The list is at https://github.com/danielcamposramos/awesome-stereoscopy and you are welcome to use or cite anything in it. Your work is in there, including a2sbs.py and mpo2sbs.py, which I added after your reply.

So I will move the investigation up the ladder you suggested as the projects that went on.

What I learned on the televisions since I wrote, in case it is useful to you:

3D still photos do work on these sets, but only from USB, and only once the file is exactly right. My own MPO writer had been typing view 0 as Baseline Primary; once both views are typed Disparity (0x020002) the set engages 3D by itself. Over the network the same bytes stay flat. I served one file four ways and the set never even listed it as image/mpo, with or without the DLNA profile, while image/jpeg was listed and displayed in 2D. The set filters against its own GetProtocolInfo, so no DLNA server can fix this. It is a software gate rather than a missing capability.

The browser is gated the same way. The panel detects the 3D signal in a web video and is simply not allowed to switch, manually or automatically, although the same panel switches happily from other inputs.

Which is why your sentence about the canvas fallback was the most useful line in your answer. You are right that it would not solve activating 3D on the set, and that is exactly the reason this project renders server side instead of trying to build a viewer for a 2011 browser.

Your gstreamer idea is now written down as a design. Our current tool only repairs files that already exist, while a gstreamer input stage would make any application that can output side by side usable on these televisions, which is a much better shape.

For the record, the signalling work went upstream since then: HandBrake and Universal Media Server merged the fixes, and MKVToolNix is reviewing two merge requests now.

Closing this, since all three questions are answered. Thanks again for taking the time.
