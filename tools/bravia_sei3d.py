#!/usr/bin/env python3
"""bravia_sei3d.py — restore 3D auto-detection to SBS/T&B movie files, losslessly.

WHY: Era BRAVIA DLNA players (KDL-EX725 / KDL-HX855, AZ2-F / AZ3 — likely the
whole 2011-2012 family) auto-engage 3D ("Foi detectado um sinal 3D") when the
H.264 elementary stream carries a frame_packing_arrangement SEI (payload type
45). Live-proven 2026-09-13 on a KDL-46EX725 via Serviio: injected SEI → TV
flips to 3D unaided; byte-identical clip without it → stays flat.

Web rips lost that signal: they only carry the Matroska StereoMode container
flag, which any MKV->TS remux strips (Serviio included) and which the DLNA
player ignores. Commercial servers "solve" this with paid re-encodes.

HOW: This tool re-inserts a 16-byte SEI NAL (harvested verbatim from x264
--frame-packing 3/4/2 — the exact bytes the TV was tested against) before
every IDR of the EXISTING video elementary stream. Picture data stays
byte-identical. No re-encode, no quality loss, ~0.002% size increase. The
Matroska stereo_mode flag is restored on the remux as a bonus.

Works on h264 video in MKV/MK3D (via mkvextract) and MP4/AVI/FLV/TS
(via ffmpeg). Non-h264 files (e.g. mpeg4-ASP AVIs) are skipped — SEI is an
H.264 mechanism; those need a re-encode instead.

Detection cascade per file: Matroska stereo_mode tag -> filename tokens
(sbs/tb/interlaced) -> full-frame geometry (width/height exactly 2x) ->
[3D]. filename convention -> skipped (report shows why).

Usage:
  bravia_sei3d.py "0 3D" --recursive --dry-run     # report only
  bravia_sei3d.py "0 3D" --recursive --in-place    # fix the library
  bravia_sei3d.py Movie.mkv --mode sbs             # single file, forced mode

Requires: mkvmerge, mkvextract, ffmpeg+ffprobe (any 6.x+), python3.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SEI_NAL = {  # x264-verbatim frame_packing_arrangement SEI (4-byte start code)
    "sbs": bytes.fromhex("0000000106" "2d" "07" "81810000030001" "2080"),
    "tb":  bytes.fromhex("0000000106" "2d" "07" "82010000030001" "2080"),
    "row": bytes.fromhex("0000000106" "2d" "07" "81010000030001" "2080"),
}
STEREO_MAP = {  # ffprobe stereo_mode -> (mode, Matroska StereoMode number)
    "left_right": ("sbs", 1), "right_left": ("sbs", 2),
    "top_bottom": ("tb", 4), "bottom_top": ("tb", 3),
    "row_lr": ("row", 7),
}
MODE_TO_MKV = {"sbs": 1, "tb": 4, "row": 7}
MKV_EXTRACT_EXTS = {".mkv", ".mk3d", ".webm"}
FFMPEG_EXTS = {".mp4", ".m4v", ".mov", ".avi", ".flv", ".ts", ".m2ts", ".mpg"}
VIDEO_EXTS = MKV_EXTRACT_EXTS | FFMPEG_EXTS
NAME_TOKENS = [
    (re.compile(r"sbs|hsbs|side.?by.?side|lado.a.lado", re.I), "sbs"),
    (re.compile(r"\btb\b|\btab\b|htb|top.?and.?bottom|top.?bottom|cima.e.baixo|up.and.down", re.I), "tb"),
    (re.compile(r"interlac|entrelaç|row.?il|field.?seq", re.I), "row"),
]


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def probe(path):
    """(vcodec, stereo_mode, fps, width, height) of the first video stream."""
    r = run(["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream_tags=stereo_mode:stream=codec_name,r_frame_rate,width,height",
             "-of", "json", str(path)])
    s = json.loads(r.stdout)["streams"][0]
    return (s.get("codec_name"), s.get("tags", {}).get("stereo_mode"),
            s.get("r_frame_rate", "25/1"), s.get("width"), s.get("height"))


def annexb_nals(data):
    marks = []
    for m in re.finditer(b"\x00\x00\x01", data):
        pos = m.start()
        sc = 4 if pos >= 1 and data[pos - 1:pos] == b"\x00" else 3
        marks.append((pos - (sc - 3), sc))
    for i, (pos, sc) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(data)
        yield pos, sc, end, data[pos + sc] & 0x1F


def inject_sei(es, sei):
    """Insert `sei` before every IDR NAL. Returns (new_es, count)."""
    out, count, last = bytearray(), 0, 0
    for pos, _sc, _end, nt in annexb_nals(es):
        if nt == 5:
            out += es[last:pos] + sei
            count += 1
            last = pos
    out += es[last:]
    return bytes(out), count


SEI_MARK = re.compile(  # ffmpeg >= 9 names the section; 6.x prints the payload-type line
    r"Frame Packing Arrangement"
    r"|last_payload_type_byte\s+\S+\s*=\s*45\s*$",
    re.MULTILINE)


def count_sei(path, seconds=8):
    """Genuine frame-packing SEI (payload type 45) count in the head of the file.

    NOTE: never match a bare '= 45' — trace_headers dumps hundreds of bit
    fields and any of them can hold the value 45. Only the payload-type
    line (anchored) or the parsed section name count.
    """
    r = subprocess.run(["ffmpeg", "-v", "trace", "-i", str(path), "-t", str(seconds),
                        "-c:v", "copy", "-bsf:v", "trace_headers", "-f", "null", "-"],
                       capture_output=True, text=True)
    return len(SEI_MARK.findall(r.stderr))


def detect_mode(path, tag, w, h, default_sbs_ok):
    """Detection cascade. Returns (mode, reason) or (None, reason)."""
    if tag in STEREO_MAP:
        return STEREO_MAP[tag], f"tag:{tag}"
    for rx, mode in NAME_TOKENS:
        if rx.search(path.name):
            return mode, "filename"
    if w and h:
        if w >= 2048 and w / h >= 3.0:
            return "sbs", "geometry:2x-width"
        if h >= 1440 and h / w >= 1.7:
            return "tb", "geometry:2x-height"
    if default_sbs_ok:
        return "sbs", "default (3D folder/name convention)"
    return None, "no 3D signal (tag/filename/geometry); use --mode or --default-sbs"


def extract_es(path, td):
    """Pull the first video ES as Annex-B into td/v.h264. Returns track count info."""
    es = Path(td) / "v.h264"
    if path.suffix.lower() in MKV_EXTRACT_EXTS:
        r = run(["mkvmerge", "-J", str(path)])
        vt = next(t["id"] for t in json.loads(r.stdout)["tracks"] if t["type"] == "video")
        run(["mkvextract", "tracks", str(path), f"{vt}:{es}"])
    else:
        run(["ffmpeg", "-y", "-v", "error", "-i", str(path), "-map", "0:v:0",
             "-c:v", "copy", "-bsf:v", "h264_mp4toannexb", "-f", "h264", str(es)])
    return es


def process(path, out_path, mode, fps, mkv_stereo):
    """Extract -> inject -> remux. Returns (idr_count, bytes_added)."""
    with tempfile.TemporaryDirectory(prefix="sei3d_") as td:
        es = extract_es(path, td)
        data = es.read_bytes()
        new, n = inject_sei(data, SEI_NAL[mode])
        if n == 0:
            return 0, 0
        new_es = Path(td) / "v.sei.h264"
        new_es.write_bytes(new)
        r = subprocess.run(
            ["mkvmerge", "-o", str(out_path), "--no-video", str(path),
             "--compression", "0:none", "--default-duration", f"0:{fps}fps",
             "--stereo-mode", f"0:{mkv_stereo}", str(new_es)],
            capture_output=True, text=True)
        if r.returncode > 1:
            raise RuntimeError(f"mkvmerge rc={r.returncode}: {r.stderr[-400:]}")
        return n, len(new) - len(data)


def stream_counts(path):
    r = run(["ffprobe", "-v", "error", "-show_entries", "stream=index,codec_type",
             "-of", "csv=p=0", str(path)])
    kinds = [l.split(",")[1] for l in r.stdout.splitlines() if "," in l]
    return {k: kinds.count(k) for k in set(kinds)}


def fmt_duration(path):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", str(path)])
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def handle_file(path, a):
    vcodec, tag, fps, w, h = probe(path)
    if vcodec != "h264":
        return f"SKIP  {path.name}: video is {vcodec}, not h264 (SEI is H.264-only)"
    if count_sei(path):
        return f"SKIP  {path.name}: already carries frame-packing SEI (idempotent)"
    mode, reason = (a.mode, "forced") if a.mode != "auto" else detect_mode(
        path, tag, w, h, a.default_sbs or "[3D]" in path.name or "3D" in str(path.parent).upper())
    if mode is None:
        return f"SKIP  {path.name}: {reason}"
    mkv_stereo = STEREO_MAP.get(tag, (None, MODE_TO_MKV[mode]))[1]

    if a.dry_run:
        return f"WOULD {path.name}: mode={mode} ({reason}), fps={fps}, {w}x{h}"

    if a.in_place:
        out_path = path.with_suffix(".sei3d.tmp.mkv")
    else:
        out_path = path.with_name(path.stem + a.suffix + ".mkv")
    try:
        n, added = process(path, out_path, mode, fps, mkv_stereo)
    except Exception as e:
        out_path.unlink(missing_ok=True)
        return f"FAIL  {path.name}: {e}"
    if n == 0:
        out_path.unlink(missing_ok=True)
        return f"SKIP  {path.name}: no IDR NALs found (unusual stream)"

    # verify before replacing anything
    ok = count_sei(out_path) > 0
    dur = fmt_duration(out_path)
    orig_dur = fmt_duration(path)
    sc_ok = stream_counts(out_path) == stream_counts(path)
    if not (ok and sc_ok and abs(dur - orig_dur) < 2.0):
        out_path.unlink(missing_ok=True)
        return (f"FAIL  {path.name}: verify failed "
                f"(sei={ok} streams={sc_ok} dur {orig_dur:.0f}->{dur:.0f})")
    if a.in_place:
        if a.backup:
            path.rename(path.with_name(path.name + ".bak"))
        else:
            os.remove(path)
        final = path.with_suffix(".mkv")  # remuxed container is Matroska
        os.rename(out_path, final)
    else:
        final = out_path
    sz = final.stat().st_size / 2**30
    return f"FIXED {path.name}: {mode} ({reason}), {n} IDRs, +{added}B, {sz:.2f}GiB"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("target", help="movie file, or folder to batch")
    ap.add_argument("--recursive", action="store_true", help="recurse into subfolders")
    ap.add_argument("--mode", default="auto", choices=["auto", "sbs", "tb", "row"])
    ap.add_argument("--in-place", action="store_true",
                    help="replace the original file after verified remux (else write alongside)")
    ap.add_argument("--suffix", default=".sei3d", help="suffix for non-in-place output")
    ap.add_argument("--backup", action="store_true", help="with --in-place, keep NAME.bak")
    ap.add_argument("--default-sbs", action="store_true",
                    help="treat untagged/unsigned files as SBS (default already applies to [3D] names / 3D folders)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    target = Path(a.target)
    files = ([target] if target.is_file()
             else sorted(p for p in (target.rglob("*") if a.recursive else target.glob("*"))
                         if p.is_file() and p.suffix.lower() in VIDEO_EXTS))
    if not files:
        sys.exit(f"no video files under {target} "
                 f"({'recursive' if a.recursive else 'top level only — try --recursive'})")
    print(f"[sei3d] {len(files)} file(s) | mode={a.mode} | "
          f"{'DRY RUN' if a.dry_run else ('IN-PLACE' if a.in_place else 'write alongside')}")
    fixed = skipped = failed = 0
    for p in files:
        try:
            line = handle_file(p, a)
        except Exception as e:
            line = f"FAIL  {p.name}: {e}"
        print(line, flush=True)
        fixed += line.startswith("FIXED")
        skipped += line.startswith("SKIP")
        failed += line.startswith("FAIL")
    print(f"[sei3d] done: {fixed} fixed, {skipped} skipped, {failed} failed")


if __name__ == "__main__":
    main()