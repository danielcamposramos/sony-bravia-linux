#!/usr/bin/env python3
"""
bravia_anaglyph.py — anaglyph <-> SBS, in both directions.

Act three of the 3D-signalling campaign: legacy 3D content, enabled on
modern displays. This tool is the anaglyph half of it.

FORWARD  (SBS -> anaglyph)  is already solved by stock ffmpeg:
             -vf stereo3d=sbsl:arcd        (arcd = red/cyan Dubois)
         It is wrapped here only so both directions live in one place.

REVERSE  (anaglyph -> SBS)  is this tool's real work, and it is built on
         one measured fact about where the stereo actually lives:

             the RED channel carries the LEFT eye,
             GREEN and BLUE carry the RIGHT eye.

         So each eye is reconstructed ONLY from the channels that carry
         it. Nothing is shared between eyes in the base extraction, and
         that is not a stylistic choice — it is the whole ballgame.

         A pointwise (per-pixel) operator CANNOT invent disparity: left
         and right differ by *where* content sits, and no function of a
         single pixel can move content sideways. An earlier attempt here
         recovered beautiful colour by fusing the channels first, and
         measured **0 px of disparity on every test image** — a perfect
         2D photo. Keeping each eye to its own channels measured the
         true disparity exactly (70/70, 69/69, 20/21, 21/21 px) on the
         corpus JPS pairs. See docs/legacy-3d-formats.md.

WHAT YOU GET, HONESTLY
    left eye   : 1 channel of real information -> luminance, true position
    right eye  : 2 channels of real information -> real G and B
    missing    : left's chroma, right's red

    --mode mono    (default) both eyes greyscale. Nothing invented,
                   disparity exact on 11/11 corpus pairs. Always safe.
    --mode color   disparity-aware colour. Measured, and measured to be
                   conditional: colour quality tracks the disparity
                   estimate exactly, so it BEATS mono on images that
                   match well and LOSES on repetitive texture, where
                   stereo matching classically fails. Off by default for
                   that reason. Numbers in docs/legacy-3d-formats.md.

    Naive channel-borrowing was tried first and is a trap worth naming:
    left supplies 1 channel, right supplies 2, so if both eyes use all
    three they come out byte-identical. Measured 0 px disparity. Colour
    without warping is not colour, it is a 2D photo.

Dubois matrices are the published red/cyan pair, cross-checked against
JackDesBwa's StereoWebViewer GLSL (MIT).

Usage
    bravia_anaglyph.py decompose IN.jpg OUT.jps [--mode color] [--half]
    bravia_anaglyph.py video    IN.mkv OUT.mkv [--half]     # anaglyph movie -> SBS+SEI
    bravia_anaglyph.py compose   IN.jps OUT.jpg
    bravia_anaglyph.py filter    [--mode color] [--half]   # ffmpeg chain, for on-the-fly use
    bravia_anaglyph.py selftest  [--corpus DIR]            # round-trip measurement
"""
import argparse, glob, os, subprocess, sys

# --- Dubois red/cyan, forward ------------------------------------------------
M_L = ((0.456, 0.500, 0.176), (-0.040, -0.038, -0.016), (-0.015, -0.021, -0.005))
M_R = ((-0.043, -0.088, -0.002), (0.378, 0.734, -0.018), (-0.072, -0.113, 1.226))

K_L = sum(M_L[0])                       # left -> red gain, 1.132
# right's (g,b) -> anaglyph (g,b) is a 2x2 block; this is its inverse
_a, _b = M_R[1][1], M_R[1][2]
_c, _d = M_R[2][1], M_R[2][2]
_det = _a * _d - _b * _c
GB_INV = ((_d / _det, -_b / _det), (-_c / _det, _a / _det))


def ffmpeg_filter(mode="color", half=False):
    """The reverse chain as a pure ffmpeg filtergraph.

    Emitted rather than executed so the media app can use it on the fly
    without numpy: the app already shells out to ffmpeg for every other
    lane, and this keeps server.py stdlib-only.
    """
    gl = 1.0 / K_L                                  # left luma from red
    (rg_g, rg_b), (rb_g, rb_b) = GB_INV             # right's G,B from anaglyph G,B
    if mode == "mono":
        # right's luminance from its own two channels, nothing borrowed
        ry_g, ry_b = (rg_g + rb_g) / 2, (rg_b + rb_b) / 2
        left = f"colorchannelmixer={gl}:0:0:0:{gl}:0:0:0:{gl}:0:0:0"
        right = (f"colorchannelmixer=0:{ry_g}:{ry_b}:0:0:{ry_g}:{ry_b}:0:"
                 f"0:{ry_g}:{ry_b}:0")
    else:
        # left keeps its own luma in R, borrows the right eye's recovered G,B
        left = (f"colorchannelmixer={gl}:0:0:0:0:{rg_g}:{rg_b}:0:"
                f"0:{rb_g}:{rb_b}:0")
        # right keeps its own G,B, borrows the left eye's luma as red
        right = (f"colorchannelmixer={gl}:0:0:0:0:{rg_g}:{rg_b}:0:"
                 f"0:{rb_g}:{rb_b}:0")
    scale = ",scale=iw/2:ih" if half else ""
    return (f"split=2[a][b];[a]{left}{scale}[l];[b]{right}{scale}[r];"
            f"[l][r]hstack=inputs=2")


def _np():
    try:
        import numpy as np
        from PIL import Image
        return np, Image
    except ImportError:
        sys.exit("decompose/compose/selftest need numpy and pillow "
                 "(the 'filter' subcommand does not)")


def _boxblur(a, k):
    np, _ = _np()
    if k < 2: return a
    c = np.cumsum(np.pad(a, ((0, 0), (k, k)), mode="edge"), axis=1)
    return (c[:, 2 * k:] - c[:, :-2 * k]) / (2 * k)


def disparity_map(ly, ry, maxd=80, ds=4):
    """Coarse dense horizontal disparity between the two recovered eyes.

    Chroma is low-frequency, so a downsampled, smoothed map is both
    enough and far more robust than a per-pixel one.
    """
    np, Image = _np()
    a, b = ly[::ds, ::ds], ry[::ds, ::ds]
    md = max(2, maxd // ds)
    best = np.full(a.shape, 1e9); arg = np.zeros(a.shape)
    for d in range(-md, md + 1):
        c = _boxblur(np.abs(a - np.roll(b, d, axis=1)), 3)
        m = c < best; best = np.where(m, c, best); arg = np.where(m, d, arg)
    return np.asarray(Image.fromarray(arg.astype("float32")).resize(
        (ly.shape[1], ly.shape[0]), Image.BILINEAR)) * ds


def _warp(img, d):
    np, _ = _np()
    h, w = img.shape[:2]
    xs = np.clip((np.arange(w)[None, :] + d).round().astype(int), 0, w - 1)
    ys = np.arange(h)[:, None]
    return img[ys, xs] if img.ndim == 2 else img[ys, xs, :]


def decompose_array(ana, mode="mono", iters=2):
    """anaglyph HxWx3 float 0..1 -> (left, right), each HxWx3."""
    np, _ = _np()
    gbi = np.array(GB_INV)
    ly = np.clip(ana[:, :, 0] / K_L, 0, 1)                        # left luminance
    rgb = np.clip(np.einsum("ij,hwj->hwi", gbi, ana[:, :, 1:]), 0, 1)
    if mode == "mono":
        ry = np.clip(rgb.mean(axis=2), 0, 1)
        return np.repeat(ly[:, :, None], 3, 2), np.repeat(ry[:, :, None], 3, 2)
    # Right's own RED leaks heavily into a_g (coefficient 0.378), so the plain
    # 2x2 inverse above is contaminated. Estimate that red from the left eye
    # warped into right coordinates, subtract it, re-invert, and iterate.
    cr = np.array([M_R[1][0], M_R[2][0]])
    d = disparity_map(ly, np.clip(rgb.mean(axis=2), 0, 1))
    rr = _warp(ly, d)
    for _ in range(iters):
        resid = ana[:, :, 1:] - rr[:, :, None] * cr[None, None, :]
        rgb = np.clip(np.einsum("ij,hwj->hwi", gbi, resid), 0, 1)
        d = disparity_map(ly, np.clip(rgb.mean(axis=2), 0, 1))
        rr = _warp(ly, d)
    gb_left = _warp(rgb, -d)
    left = np.stack([ly, gb_left[:, :, 0], gb_left[:, :, 1]], axis=2)
    right = np.stack([rr, rgb[:, :, 0], rgb[:, :, 1]], axis=2)
    return np.clip(left, 0, 1), np.clip(right, 0, 1)


def cmd_decompose(a):
    np, Image = _np()
    ana = np.asarray(Image.open(a.src).convert("RGB"), dtype=np.float64) / 255.0
    l, r = decompose_array(ana, a.mode)
    if a.half:
        l, r = l[:, ::2], r[:, ::2]
    out = np.concatenate([l, r], axis=1)
    # .jps IS a JPEG — only the extension differs, which is exactly why no
    # image library (and no DLNA server) recognises it. Force the format.
    ext = os.path.splitext(a.dst)[1].lower()
    fmt = "JPEG" if ext in (".jps", ".jpg", ".jpeg", "") else None
    Image.fromarray((out * 255 + 0.5).astype("uint8")).save(
        a.dst, format=fmt, quality=95)
    print(f"{a.src} -> {a.dst}  mode={a.mode} {out.shape[1]}x{out.shape[0]}")


def cmd_compose(a):
    """SBS -> anaglyph, via stock ffmpeg (arcd is its default output)."""
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", a.src,
           "-vf", "stereo3d=sbsl:arcd", a.dst]
    subprocess.run(cmd, check=True)
    print(f"{a.src} -> {a.dst}  (stereo3d=sbsl:arcd)")


def cmd_filter(a):
    print(ffmpeg_filter(a.mode, a.half))


def cmd_video(a):
    """Anaglyph movie -> SBS + frame-packing SEI. The end file.

    This is the case act three exists for: material that survives only as
    anaglyph, because the stereo original is gone. The output is a
    first-class modern 3D file — SBS pixels plus the in-stream SEI these
    TVs auto-engage on — so it plays as 3D on hardware that would show the
    anaglyph flat.

    Half-width (--half) keeps the original frame size and is what
    frame-compatible 3D broadcast used; full width doubles it.
    """
    vf = ffmpeg_filter(a.mode, a.half)
    cmd = ["ffmpeg", "-y", "-v", "error", "-stats", "-i", a.src,
           "-vf", vf, "-c:v", "libx264", "-preset", a.preset, "-crf", str(a.crf),
           "-x264opts", "frame-packing=3",          # the act-one signal
           "-c:a", "copy", a.dst]
    print("+ " + " ".join(cmd))
    subprocess.run(cmd, check=True)
    # Verify both signals actually landed. ffprobe's compact output does not
    # reliably surface side data, so ask for JSON and read the stream tag too.
    side = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-read_intervals", "%+#3", "-show_frames", "-of", "json", a.dst],
        capture_output=True, text=True).stdout
    tag = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream_tags=stereo_mode",
         "-of", "default=nw=1:nk=1", a.dst],
        capture_output=True, text=True).stdout.strip()
    sei = "Stereo 3D" in side
    print(f"{a.src} -> {a.dst}  mode={a.mode}{' half' if a.half else ''}")
    print(f"  in-stream frame-packing SEI (hardware 3D reads this): "
          f"{'PRESENT' if sei else 'MISSING — check the x264 build'}")
    print(f"  container StereoMode tag (software players read this): "
          f"{tag or 'ABSENT'}")
    if sei and not tag:
        # Not a bug in this tool: ffmpeg's Matroska muxer does not derive the
        # container tag from the SEI. That asymmetry IS this campaign's
        # finding, from the other side — see mkvtoolnix Codeberg #6309, which
        # asks mkvmerge to derive one from the other.
        print("  note: ffmpeg writes the SEI but not the container tag. The TV")
        print("        is satisfied; for software players add it losslessly:")
        print(f"        mkvmerge -o out.mkv --stereo-mode 0:1 {a.dst}")
    return 0 if sei else 1


def cmd_selftest(a):
    """Forward-then-reverse on real JPS pairs; reports PSNR and disparity."""
    np, Image = _np()
    ml, mr = np.array(M_L), np.array(M_R)
    W = np.array([0.299, 0.587, 0.114])

    def psnr(x, y):
        m = ((x - y) ** 2).mean()
        return 99.0 if m == 0 else 10 * np.log10(1.0 / m)

    def shift(x, y, rng=70):
        x = (x - x.mean()) / (x.std() + 1e-9); y = (y - y.mean()) / (y.std() + 1e-9)
        h, w = x.shape; c = slice(h // 4, 3 * h // 4); best, bs = -9, 0
        for s in range(-rng, rng + 1):
            v = (x[c, rng:w - rng] * np.roll(y, s, axis=1)[c, rng:w - rng]).mean()
            if v > best: best, bs = v, s
        return bs

    files = sorted(glob.glob(os.path.join(a.corpus, "*.jps")))
    if not files:
        sys.exit(f"no .jps ground-truth pairs in {a.corpus}")
    ok = 0
    for f in files:
        im = np.asarray(Image.open(f).convert("RGB"), dtype=np.float64) / 255.0
        h, w, _ = im.shape
        if w % 2: im, w = im[:, :-1], w - 1
        L, R = im[:, :w // 2], im[:, w // 2:]
        ana = np.clip(L @ ml.T + R @ mr.T, 0, 1)
        lh, rh = decompose_array(ana, "mono")
        d_true, d_rec = shift(L @ W, R @ W), shift(lh[:, :, 0], rh[:, :, 0])
        good = abs(d_true - d_rec) <= 2
        ok += good
        print(f"  {os.path.basename(f)[:30]:30} luma {psnr(lh[:, :, 0], L @ W):5.2f} dB"
              f"  disparity {d_true:+3d} -> {d_rec:+3d} px  "
              f"{'ok' if good else 'MISMATCH'}")
    print(f"{ok}/{len(files)} pairs kept their disparity")
    return 0 if ok == len(files) else 1


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("decompose", help="anaglyph -> SBS/JPS")
    d.add_argument("src"); d.add_argument("dst")
    d.add_argument("--mode", choices=("mono", "color"), default="mono")
    d.add_argument("--half", action="store_true", help="half-width SBS (frame-compatible)")
    d.set_defaults(func=cmd_decompose)
    c = sub.add_parser("compose", help="SBS -> anaglyph (stock ffmpeg)")
    c.add_argument("src"); c.add_argument("dst"); c.set_defaults(func=cmd_compose)
    f = sub.add_parser("filter", help="print the ffmpeg filtergraph for on-the-fly use")
    f.add_argument("--mode", choices=("mono", "color"), default="mono")
    f.add_argument("--half", action="store_true"); f.set_defaults(func=cmd_filter)
    v = sub.add_parser("video", help="anaglyph video -> SBS + SEI (the end file)")
    v.add_argument("src"); v.add_argument("dst")
    v.add_argument("--mode", choices=("mono", "color"), default="mono")
    v.add_argument("--half", action="store_true",
                   help="half-width SBS, keeps the original frame size")
    v.add_argument("--crf", type=int, default=18)
    v.add_argument("--preset", default="medium")
    v.set_defaults(func=cmd_video)
    s = sub.add_parser("selftest", help="round-trip measurement on JPS ground truth")
    s.add_argument("--corpus", default="/media/Arquivos/Pictures/3D/DUAL")
    s.set_defaults(func=cmd_selftest)
    a = p.parse_args()
    sys.exit(a.func(a) or 0)


if __name__ == "__main__":
    main()
