#!/usr/bin/env python3
"""hmd-edid.py: a 3D display's own EDID, marked as a head-mounted display.

SteamVR on Linux drives its headset directly, leased from the desktop
compositor, and KWin offers a display for leasing only when the kernel marks
its connector non-desktop. The kernel sets that when the EDID carries a
DisplayID 2.0 extension whose base section declares the primary use
"head-mounted VR" (drivers/gpu/drm/drm_edid.c,
drm_displayid_process_base_section_header, reached from the first data
block). This copies the display's EDID unchanged and appends one such block:
header (version 0x20, primary use 7) and one harmless Product Identification
data block (tag 0x20: no OUI, the display's product code, no name), so every
mode and the HDMI 3D information stay as the display declares them.

Load it at run time through the kernel's EDID override (root):
    cat OUT > /sys/kernel/debug/dri/<card>/<connector>/edid_override
    echo detect > /sys/class/drm/<cardN-connector>/status
and undo it by writing exactly the five bytes "reset", with no newline
(printf reset > .../edid_override; the kernel reads "reset\n" from echo as
an EDID and refuses it with an I/O error), then echo off and detect to the
connector's status so the desktop takes the display back. Nothing is written to disk
outside OUT; a reboot clears the override too.

Usage: hmd-edid.py card1-HDMI-A-2 OUT.bin
"""
import sys

EDID_BLOCK = 128
DISPLAYID_EXT = 0x70
DISPLAYID_VER_20 = 0x20
PRIMARY_USE_HEAD_MOUNTED_VR = 7
DATA_BLOCK_2_PRODUCT_ID = 0x20


def checksum(data):
    return (256 - sum(data) % 256) % 256


def displayid_hmd_block(product_code):
    # Product Identification data block: OUI (3), product code (2, little
    # endian), serial (4), week (1), year (1), name length (1): 12 bytes.
    payload = bytes([0, 0, 0, product_code & 255, product_code >> 8, 0, 0, 0, 0, 0, 0, 0])
    blocks = bytes([DATA_BLOCK_2_PRODUCT_ID, 0x00, len(payload)]) + payload
    header = bytes([DISPLAYID_VER_20, len(blocks), PRIMARY_USE_HEAD_MOUNTED_VR, 0])
    section = header + blocks
    section += bytes([checksum(section)])          # DisplayID checksum
    ext = bytes([DISPLAYID_EXT]) + section
    ext += bytes(EDID_BLOCK - 1 - len(ext))
    return ext + bytes([checksum(ext)])            # EDID extension checksum


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    connector, out = sys.argv[1], sys.argv[2]
    edid = bytearray(open(f"/sys/class/drm/{connector}/edid", "rb").read())
    if len(edid) < EDID_BLOCK or edid[:8] != b"\x00\xff\xff\xff\xff\xff\xff\x00":
        sys.exit(f"{connector}: no EDID")
    blocks = len(edid) // EDID_BLOCK
    if any(edid[i * EDID_BLOCK] == DISPLAYID_EXT for i in range(1, blocks)):
        sys.exit(f"{connector}: already has a DisplayID extension; not touched")
    vendor = edid[8] << 8 | edid[9]
    name = "".join(chr(((vendor >> s) & 31) + 64) for s in (10, 5, 0))
    product = edid[10] | edid[11] << 8
    edid[126] += 1                                 # one more extension block
    edid[127] = checksum(edid[:127])
    edid += displayid_hmd_block(product)
    open(out, "wb").write(edid)
    print(f"{connector}: {name} 0x{vendor:04x} product 0x{product:04x}, "
          f"{blocks} blocks -> {len(edid) // EDID_BLOCK}, head-mounted VR block added: {out}")


if __name__ == "__main__":
    main()
