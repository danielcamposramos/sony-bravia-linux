#!/usr/bin/env python3
"""
bravia_mpo.py — write and inspect MPO (Multi-Picture Object) stereo files.

Why this exists: `.jps` is a JPEG that no library will admit is a JPEG.
Serviio's own database indexes .mp3 .jpg .flac .wma .mkv .avi .mp4 .m4a
.flv .wav and nothing else — no .jps, no .mpo, not even .png — so the
community's native stereo format is invisible to the DLNA layer.

MPO is the other half of the problem and the more interesting one: it is
what Sony's own 3D cameras wrote (CIPA DC-007), so it is the format these
sets are most likely to recognise as a 3D still. This writes real MPO
files from a stereo pair so that can actually be tested on the hardware
rather than argued about.

Structure written (CIPA DC-007 Multi-Picture Format):
    image 1: JPEG carrying an APP2 "MPF" segment with the MP Index IFD
             (MPFVersion, NumberOfImages, MPEntry)
    image 2: plain JPEG, concatenated
    MP entries carry each image's size and its offset from the MP
    endian field, with the first image's offset fixed at 0 by the spec.
    view 0 is the Baseline MP Primary Image (0x030000) and carries the
    representative flag; view 1 is Multi-frame Image: Disparity (0x020002),
    which is what marks the file as a stereo pair.

Usage
    bravia_mpo.py build LEFT.jpg RIGHT.jpg OUT.mpo
    bravia_mpo.py from-sbs SBS.jpg OUT.mpo        # split an SBS frame first
    bravia_mpo.py inspect FILE.mpo
"""
import argparse, io, struct, sys

# CIPA DC-007 MPType codes. Getting these right matters: a reader deciding
# "is this a 3D still?" looks here, and 0x030002 (which looks plausible) is
# not a defined code at all — exiftool reports it as Unknown.
MP_TYPE_PRIMARY = 0x030000      # Baseline MP Primary Image
MP_TYPE_DISPARITY = 0x020002    # Multi-frame Image: Disparity (a stereo pair)
ATTR_REPRESENTATIVE = 0x20000000


def _split_jpeg_header(data):
    """Return the offset at which an APP2 segment may be inserted: after SOI
    and after any leading APP0/APP1 segments, which the spec expects to
    come first."""
    if data[:2] != b"\xff\xd8":
        raise ValueError("not a JPEG (no SOI)")
    i = 2
    while i + 4 <= len(data) and data[i] == 0xFF and data[i + 1] in (0xE0, 0xE1):
        seg = struct.unpack(">H", data[i + 2:i + 4])[0]
        i += 2 + seg
    return i


def _mpf_segment(sizes, offsets, attrs):
    """Build the APP2 MPF segment. Little-endian ('II') throughout."""
    n = len(sizes)
    ifd = struct.pack("<H", 3)                                  # 3 entries
    ifd += struct.pack("<HHI", 0xB000, 7, 4) + b"0100"          # MPFVersion
    ifd += struct.pack("<HHII", 0xB001, 4, 1, n)                # NumberOfImages
    entry_off = 8 + (2 + 3 * 12 + 4)                            # after the IFD
    ifd += struct.pack("<HHII", 0xB002, 7, 16 * n, entry_off)   # MPEntry
    ifd += struct.pack("<I", 0)                                 # no next IFD
    entries = b""
    for a, s, o in zip(attrs, sizes, offsets):
        entries += struct.pack("<IIIHH", a, s, o, 0, 0)
    body = b"II" + struct.pack("<HI", 0x2A, 8) + ifd + entries
    return b"\xff\xe2" + struct.pack(">H", len(body) + 4 + 2) + b"MPF\x00" + body


def build_mpo(left_bytes, right_bytes):
    ins = _split_jpeg_header(left_bytes)
    n = 2
    # marker(2) + length(2) + 'MPF\0'(4) + TIFF header(8) + IFD(2+3*12+4) + entries
    seg_len = 2 + 2 + 4 + (8 + (2 + 3 * 12 + 4) + 16 * n)
    tiff_at = ins + 2 + 2 + 4                                   # MP endian field
    size1 = len(left_bytes) + seg_len
    size2 = len(right_bytes)
    offset2 = size1 - tiff_at                                   # from MP endian field
    seg = _mpf_segment([size1, size2], [0, offset2],
                       [ATTR_REPRESENTATIVE | MP_TYPE_PRIMARY, MP_TYPE_DISPARITY])
    assert len(seg) == seg_len, (len(seg), seg_len)
    return left_bytes[:ins] + seg + left_bytes[ins:] + right_bytes


def _encode(img, quality=95):
    b = io.BytesIO()
    img.convert("RGB").save(b, format="JPEG", quality=quality)
    return b.getvalue()


def cmd_build(a):
    from PIL import Image
    l = _encode(Image.open(a.left), a.quality)
    r = _encode(Image.open(a.right), a.quality)
    open(a.out, "wb").write(build_mpo(l, r))
    print(f"{a.out}  ({len(l)} + {len(r)} bytes, 2 views)")


def cmd_from_sbs(a):
    from PIL import Image
    im = Image.open(a.sbs).convert("RGB")
    w, h = im.size
    half = w // 2
    l = _encode(im.crop((0, 0, half, h)), a.quality)
    r = _encode(im.crop((half, 0, half * 2, h)), a.quality)
    open(a.out, "wb").write(build_mpo(l, r))
    print(f"{a.out}  ({half}x{h} per view, 2 views)")


def cmd_inspect(a):
    data = open(a.file, "rb").read()
    i = data.find(b"\xff\xe2")
    if i < 0 or data[i + 4:i + 8] != b"MPF\x00":
        print("no MPF APP2 segment — not an MPO"); return 1
    t = i + 8
    n = struct.unpack_from("<I", data, t + 8 + 2 + 12 + 8)[0]
    print(f"{a.file}: MPF present, NumberOfImages={n}, total {len(data)} bytes")
    eo = t + struct.unpack_from("<I", data, t + 8 + 2 + 24 + 8)[0]
    for k in range(n):
        attr, size, off, _, _ = struct.unpack_from("<IIIHH", data, eo + 16 * k)
        print(f"  view {k}: attr=0x{attr:08x} type=0x{attr & 0xFFFFFF:06x} "
              f"size={size} offset={off}")
    try:
        from PIL import Image
        im = Image.open(a.file)
        print(f"  PIL reads it as: format={im.format} size={im.size} "
              f"frames={getattr(im, 'n_frames', 1)}")
    except Exception as e:
        print(f"  PIL could not read it: {e}")
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="cmd", required=True)
    b = s.add_parser("build"); b.add_argument("left"); b.add_argument("right")
    b.add_argument("out"); b.add_argument("--quality", type=int, default=95)
    b.set_defaults(func=cmd_build)
    f = s.add_parser("from-sbs"); f.add_argument("sbs"); f.add_argument("out")
    f.add_argument("--quality", type=int, default=95); f.set_defaults(func=cmd_from_sbs)
    i = s.add_parser("inspect"); i.add_argument("file"); i.set_defaults(func=cmd_inspect)
    a = p.parse_args(); sys.exit(a.func(a) or 0)


if __name__ == "__main__":
    main()
