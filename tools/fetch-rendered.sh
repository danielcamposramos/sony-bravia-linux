#!/usr/bin/env bash
# fetch-rendered.sh — fetch a JavaScript-rendered page through the local
# browserless/chromium container, for sources that plain curl cannot read.
#
# Why this exists: several sources this project depends on are JS-rendered
# (Sony's RefLib document viewer is a Blazor SPA; some archive views need
# scripting). curl gets an app shell; a real engine gets the content.
#
# What it is NOT for: defeating anti-bot controls. Sony's WAF deliberately
# blocks non-browser clients and answers them with HTTP 200 plus an
# "Access Denied" body. Default browserless is blocked the same way, and
# that is where this tool stops — escalating to stealth plugins or
# fingerprint spoofing to get past a WAF is circumventing an access
# control, whatever the intent. If a source blocks automation, open it in
# your own browser instead.
#
# Usage:
#   tools/fetch-rendered.sh <url> [output-file] [wait-selector]
#
# Env:
#   BROWSERLESS_URL    default http://localhost:3100
#   BROWSERLESS_TOKEN  required (see the container's TOKEN env var)
#
# Exit codes: 0 ok · 2 usage · 3 container unreachable · 4 fetch failed
#             5 blocked (content looks like an anti-bot page)

set -euo pipefail

URL="${1:-}"
OUT="${2:--}"
WAIT_SEL="${3:-}"
BL="${BROWSERLESS_URL:-http://localhost:3100}"
TOKEN="${BROWSERLESS_TOKEN:-}"

if [ -z "$URL" ]; then
    echo "usage: $0 <url> [output-file] [wait-selector]" >&2
    exit 2
fi
if [ -z "$TOKEN" ]; then
    echo "error: BROWSERLESS_TOKEN is not set" >&2
    echo "  hint: docker inspect browserless --format '{{range .Config.Env}}{{println .}}{{end}}' | grep TOKEN" >&2
    exit 2
fi

if ! curl -s -o /dev/null --max-time 5 "$BL/" ; then
    echo "error: browserless not reachable at $BL" >&2
    echo "  hint: docker ps --filter name=browserless" >&2
    exit 3
fi

payload=$(python3 - "$URL" "$WAIT_SEL" <<'PY'
import json, sys
url, sel = sys.argv[1], sys.argv[2]
body = {"url": url,
        "gotoOptions": {"waitUntil": "networkidle2", "timeout": 60000}}
if sel:
    body["waitForSelector"] = {"selector": sel, "timeout": 30000}
print(json.dumps(body))
PY
)

tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT

code=$(curl -s -X POST "$BL/content?token=$TOKEN" \
        -H 'Content-Type: application/json' \
        --max-time 120 -d "$payload" -o "$tmp" -w '%{http_code}')

if [ "$code" != "200" ]; then
    echo "error: browserless returned HTTP $code" >&2
    head -c 300 "$tmp" >&2; echo >&2
    exit 4
fi

# A WAF block often arrives as HTTP 200 with a denial body — check content,
# never the status code. This is the trap that made an earlier pass record a
# perfectly good Sony URL as dead.
if grep -qiE '<title>[^<]*(access denied|forbidden|attention required|just a moment)' "$tmp"; then
    echo "blocked: the site served an anti-bot page (HTTP 200, denial body)" >&2
    echo "  $(grep -oiE '<title>[^<]*</title>' "$tmp" | head -1)" >&2
    echo "  open this URL in your own browser instead; do not escalate." >&2
    exit 5
fi

if [ "$OUT" = "-" ]; then
    cat "$tmp"
else
    cp "$tmp" "$OUT"
    echo "saved $(wc -c < "$OUT") bytes to $OUT" >&2
fi
