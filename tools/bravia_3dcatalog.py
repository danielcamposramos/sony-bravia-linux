#!/usr/bin/env python3
"""
bravia_3dcatalog.py — build a 3D index of the library.

The serving side has to know what it is serving. Detection itself is not
new here: ffmpeg-3d-wrapper.sh has been deciding "is this input 3D?" on
every Serviio transcode for a while, from filename tokens and the
Matroska stereo_mode tag. Its flaw is that the answer is thrown away
after each file — it decides one encode and forgets, so nothing ever
accumulates and nothing can be browsed.

This is that same detection, lifted out of the transcode path and
written down: walk the library, type every file, emit one JSON index
keyed by path. The portal then serves a 3D category from the index
(All 3D photos / All 3D movies-series-videos) instead of leaving the
content scattered across whatever folder tree happens to hold it.

TYPES
    sbs  tab  row  col  anaglyph  jps  mpo  frame-packed  unknown

CONFIDENCE, stated per row and never inflated
    certain   the file says so: .jps/.mpo extension, Matroska stereo_mode,
              an H.264 frame_packing SEI, or an owner override
    likely    a filename token the wrapper already trusts in production
              (sbs/hsbs/tb/tab/htb/[3D]/lado-a-lado/cima-e-baixo)
    guess     measured from pixels — aspect ratio, row/column correlation,
              red-vs-cyan channel divergence. These WILL be wrong
              sometimes, which is the whole reason overrides exist.

An owner override always wins. A guess must never outvote the person who
owns the content.

Usage
    bravia_3dcatalog.py scan DIR [DIR...] [-o index.json] [--deep]
    bravia_3dcatalog.py show index.json [--type anaglyph] [--photos|--videos]
    bravia_3dcatalog.py set  index.json PATH TYPE     # owner override
"""
import argparse, json, os, re, subprocess, sys, time

PHOTO_EXT = {".jpg", ".jpeg", ".png", ".jps", ".mpo", ".pns", ".gif", ".bmp",
             ".tif", ".tiff", ".webp"}
VIDEO_EXT = {".mkv", ".mp4", ".m4v", ".avi", ".wmv", ".webm", ".mov", ".mpg",
             ".mpeg", ".m2ts", ".ts", ".rmvb", ".flv", ".ogm", ".divx"}

# The tokens ffmpeg-3d-wrapper.sh already acts on in production, kept
# deliberately identical so the catalogue and the transcode path cannot
# disagree about the same file.
TOK_SBS = re.compile(r"sbs|hsbs|side.?by.?side|lado.a.lado", re.I)
TOK_TAB = re.compile(r"\b(tb|tab|htb)\b|top.?bottom|cima.e.baixo|up.and.down", re.I)
TOK_3D = re.compile(r"\[3d\]", re.I)
TOK_ANA = re.compile(r"anaglyph|anag|\bana\b|red.?cyan", re.I)
TOK_ROW = re.compile(r"row.?inter|interlaced|line.?inter", re.I)
TOK_COL = re.compile(r"col(umn)?.?inter", re.I)


def ffprobe(path, entries):
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", entries,
             "-of", "default=nw=1:nk=1", path],
            capture_output=True, text=True, timeout=30)
        return out.stdout.strip()
    except Exception:
        return ""


def probe_video(path):
    """certain > likely. Container tag and stream side-data both count."""
    tag = ffprobe(path, "stream_tags=stereo_mode")
    if tag:
        t = tag.lower()
        if "left" in t or "sbs" in t or t in ("1", "11"): return "sbs", "certain", f"stereo_mode={tag}"
        if "top" in t or "bottom" in t: return "tab", "certain", f"stereo_mode={tag}"
        if "row" in t: return "row", "certain", f"stereo_mode={tag}"
        if "column" in t: return "col", "certain", f"stereo_mode={tag}"
        return "frame-packed", "certain", f"stereo_mode={tag}"
    side = ffprobe(path, "frame=side_data_list")
    if side and "Stereo" in side:
        return "frame-packed", "certain", "SEI frame_packing"
    return None


def measure_photo(path, deep=False):
    """Pixel evidence. Always 'guess' — it is measurement, not declaration."""
    try:
        import numpy as np
        from PIL import Image
    except ImportError:
        return None
    try:
        im = Image.open(path); im.draft("RGB", (512, 512))
        a = np.asarray(im.convert("RGB"), dtype=np.float32) / 255.0
    except Exception:
        return None
    h, w, _ = a.shape
    if h < 16 or w < 16: return None
    # anaglyph: red channel decorrelates from green/blue when two views are
    # multiplexed into colour, which is exactly what the format does.
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    cyan = (g + b) / 2
    def corr(x, y):
        x = x - x.mean(); y = y - y.mean()
        d = (x.std() * y.std())
        return float((x * y).mean() / d) if d > 1e-6 else 1.0
    c = corr(r, cyan)
    if c < 0.86:
        return "anaglyph", "guess", f"red/cyan corr={c:.3f}"
    if not deep: return None
    # side-by-side / top-bottom: the two halves correlate far better than
    # random halves of a normal photo do.
    lh, rh = a[:, :w // 2], a[:, w // 2:w // 2 * 2]
    th, bh = a[:h // 2], a[h // 2:h // 2 * 2]
    cs = corr(lh.mean(2), rh.mean(2)) if lh.shape == rh.shape else 0
    ct = corr(th.mean(2), bh.mean(2)) if th.shape == bh.shape else 0
    if cs > 0.62 and cs > ct: return "sbs", "guess", f"half corr={cs:.3f}"
    if ct > 0.62: return "tab", "guess", f"half corr={ct:.3f}"
    return None


def classify(path, deep=False):
    name = os.path.basename(path)
    ext = os.path.splitext(name)[1].lower()
    kind = "photo" if ext in PHOTO_EXT else "video" if ext in VIDEO_EXT else None
    if not kind: return None
    if ext == ".jps": return kind, "jps", "certain", "extension (.jps = SBS JPEG)"
    if ext == ".pns": return kind, "jps", "certain", "extension (.pns = SBS PNG)"
    if ext == ".mpo": return kind, "mpo", "certain", "extension (.mpo)"
    if kind == "video":
        got = probe_video(path)
        if got: return (kind,) + got
    for rx, t in ((TOK_SBS, "sbs"), (TOK_TAB, "tab"), (TOK_ROW, "row"),
                  (TOK_COL, "col"), (TOK_ANA, "anaglyph")):
        if rx.search(name): return kind, t, "likely", f"filename token ({t})"
    if TOK_3D.search(name): return kind, "sbs", "likely", "filename token ([3D])"
    if kind == "photo":
        got = measure_photo(path, deep)
        if got: return (kind,) + got
    return None


def cmd_scan(a):
    idx = {"generated": time.strftime("%Y-%m-%dT%H:%M:%S"), "roots": a.dirs,
           "items": {}, "overrides": {}}
    if os.path.exists(a.out):                       # never lose overrides
        try:
            idx["overrides"] = json.load(open(a.out)).get("overrides", {})
        except Exception: pass
    seen = n3d = 0
    for root in a.dirs:
        for dirpath, _, files in os.walk(root):
            for f in sorted(files):
                p = os.path.join(dirpath, f)
                seen += 1
                got = classify(p, a.deep)
                if not got: continue
                kind, t, conf, why = got
                n3d += 1
                idx["items"][p] = {"kind": kind, "type": t,
                                   "confidence": conf, "evidence": why}
    for p, t in idx["overrides"].items():           # owner always wins
        if p in idx["items"]:
            idx["items"][p].update(type=t, confidence="certain",
                                   evidence="owner override")
        else:
            idx["items"][p] = {"kind": "photo" if os.path.splitext(p)[1].lower()
                               in PHOTO_EXT else "video", "type": t,
                               "confidence": "certain", "evidence": "owner override"}
    json.dump(idx, open(a.out, "w"), indent=1, sort_keys=True)
    by = {}
    for v in idx["items"].values():
        by[v["type"]] = by.get(v["type"], 0) + 1
    print(f"scanned {seen} files, indexed {n3d} as 3D -> {a.out}")
    for t, c in sorted(by.items(), key=lambda kv: -kv[1]):
        print(f"   {t:14} {c}")


def cmd_show(a):
    idx = json.load(open(a.index))
    for p, v in sorted(idx["items"].items()):
        if a.type and v["type"] != a.type: continue
        if a.photos and v["kind"] != "photo": continue
        if a.videos and v["kind"] != "video": continue
        print(f"{v['type']:13} {v['confidence']:8} {os.path.basename(p)[:44]:44} {v['evidence']}")


def cmd_set(a):
    idx = json.load(open(a.index))
    idx.setdefault("overrides", {})[a.path] = a.type
    idx.setdefault("items", {}).setdefault(a.path, {"kind": "photo"})
    idx["items"][a.path].update(type=a.type, confidence="certain",
                                evidence="owner override")
    json.dump(idx, open(a.index, "w"), indent=1, sort_keys=True)
    print(f"override: {a.path} -> {a.type}")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="cmd", required=True)
    sc = s.add_parser("scan"); sc.add_argument("dirs", nargs="+")
    sc.add_argument("-o", "--out", default="3dindex.json")
    sc.add_argument("--deep", action="store_true",
                    help="also measure SBS/TAB layout from pixels (slower)")
    sc.set_defaults(func=cmd_scan)
    sh = s.add_parser("show"); sh.add_argument("index")
    sh.add_argument("--type"); sh.add_argument("--photos", action="store_true")
    sh.add_argument("--videos", action="store_true"); sh.set_defaults(func=cmd_show)
    st = s.add_parser("set"); st.add_argument("index"); st.add_argument("path")
    st.add_argument("type"); st.set_defaults(func=cmd_set)
    a = p.parse_args(); a.func(a)


if __name__ == "__main__":
    main()
