#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bravia_ircc.py -- no-registration IRCC remote-control driver for Sony BRAVIA
Linux TVs (right-to-repair project).

Targets the owner's own hardware on the owner's own LAN:
    - KDL-46HX855 (AZ3F chassis)
    - KDL-46EX725 (expendable test target, default host)

Protocol facts (live-verified 2026-09-13 against these sets, cross-checked
against Sony's official IRCC code table at
https://pro-bravia.sony.net/remote-display-control/ircc-ip/ and the
chr15m/media-remote SNIFF.md capture of a TV-served remoteCommandList):

  * Arbitrary keypresses are UNAUTHENTICATED:
        POST http://<IP>/IRCC
        SOAPAction: "urn:schemas-sony-com:service:IRCC:1#X_SendIRCC"
        Content-Type: "text/xml; charset=UTF-8"
    with an X_SendIRCC SOAP envelope carrying a base64 <IRCCCode>.

  * IRCCCode = base64 of EXACTLY 13 bytes:
        struct.pack(">IIIB", manufacturer, device, function, 0x03)
    i.e. three big-endian u32 words followed by the constant byte 0x03.

  * Standard codes: manufacturer=1, device=1.
    MDF variant: manufacturer=2, device=26 (HDMI1..4 = 0x5a..0x5d).
    Color buttons: manufacturer=2, device 0x97 -- CONFIRMED by the EX725's
    own /cers/api/getRemoteCommandList (2026-09-13, saved in
    docs/research/liverecon/).  The *_alt entries carry the device 0x9c
    variant Sony's Android-generation table uses, kept for that family.

  * URL-type CERS commands (no auth, port 80):
        GET /cers/command/MuteOn   GET /cers/command/MuteOff
    Unauthenticated info: GET /cers/api/getSystemInformation (XML).

  * On the HX855, POST /IRCC is ALSO served on port 52323 (DMR stack); on
    the EX725 /IRCC on 52323 returns 501.  Default port is 80.

PERSISTENT-STATE HAZARD -- read before driving a set:
  Service-mode entry (standby -> DISPLAY -> Ch 5 -> VolumeUp -> POWER)
  writes NVM (persistent factory/service state), and the Mute+0-class /
  digit keys used inside service mode change persistent service values
  too.  Wrong values there can require a full factory reset (or worse,
  NVM re-initialisation) to undo.  The built-in service-mode sequences
  are therefore double-gated: they need BOTH --allow-service-mode on the
  command line AND an interactive y/N confirmation, and the
  confirmation is refused outright when stdin is not a TTY (so 'echo y
  |' cannot bypass it).  VolumeUp+Power never happens implicitly.

SERVICE-MODE ENTRY CANNOT BE ARMED OVER IRCC (live-tested 2026-09-13,
  EX725): with every code verified against the TV's own command list and
  remote-like 0.6 s pacing from standby, the sequence booted the set
  normally every time; the physical remote armed it instantly.  The
  standby arming path evidently does not honour network-injected keys.
  This is also good news for safety: the LAN path cannot write service
  NVM.  Keep the sequences for documentation, but entry needs IR.

This tool never scans, never discovers, and never touches any port other
than the one host:port the operator names.  Stdlib only, Python 3.9+.

Examples:
    python3 tools/bravia_ircc.py send power
    python3 tools/bravia_ircc.py send 0x74                 # raw function hex
    python3 tools/bravia_ircc.py seq vol-up:0.5,vol-up:0.5 --host 192.168.0.20
    python3 tools/bravia_ircc.py seq nav-up
    python3 tools/bravia_ircc.py mute                      # CERS MuteOn
    python3 tools/bravia_ircc.py unmute                     # CERS MuteOff
    python3 tools/bravia_ircc.py info
    python3 tools/bravia_ircc.py codes
    python3 tools/bravia_ircc.py selftest
    python3 tools/bravia_ircc.py seq service-mode-entry --allow-service-mode
"""

import argparse
import base64
import http.client
import math
import re
import socket
import struct
import sys
import time

# --------------------------------------------------------------------------
# Constants and target policy
# --------------------------------------------------------------------------

DEFAULT_HOST = "192.168.0.22"   # the expendable EX725 test target
MONITOR_HOST = "192.168.0.21"   # the workstation's HX855 monitor -- NEVER a default
DEFAULT_PORT = 80              # /IRCC on 52323 works on HX855 only (501 on EX725)
DEFAULT_DELAY = 1.0             # TV IR receivers need spacing between keys
DEFAULT_TIMEOUT = 5.0

IRCC_PATH = "/IRCC"
SOAP_ACTION = "urn:schemas-sony-com:service:IRCC:1#X_SendIRCC"

CERS_MUTE_ON = "/cers/command/MuteOn"
CERS_MUTE_OFF = "/cers/command/MuteOff"
CERS_SYSTEM_INFO = "/cers/api/getSystemInformation"

SOAP_ENVELOPE = (
    '<?xml version="1.0" encoding="utf-8"?>\n'
    '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" '
    's:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">\n'
    '  <s:Body>\n'
    '    <u:X_SendIRCC xmlns:u="urn:schemas-sony-com:service:IRCC:1">\n'
    "      <IRCCCode>{code}</IRCCCode>\n"
    "    </u:X_SendIRCC>\n"
    "  </s:Body>\n"
    "</s:Envelope>"
)

IRCC_TAIL_BYTE = 0x03  # constant final byte of every 13-byte IRCCCode struct


# --------------------------------------------------------------------------
# IRCC code table
#
# Every entry is (name, manufacturer, device, function, description).
# base64 constants are DERIVED from struct.pack(">IIIB", manu, dev, func, 3);
# nothing in this table is a pasted string.  Cross-checked against the
# EX725's OWN authoritative /cers/api/getRemoteCommandList (2026-09-13,
# after CERS registration; saved as
# docs/research/liverecon/cers_remoteCommandList_KDL-46EX725.xml), Sony's
# Android-generation table (pro-bravia.sony.net), and the TV-served list
# captured in chr15m/media-remote SNIFF.md.  Generation differences found:
# color/media family device 0x97 here vs 0x9c on Android-gen.
# --------------------------------------------------------------------------

_KEY_TABLE_RAW = [
    # -- standard codes: manufacturer=1, device=1 --
    ("power",        1,   1, 0x15, "power toggle / standby press"),
    ("input",        1,   1, 0x25, "input select (cycles inputs)"),
    ("gguide",       1,   1, 0x0e, "G-Guide button"),
    ("epg",          2, 164, 0x5b, "electronic programme guide"),
    ("jump",         1,   1, 0x3b, "jump (last channel)"),
    ("teletext",     1,   1, 0x3f, "teletext toggle"),
    ("audio",        1,   1, 0x17, "audio track select"),
    ("subtitle",     2, 151, 0x28, "subtitle cycle"),
    ("closed-caption", 2, 164, 0x10, "closed-caption toggle"),
    ("display",      1,   1, 0x3a, "DISPLAY (info banner; no-op on some "
                                    "inputs on the EX725 despite being "
                                    "in the TV's own table)"),
    ("wide",         2, 164, 0x3d, "wide / aspect mode"),
    ("pap",          2, 164, 0x77, "picture-and-picture"),
    ("program-description", 2, 151, 0x16, "program description overlay"),
    ("num1",         1,   1, 0x00, "digit 1"),
    ("num2",         1,   1, 0x01, "digit 2"),
    ("num3",         1,   1, 0x02, "digit 3"),
    ("num4",         1,   1, 0x03, "digit 4"),
    ("num5",         1,   1, 0x04, "digit 5"),
    ("num6",         1,   1, 0x05, "digit 6"),
    ("num7",         1,   1, 0x06, "digit 7"),
    ("num8",         1,   1, 0x07, "digit 8"),
    ("num9",         1,   1, 0x08, "digit 9"),
    ("num0",         1,   1, 0x09, "digit 0"),
    ("num11",        1,   1, 0x0a, "digit 11 / +10"),
    ("num12",        1,   1, 0x0b, "digit 12 / +20"),
    ("dot",          2, 151, 0x1d, "decimal dot for channel entry"),
    # volume / channel
    ("volume-up",    1,   1, 0x12, "volume up"),
    ("volume-down",  1,   1, 0x13, "volume down"),
    ("mute",         1,   1, 0x14, "mute toggle"),
    ("channel-up",   1,   1, 0x10, "channel up"),
    ("channel-down", 1,   1, 0x11, "channel down"),
    # cursor / navigation (standard family)
    ("up",           1,   1, 0x74, "cursor up   [live-verified]"),
    ("down",         1,   1, 0x75, "cursor down"),
    ("left",         1,   1, 0x34, "cursor left"),
    ("right",        1,   1, 0x33, "cursor right"),
    ("confirm",      1,   1, 0x65, "confirm / enter   [live-verified]"),
    ("home",         1,   1, 0x60, "HOME menu"),
    ("exit",         1,   1, 0x63, "EXIT"),
    ("back",         2, 151, 0x23, "back / return"),
    ("options",      2, 151, 0x36, "OPTIONS button"),
    ("help",         2, 196, 0x4d, "help"),
    # color buttons -- manufacturer=2, device=0x97, CONFIRMED by the
    # EX725's own getRemoteCommandList (2026-09-13).
    ("red",          2, 151, 0x25, "red color button   [TV-table-verified]"),
    ("green",        2, 151, 0x26, "green color button   [TV-table-verified]"),
    ("yellow",       2, 151, 0x27, "yellow color button   [TV-table-verified]"),
    ("blue",         2, 151, 0x24, "blue color button   [TV-table-verified]"),
    # color buttons, device=0x9c -- the variant Sony's Android-generation
    # table (pro-bravia.sony.net) uses.  This 2011 chassis uses 0x97 above;
    # the 2026-09-13 "live note" that claimed 0x9c for this set was wrong.
    ("red-alt",      2, 156, 0x25, "red, Android-gen device 0x9c"),
    ("green-alt",    2, 156, 0x26, "green, Android-gen device 0x9c"),
    ("yellow-alt",   2, 156, 0x27, "yellow, Android-gen device 0x9c"),
    ("blue-alt",     2, 156, 0x24, "blue, Android-gen device 0x9c"),
    # media transport -- manufacturer=2, device=0x97 family
    ("play",         2, 151, 0x1a, "play"),
    ("pause",        2, 151, 0x19, "pause"),
    ("stop",         2, 151, 0x18, "stop"),
    ("prev",         2, 151, 0x3c, "previous track"),
    ("next",         2, 151, 0x3d, "next track"),
    # media transport extras (EX725's own table)
    ("rewind",       2, 151, 0x1b, "rewind"),
    ("forward",      2, 151, 0x1c, "fast forward"),
    ("replay",       2, 151, 0x79, "replay (jump back)"),
    ("advance",      2, 151, 0x78, "advance (jump forward)"),
    ("eject",        2, 151, 0x48, "eject"),
    ("rec",          2, 151, 0x20, "record"),
    ("ten-key",      2, 151, 0x0c, "ten-key keypad toggle"),
    # tuner-family and service keys (EX725's own table)
    ("analog",       2, 119, 0x0d, "analog tuner"),
    ("digital",      2, 151, 0x32, "digital tuner"),
    ("bs",           2, 151, 0x2c, "BS (broadcast satellite) band"),
    ("cs",           2, 151, 0x2b, "CS (communication satellite) band"),
    ("bscs",         2, 151, 0x10, "BS/CS toggle"),
    ("ddata",        2, 151, 0x15, "data broadcast (BML/Ddata) toggle"),
    ("mode3d",       2, 119, 0x4d, "3D mode toggle"),
    ("my-epg",       2, 119, 0x6b, "My EPG"),
    ("write-chapter", 2, 119, 0x6c, "write chapter mark (recording)"),
    ("delete-video", 2, 119, 0x1f, "delete recorded video"),
    ("easy-startup", 2, 119, 0x6a, "easy setup (initial setup wizard)"),
    # MDF variant -- manufacturer=2, device=26
    ("hdmi1",        2,  26, 0x5a, "HDMI input 1"),
    ("hdmi2",        2,  26, 0x5b, "HDMI input 2"),
    ("hdmi3",        2,  26, 0x5c, "HDMI input 3"),
    ("hdmi4",        2,  26, 0x5d, "HDMI input 4"),
    ("sync-menu",    2,  26, 0x58, "SYNC MENU"),
    ("top-menu",     2,  26, 0x60, "BD/DVD top menu"),
    ("popup-menu",   2,  26, 0x61, "BD/DVD popup menu"),
    ("internet-widgets", 2, 26, 0x7a, "Internet Widgets"),
    ("internet-video", 2, 26, 0x79, "Internet Video / video portal"),
    ("scene-select", 2,  26, 0x78, "Scene Select"),
    ("imanual",      2,  26, 0x7b, "iManual (on-screen manual)"),
    ("applicast",    2,  26, 0x6f, "AppliCast widgets"),
    ("actvila",      2,  26, 0x72, "acTVila video service"),
    ("track-id",     2,  26, 0x7e, "TrackID"),
    ("one-touch-time-rec", 2, 26, 0x64, "one-touch timed record"),
    ("one-touch-view", 2, 26, 0x65, "one-touch view"),
    ("one-touch-rec", 2, 26, 0x62, "one-touch record"),
    ("one-touch-rec-stop", 2, 26, 0x63, "stop one-touch record"),
]

KEY_TABLE = {name: (manu, dev, func, desc)
             for name, manu, dev, func, desc in _KEY_TABLE_RAW}

# Convenience aliases (normalized, lowercase, hyphens).
KEY_ALIASES = {
    "vol-up": "volume-up", "vol+": "volume-up", "volume+": "volume-up",
    "vol-down": "volume-down", "vol-": "volume-down", "volume-": "volume-down",
    "ch-up": "channel-up", "ch+": "channel-up",
    "ch-down": "channel-down", "ch-": "channel-down",
    "standby": "power", "power-toggle": "power",
    "enter": "confirm", "ok": "confirm", "select": "confirm",
    "return": "back",
    "cursor-up": "up", "cursor-down": "down",
    "cursor-left": "left", "cursor-right": "right",
    "cc": "closed-caption", "subtitle-cycle": "subtitle",
    "input-select": "input",
    "hdmi-1": "hdmi1", "hdmi-2": "hdmi2", "hdmi-3": "hdmi3", "hdmi-4": "hdmi4",
    "digit-1": "num1", "digit-2": "num2", "digit-3": "num3", "digit-4": "num4",
    "digit-5": "num5", "digit-6": "num6", "digit-7": "num7", "digit-8": "num8",
    "digit-9": "num9", "digit-0": "num0",
    "0": "num0", "1": "num1", "2": "num2", "3": "num3", "4": "num4",
    "5": "num5", "6": "num6", "7": "num7", "8": "num8", "9": "num9",
}

# Published base64 constants that derived codes MUST reproduce.  Sources:
# live-verified 2026-09-13 (up/power/confirm), Sony official IRCC table,
# and SNIFF.md TV-served remoteCommandList.
PUBLISHED_SPOT_CHECKS = {
    "up":        "AAAAAQAAAAEAAAB0Aw==",
    "power":     "AAAAAQAAAAEAAAAVAw==",
    "confirm":   "AAAAAQAAAAEAAABlAw==",
    "down":      "AAAAAQAAAAEAAAB1Aw==",
    "left":      "AAAAAQAAAAEAAAA0Aw==",
    "right":     "AAAAAQAAAAEAAAAzAw==",
    "home":      "AAAAAQAAAAEAAABgAw==",
    "exit":      "AAAAAQAAAAEAAABjAw==",
    "display":   "AAAAAQAAAAEAAAA6Aw==",
    "volume-up": "AAAAAQAAAAEAAAASAw==",
    "volume-down": "AAAAAQAAAAEAAAATAw==",
    "mute":      "AAAAAQAAAAEAAAAUAw==",
    "channel-up": "AAAAAQAAAAEAAAAQAw==",
    "channel-down": "AAAAAQAAAAEAAAARAw==",
    "num5":      "AAAAAQAAAAEAAAAEAw==",
    "input":     "AAAAAQAAAAEAAAAlAw==",
    "hdmi1":     "AAAAAgAAABoAAABaAw==",
    "hdmi2":     "AAAAAgAAABoAAABbAw==",
    "hdmi3":     "AAAAAgAAABoAAABcAw==",
    "hdmi4":     "AAAAAgAAABoAAABdAw==",
    "back":      "AAAAAgAAAJcAAAAjAw==",
    "options":   "AAAAAgAAAJcAAAA2Aw==",
    "red":       "AAAAAgAAAJcAAAAlAw==",
    "green":     "AAAAAgAAAJcAAAAmAw==",
    "yellow":    "AAAAAgAAAJcAAAAnAw==",
    "blue":      "AAAAAgAAAJcAAAAkAw==",
}


# --------------------------------------------------------------------------
# Sequence library
#
# Each sequence: name -> (steps, description) where steps is a list of
# (key_name, delay_after_seconds_or_None).  None means use --delay.
# DANGEROUS sequences change persistent service state and are guarded by
# BOTH --allow-service-mode AND an interactive y/N confirmation.
# --------------------------------------------------------------------------

SEQUENCES = {
    "nav-up":    ([("up", None)], "cursor up"),
    "nav-down":  ([("down", None)], "cursor down"),
    "nav-left":  ([("left", None)], "cursor left"),
    "nav-right": ([("right", None)], "cursor right"),
    "vol-up":    ([("volume-up", None)], "volume up one step"),
    "vol-down":  ([("volume-down", None)], "volume down one step"),
    "mute-toggle": ([("mute", None)], "IRCC mute toggle"),
    "ch-up":     ([("channel-up", None)], "channel up"),
    "ch-down":   ([("channel-down", None)], "channel down"),
    "home":      ([("home", None)], "HOME menu"),
    "standby":   ([("power", None)], "standby press (power toggle)"),
    # AZ3F service manual entry sequences.  Entered from standby:
    #   DISPLAY -> Ch 5 -> Vol+ -> POWER   (service mode)
    #   DISPLAY -> Ch 5 -> Vol- -> POWER   (self diagnostic)
    # VolumeUp+Power writes to NVM (persistent service state).
    "service-mode-entry": ([
        ("power", 5.0),        # standby press, then let the set settle
        ("display", 0.6),
        ("num5", 0.6),
        ("volume-up", 0.6),
        ("power", None),
    ], "AZ3F service manual: standby -> DISPLAY -> Ch 5 -> VOL+ -> POWER "
       "(enters factory service mode; writes NVM).  LIVE-TESTED NEGATIVE "
       "on the EX725 2026-09-13: does NOT arm via IRCC even with verified "
       "codes and tight pacing -- the physical remote is required; the "
       "set just boots normally.  Kept for documentation and for the day "
       "a root shell can inject at the IR/standby layer."),
    "self-diagnostic": ([
        ("power", 5.0),
        ("display", 0.6),
        ("num5", 0.6),
        ("volume-down", 0.6),
        ("power", None),
    ], "AZ3F service manual: standby -> DISPLAY -> Ch 5 -> VOL- -> POWER "
       "(enters self-diagnostic screen; changes service state)"),
}

DANGEROUS_SEQUENCES = {"service-mode-entry", "self-diagnostic"}


# --------------------------------------------------------------------------
# Code construction / resolution
# --------------------------------------------------------------------------

def build_ircc_code(manufacturer, device, function):
    """Return the base64 IRCCCode for a key.

    Derived, never pasted: base64(struct.pack('>IIIB', manu, dev, func, 0x03)).
    """
    payload = struct.pack(">IIIB", manufacturer, device, function, IRCC_TAIL_BYTE)
    return base64.b64encode(payload).decode("ascii")


def decode_ircc_code(code_b64):
    """Decode a base64 IRCCCode; return (manufacturer, device, function).

    Raises ValueError unless it is exactly 13 bytes with tail byte 0x03.
    """
    try:
        raw = base64.b64decode(code_b64, validate=True)
    except Exception as exc:
        raise ValueError("not valid base64: %r" % (code_b64,))
    if len(raw) != 13:
        raise ValueError("IRCCCode must decode to 13 bytes, got %d" % len(raw))
    if raw[12] != IRCC_TAIL_BYTE:
        raise ValueError("IRCCCode tail byte must be 0x03, got 0x%02x" % raw[12])
    manu, dev, func = struct.unpack(">III", raw[:12])
    return manu, dev, func


def normalize_name(name):
    return name.strip().lower().replace("_", "-")


def lookup_key(name):
    """Resolve a table/alias name to (manu, dev, func); None if unknown."""
    key = normalize_name(name)
    if key in KEY_TABLE:
        manu, dev, func, _ = KEY_TABLE[key]
        return manu, dev, func
    if key in KEY_ALIASES:
        manu, dev, func, _ = KEY_TABLE[KEY_ALIASES[key]]
        return manu, dev, func
    return None


def resolve_key_spec(spec, default_manu=1, default_dev=1):
    """Resolve a CLI key spec: table/alias name, hex function, or base64.

    Returns (manu, dev, func).  Raises ValueError with a helpful message.
    """
    spec = spec.strip()
    triple = lookup_key(spec)
    if triple is not None:
        return triple
    # raw function hex (0xNN or NN) -> standard family unless overridden
    if re.fullmatch(r"0x[0-9a-fA-F]{1,8}", spec):
        func = int(spec, 16)
    elif re.fullmatch(r"[0-9a-fA-F]{1,2}", spec):
        func = int(spec, 16)
    else:
        # full base64 IRCCCode constant
        try:
            return decode_ircc_code(spec)
        except ValueError:
            raise ValueError(
                "unknown key %r (not a table name, alias, hex function, or "
                "13-byte base64 IRCCCode).  Run 'codes' to list keys." % spec)
    if not 0 <= func <= 0xFFFFFFFF:
        raise ValueError("function out of range: %r" % spec)
    return default_manu, default_dev, func


# --------------------------------------------------------------------------
# HTTP transport (stdlib http.client; only the named host:port is contacted)
# --------------------------------------------------------------------------

def http_request(host, port, method, path, body=None, headers=None, timeout=DEFAULT_TIMEOUT):
    """Perform one HTTP request.  Returns (status, text)."""
    conn = http.client.HTTPConnection(host, port, timeout=timeout)
    try:
        conn.request(method, path, body=body, headers=headers or {})
        resp = conn.getresponse()
        data = resp.read()
        return resp.status, data.decode("utf-8", "replace")
    finally:
        conn.close()


def is_soap_fault(text):
    return ("Fault" in text) or ("errorCode" in text)


def send_ircc(host, port, code_b64, timeout=DEFAULT_TIMEOUT, quiet=False):
    """POST one X_SendIRCC SOAP envelope.  Prints status/body on faults."""
    body = SOAP_ENVELOPE.format(code=code_b64)
    headers = {
        "Content-Type": "text/xml; charset=UTF-8",
        "SOAPAction": SOAP_ACTION,
    }
    try:
        status, text = http_request(host, port, "POST", IRCC_PATH,
                                    body=body, headers=headers, timeout=timeout)
    except (socket.error, OSError, http.client.HTTPException) as exc:
        print("error: %s:%s %s: %s" % (host, port, IRCC_PATH, exc),
              file=sys.stderr)
        return False
    if not quiet:
        print("IRCC %s: HTTP %d" % (code_b64, status))
    if status != 200 or is_soap_fault(text):
        # SOAP faults show errorCode 800 etc. -- print the whole body.
        print("--- response body ---")
        print(text.rstrip())
        print("---------------------")
        return False
    return True


def cers_command(host, port, path, timeout=DEFAULT_TIMEOUT):
    """GET a CERS URL-type command (e.g. MuteOn/MuteOff); no auth needed."""
    try:
        status, text = http_request(host, port, "GET", path, timeout=timeout)
    except (socket.error, OSError, http.client.HTTPException) as exc:
        print("error: %s:%s %s: %s" % (host, port, path, exc), file=sys.stderr)
        return False
    print("GET %s: HTTP %d" % (path, status))
    if status != 200:
        print("--- response body ---")
        print(text.rstrip())
        print("---------------------")
        return False
    return True


# --------------------------------------------------------------------------
# Safety guards
# --------------------------------------------------------------------------

def check_host(host):
    """Refuse to drive the workstation's monitor by accident."""
    if host == MONITOR_HOST:
        print(
            "WARNING: %s is the workstation's monitor (KDL-46HX855).\n"
            "         The default target is the expendable EX725 at %s.\n"
            "         Keypresses will change what is on your screen." %
            (MONITOR_HOST, DEFAULT_HOST))
        if not sys.stdin.isatty():
            print("Refused: explicit confirmation needed for %s "
                  "(stdin is not a TTY)." % MONITOR_HOST, file=sys.stderr)
            sys.exit(2)
        try:
            answer = input("Type 'yes' to drive the monitor anyway: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            answer = ""
        if answer != "yes":
            print("Aborted.", file=sys.stderr)
            sys.exit(2)


def guard_dangerous_sequence(name):
    """Guard service-mode sequences behind --allow-service-mode + y/N.

    The confirmation must be genuinely interactive: it is refused outright
    when stdin is not a TTY, so 'echo y |' / piped scripts cannot bypass
    it the way they could a bare input() read.
    """
    if not sys.stdin.isatty():
        print("Refused: sequence '%s' needs an INTERACTIVE y/N confirmation "
              "(stdin is not a TTY)." % name, file=sys.stderr)
        sys.exit(2)
    description = SEQUENCES[name][1]
    print(
        "\nDANGER: sequence '%s' changes PERSISTENT service state.\n"
        "  %s\n"
        "  Entering service mode via VOL+ + POWER writes to NVM; wrong\n"
        "  values can require a full factory reset to undo.\n"
        "  Target set must already be at hand: this runs on the TV at the\n"
        "  host you named.\n" % (name, description))
    print("This is refused by default.  It requires BOTH:")
    print("  1. --allow-service-mode on the command line, and")
    print("  2. an interactive y/N confirmation.\n")
    try:
        answer = input("Send '%s' anyway? [y/N] " % name).strip().lower()
    except (EOFError, KeyboardInterrupt):
        answer = ""
    if answer not in ("y", "yes"):
        print("Refused.", file=sys.stderr)
        sys.exit(2)
    print("Proceeding with '%s'.\n" % name)


# --------------------------------------------------------------------------
# Command implementations
# --------------------------------------------------------------------------

def cmd_send(args):
    host, port = args.host, args.port
    check_host(host)
    try:
        manu, dev, func = resolve_key_spec(args.key, args.manufacturer or 1,
                                          args.device or 1)
    except ValueError as exc:
        print("error: %s" % exc, file=sys.stderr)
        sys.exit(2)
    code = build_ircc_code(manu, dev, func)
    print("key '%s' -> manufacturer=%d device=%d function=0x%02x  [%s]"
          % (args.key, manu, dev, func, code))
    ok = send_ircc(host, port, code, timeout=args.timeout)
    sys.exit(0 if ok else 1)


def parse_seq_steps(spec):
    """Parse a seq argument into [(key_spec, delay_or_None), ...].

    Accepts either one library sequence name, or a comma-separated list of
    key names with optional per-key delay: 'name', 'name:0.5'.
    """
    name = normalize_name(spec)
    if name in SEQUENCES:
        return name, list(SEQUENCES[name][0])
    steps = []
    for item in spec.split(","):
        item = item.strip()
        if not item:
            raise ValueError("empty step in sequence %r" % spec)
        delay = None
        if ":" in item:
            key_part, _, delay_part = item.rpartition(":")
            try:
                delay = float(delay_part)
                if not math.isfinite(delay) or delay < 0:
                    raise ValueError
                item = key_part
            except ValueError:
                # not a usable delay suffix; treat the whole item as the key
                delay = None
        # Validate the step NOW, before any key is sent: a typo must
        # never half-execute a sequence on the TV.
        try:
            resolve_key_spec(item)
        except ValueError as exc:
            raise ValueError("bad step %r in sequence %r: %s"
                             % (item, spec, exc))
        steps.append((item, delay))
    return None, steps


def cmd_seq(args):
    host, port, delay = args.host, args.port, args.delay
    check_host(host)
    try:
        seq_name, steps = parse_seq_steps(args.keys)
    except ValueError as exc:
        print("error: %s" % exc, file=sys.stderr)
        sys.exit(2)

    if seq_name in DANGEROUS_SEQUENCES:
        if not args.allow_service_mode:
            print(
                "Refused: sequence '%s' is a service-mode sequence.\n"
                "It changes persistent service state (VolumeUp+Power writes\n"
                "to NVM) and is disabled by default.  Re-run with\n"
                "--allow-service-mode and confirm interactively if you\n"
                "really mean it." % seq_name, file=sys.stderr)
            sys.exit(2)
        guard_dangerous_sequence(seq_name)

    # Resolve and build EVERY step before the first keypress.  A key that
    # fails to resolve mid-sequence must never leave the TV partway into a
    # multi-key state (worst case: half a service-mode entry).
    try:
        plan = []
        for key_spec, step_delay in steps:
            manu, dev, func = resolve_key_spec(key_spec)
            plan.append((key_spec, build_ircc_code(manu, dev, func),
                         manu, dev, func, step_delay))
    except ValueError as exc:
        print("error: %s" % exc, file=sys.stderr)
        sys.exit(2)

    print("sequence: %s" % (seq_name or args.keys))
    ok = True
    for i, (key_spec, code, manu, dev, func, step_delay) in enumerate(plan):
        print("[%d/%d] %-12s manu=%d dev=%d func=0x%02x"
              % (i + 1, len(plan), key_spec, manu, dev, func))
        if not send_ircc(host, port, code, timeout=args.timeout):
            ok = False
            break
        if i + 1 < len(plan):
            pause = step_delay if step_delay is not None else delay
            time.sleep(pause)
    print("sequence %s" % ("completed." if ok else "ABORTED on failure."))
    sys.exit(0 if ok else 1)


def cmd_mute(args):
    check_host(args.host)
    ok = cers_command(args.host, args.port, CERS_MUTE_ON, timeout=args.timeout)
    sys.exit(0 if ok else 1)


def cmd_unmute(args):
    check_host(args.host)
    ok = cers_command(args.host, args.port, CERS_MUTE_OFF, timeout=args.timeout)
    sys.exit(0 if ok else 1)


def cmd_info(args):
    check_host(args.host)
    try:
        status, text = http_request(args.host, args.port, "GET",
                                    CERS_SYSTEM_INFO, timeout=args.timeout)
    except (socket.error, OSError, http.client.HTTPException) as exc:
        print("error: %s:%s %s: %s"
              % (args.host, args.port, CERS_SYSTEM_INFO, exc), file=sys.stderr)
        sys.exit(1)
    print("GET %s: HTTP %d" % (CERS_SYSTEM_INFO, status))
    print(text.rstrip())
    sys.exit(0 if status == 200 else 1)


def cmd_codes(args):
    print("Named IRCC keys (all base64 derived from "
          "struct.pack('>IIIB', manu, dev, func, 0x03)):\n")
    current_family = None
    for name, manu, dev, func, desc in _KEY_TABLE_RAW:
        code = build_ircc_code(manu, dev, func)
        family = "manufacturer=%d device=%d" % (manu, dev)
        if family != current_family:
            print("-- %s --" % family)
            current_family = family
        print("  %-14s func=0x%02x  %-28s # %s" % (name, func, code, desc))
    print("\nAliases: %s" % ", ".join(sorted(KEY_ALIASES)))
    print("\nSequences (seq <name>, or comma-separated keys with :delay):")
    for name, (steps, desc) in SEQUENCES.items():
        flag = "  [DANGEROUS: needs --allow-service-mode + y/N]" \
            if name in DANGEROUS_SEQUENCES else ""
        keys = ", ".join("%s%s" % (k, "" if d is None else ":%gs" % d)
                         for k, d in steps)
        print("  %-20s %s\n      %-58s # %s%s" % (name, keys, "", desc, flag))
    sys.exit(0)


def cmd_selftest(args):
    failures = []

    print("1. every named code builds/decodes a 13-byte struct and "
          "round-trips:")
    for name, manu, dev, func, desc in _KEY_TABLE_RAW:
        code = build_ircc_code(manu, dev, func)
        try:
            m, d, f = decode_ircc_code(code)
        except ValueError as exc:
            failures.append("%s: %s" % (name, exc))
            print("  FAIL %-14s %s" % (name, exc))
            continue
        assert struct.calcsize(">IIIB") == 13, "struct layout must be 13 bytes"
        if (m, d, f) != (manu, dev, func):
            failures.append("%s: round-trip mismatch %r != %r"
                            % (name, (m, d, f), (manu, dev, func)))
            print("  FAIL %-14s round-trip mismatch" % name)
            continue
        print("  ok   %-14s words: manufacturer=%-4d device=%-4d "
              "function=0x%02x  %s" % (name, m, d, f, code))

    print("\n2. derived codes reproduce published/verified constants:")
    for name, published in PUBLISHED_SPOT_CHECKS.items():
        manu, dev, func, _ = KEY_TABLE[name]
        derived = build_ircc_code(manu, dev, func)
        if derived == published:
            print("  ok   %-14s == %s" % (name, published))
        else:
            failures.append("%s: derived %s != published %s"
                            % (name, derived, published))
            print("  FAIL %-14s derived %s != published %s"
                  % (name, derived, published))

    print("\n3. aliases resolve to table entries:")
    for alias, target in sorted(KEY_ALIASES.items()):
        if target not in KEY_TABLE:
            failures.append("alias %s -> %s missing from KEY_TABLE"
                            % (alias, target))
            print("  FAIL %-14s -> %s missing" % (alias, target))
        else:
            print("  ok   %-14s -> %s" % (alias, target))

    print("\n4. sequences reference valid keys, dangerous ones are guarded:")
    for name, (steps, _desc) in SEQUENCES.items():
        for key_spec, _delay in steps:
            try:
                resolve_key_spec(key_spec)
            except ValueError as exc:
                failures.append("sequence %s: bad step %r (%s)"
                                % (name, key_spec, exc))
                print("  FAIL %-20s step %r" % (name, key_spec))
                continue
        guard = name in DANGEROUS_SEQUENCES
        expect_guard = name in ("service-mode-entry", "self-diagnostic")
        if guard != expect_guard:
            failures.append("sequence %s guard flag wrong" % name)
            print("  FAIL %-20s guard flag wrong" % name)
        else:
            print("  ok   %-20s %d steps%s"
                  % (name, len(steps),
                     "  [guarded]" if guard else ""))
    if not DANGEROUS_SEQUENCES <= set(SEQUENCES):
        failures.append("DANGEROUS_SEQUENCES not a subset of SEQUENCES")
        print("  FAIL dangerous set consistency")
    else:
        print("  ok   dangerous set ⊆ sequences: %s"
              % ", ".join(sorted(DANGEROUS_SEQUENCES)))

    print("\n5. target policy:")
    if DEFAULT_HOST == "192.168.0.22" and DEFAULT_HOST != MONITOR_HOST \
            and MONITOR_HOST == "192.168.0.21":
        print("  ok   default host is %s (expendable EX725); "
              "%s (monitor) is never a default and needs confirmation."
              % (DEFAULT_HOST, MONITOR_HOST))
    else:
        failures.append("default host policy violated")
        print("  FAIL default host policy")
    if DEFAULT_PORT == 80 and DEFAULT_DELAY == 1.0 and DEFAULT_TIMEOUT == 5.0:
        print("  ok   port=%d delay=%.1f timeout=%.1f"
              % (DEFAULT_PORT, DEFAULT_DELAY, DEFAULT_TIMEOUT))
    else:
        failures.append("default port/delay/timeout wrong")
        print("  FAIL defaults")

    print("\n%d named codes, %d aliases, %d sequences, %d spot-checks."
          % (len(KEY_TABLE), len(KEY_ALIASES), len(SEQUENCES),
             len(PUBLISHED_SPOT_CHECKS)))
    if failures:
        print("SELFTEST FAILED: %d failure(s)" % len(failures))
        for f in failures:
            print("  - %s" % f)
        sys.exit(1)
    print("SELFTEST PASSED")


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _add_common_opts(parser, sub=False):
    """Common options on the main parser and each subparser.

    On subparsers the defaults are SUPPRESS so a subcommand flag wins, a
    global flag is inherited, and the documented default applies only when
    neither position was used.
    """
    d = argparse.SUPPRESS if sub else None
    parser.add_argument(
        "--host", default=d, metavar="IP",
        help="TV IPv4 address (default %s, the expendable EX725 test target; "
             "%s is the workstation monitor and never a default)"
             % (DEFAULT_HOST, MONITOR_HOST))
    parser.add_argument(
        "--port", type=int, default=d, metavar="N",
        help="HTTP port (default %d; port 52323 also serves /IRCC on the "
             "HX855 but returns 501 on the EX725)" % DEFAULT_PORT)
    parser.add_argument(
        "--delay", type=float, default=d, metavar="SEC",
        help="delay between sequence keys in seconds (default %.1f; TV IR "
             "receivers need spacing)" % DEFAULT_DELAY)
    parser.add_argument(
        "--timeout", type=float, default=d, metavar="SEC",
        help="per-request timeout in seconds (default %.1f)" % DEFAULT_TIMEOUT)
    parser.add_argument(
        "--allow-service-mode", action="store_true", default=d,
        help="unlock service-mode sequences (still requires an "
             "interactive y/N confirmation)")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="bravia_ircc.py",
        description="No-registration IRCC remote driver for the owner's Sony "
                    "BRAVIA Linux TVs (right-to-repair, own hardware, own "
                    "LAN).  Never scans; contacts only the named host:port.",
        epilog="Examples:  %(prog)s send power | %(prog)s send 0x74 | "
               "%(prog)s seq vol-up:0.5,vol-up:0.5 | %(prog)s mute | "
               "%(prog)s info | %(prog)s codes | %(prog)s selftest")
    _add_common_opts(parser)

    sub = parser.add_subparsers(dest="command", metavar="command")
    sub.required = True

    p = sub.add_parser("send", help="send one key by name or raw function hex")
    _add_common_opts(p, sub=True)
    p.add_argument("key", metavar="KEY",
                   help="key name/alias, hex function (e.g. 0x74), or full "
                        "base64 IRCCCode")
    p.add_argument("--manufacturer", type=int, default=1,
                   help="manufacturer word for raw hex functions (default 1)")
    p.add_argument("--device", type=int, default=1,
                   help="device word for raw hex functions (default 1)")
    p.set_defaults(func=cmd_send)

    p = sub.add_parser("seq", help="send a key sequence")
    _add_common_opts(p, sub=True)
    p.add_argument("keys", metavar="SEQ",
                   help="sequence name ('nav-up', 'vol-up', ...) or "
                        "comma-separated keys with optional per-key delay "
                        "('up,confirm:0.5,down')")
    p.set_defaults(func=cmd_seq)

    p = sub.add_parser("mute", help="CERS MuteOn (GET, no auth)")
    _add_common_opts(p, sub=True)
    p.set_defaults(func=cmd_mute)

    p = sub.add_parser("unmute", help="CERS MuteOff (GET, no auth)")
    _add_common_opts(p, sub=True)
    p.set_defaults(func=cmd_unmute)

    p = sub.add_parser("info", help="GET /cers/api/getSystemInformation (XML)")
    _add_common_opts(p, sub=True)
    p.set_defaults(func=cmd_info)

    p = sub.add_parser("codes", help="list the named-key table and sequences")
    _add_common_opts(p, sub=True)
    p.set_defaults(func=cmd_codes)

    p = sub.add_parser("selftest",
                       help="offline self-test: assert every named code "
                            "decodes to 13 bytes; prints the words")
    _add_common_opts(p, sub=True)
    p.set_defaults(func=cmd_selftest)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    # Resolve defaults (works whether flags were given globally or after
    # the subcommand; subcommand position wins).
    args.host = getattr(args, "host", None) or DEFAULT_HOST
    args.port = getattr(args, "port", None) or DEFAULT_PORT
    args.delay = getattr(args, "delay", None) or DEFAULT_DELAY
    args.timeout = getattr(args, "timeout", None) or DEFAULT_TIMEOUT
    args.allow_service_mode = bool(getattr(args, "allow_service_mode", None))

    # Non-finite pacing (e.g. --delay inf / nan) would hang the script
    # mid-sequence with the TV left in whatever state the last key put it.
    for opt in ("delay", "timeout"):
        value = getattr(args, opt)
        if not math.isfinite(value) or value < 0:
            parser.error("--%s must be a finite, non-negative number of "
                         "seconds (got %r)" % (opt, value))

    args.func(args)


if __name__ == "__main__":
    main()