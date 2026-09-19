#!/usr/bin/env python3
"""Inject a frame packing arrangement SEI message into a raw HEVC Annex B stream.

The message is written as a prefix SEI NAL unit immediately before the first
IRAP picture, which is where encoders (e.g. x264 for AVC) place it. The syntax
follows Rec. ITU-T H.265, annex D.2.7 / D.3.7; the leading fields are the same
as in Rec. ITU-T H.264.

Usage: hevc_inject_frame_packing.py in.h265 out.h265 [--type 3] [--ci 1|2] [--cancel]
"""

import argparse
import sys


class BitWriter:
    def __init__(self):
        self.bytes = bytearray()
        self.pos = 0

    def put(self, value, count):
        for i in range(count - 1, -1, -1):
            if self.pos == 0:
                self.bytes.append(0)
            if (value >> i) & 1:
                self.bytes[-1] |= 0x80 >> self.pos
            self.pos = (self.pos + 1) & 7

    def put_ue(self, value):
        code_num = value + 1
        num_bits = code_num.bit_length() - 1
        self.put(0, num_bits)
        self.put(code_num, num_bits + 1)

    def align_with_trailing_bits(self):
        self.put(1, 1)
        while self.pos:
            self.put(0, 1)


def escape_ebsp(rbsp):
    out = bytearray()
    zeros = 0
    for b in rbsp:
        if zeros == 2 and b <= 3:
            out.append(3)
            zeros = 0
        out.append(b)
        zeros = zeros + 1 if b == 0 else 0
    return out


def build_sei_nalu(arrangement_type, content_interpretation_type, cancel):
    w = BitWriter()
    w.put_ue(0)                    # frame_packing_arrangement_id
    w.put(1 if cancel else 0, 1)   # frame_packing_arrangement_cancel_flag

    if cancel:
        w.align_with_trailing_bits()
    else:
        w.put(arrangement_type, 7)              # frame_packing_arrangement_type
        w.put(0, 1)                             # quincunx_sampling_flag
        w.put(content_interpretation_type, 6)   # content_interpretation_type
        w.put(0, 1)                             # spatial_flipping_flag
        w.put(0, 1)                             # frame0_flipped_flag
        w.put(1, 1)                             # current_frame_is_frame0_flag
        w.put(0, 1)                             # field_views_flag
        w.put(1, 1)                             # frame0_self_contained_flag
        w.put(1, 1)                             # frame1_self_contained_flag
        w.put(0, 8)                             # frame_packing_arrangement_reserved_byte
        w.put(1, 1)                             # frame_packing_arrangement_persistence_flag
        w.put(0, 1)                             # upsampled_aspect_ratio_flag
        w.align_with_trailing_bits()

    payload = bytes(w.bytes)
    assert len(payload) < 255

    header = bytes([39 << 1, 1])   # nal_unit_type 39 (prefix SEI), nuh_layer_id 0, nuh_temporal_id_plus1 1
    message = bytes([45, len(payload)]) + payload

    return header + bytes(escape_ebsp(message))


def split_annex_b(data):
    units = []
    i = 0
    start = None
    while i < len(data) - 3:
        if data[i:i+3] == b"\x00\x00\x01":
            if start is not None:
                units.append((start, i))
            i += 3
            start = i
        elif data[i:i+4] == b"\x00\x00\x00\x01":
            if start is not None:
                units.append((start, i))
            i += 4
            start = i
        else:
            i += 1
    if start is not None:
        units.append((start, len(data)))
    return [(s, e, (data[s] >> 1) & 0x3F) for s, e in units if s < e]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--type", type=int, default=3, help="frame_packing_arrangement_type (3 = side by side, 4 = top/bottom)")
    ap.add_argument("--ci", type=int, default=1, help="content_interpretation_type (1 = frame0 is left, 2 = frame0 is right)")
    ap.add_argument("--cancel", action="store_true")
    args = ap.parse_args()

    data = open(args.input, "rb").read()
    units = split_annex_b(data)

    irap = next(((s, e, t) for s, e, t in units if t in (19, 20, 21)), None)
    if not irap:
        sys.exit("no IRAP picture found")

    # Insert before the start code of the first IRAP NAL unit.
    insert_at = irap[0]
    while data[insert_at - 1] == 0 and not (data[insert_at - 4:insert_at] == b"\x00\x00\x00\x01" or data[insert_at - 3:insert_at] == b"\x00\x00\x01"):
        insert_at -= 1
    insert_at -= 4 if data[insert_at - 4:insert_at] == b"\x00\x00\x00\x01" else 3

    sei = build_sei_nalu(args.type, args.ci, args.cancel)
    out = data[:insert_at] + b"\x00\x00\x00\x01" + sei + data[insert_at:]
    open(args.output, "wb").write(out)

    print(f"injected prefix SEI: type={args.type} ci={args.ci} cancel={args.cancel} at byte {insert_at}")


if __name__ == "__main__":
    main()
