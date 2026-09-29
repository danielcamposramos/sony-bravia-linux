


from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tomllib
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import ledger


SCHEMA = 1
DEFAULT_MANIFEST = "data/evidence-ledger/federation.toml"
DEFAULT_VIEW = "docs/reference/evidence-ledger/pointers.md"
REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
REF = re.compile(r"^[A-Za-z0-9_./-]+$")
REASONS = {"SUPPORTED", "UNTESTED", "CORRECTED", "SUPERSEDED", "STALE"}


def require(pointer: dict, field: str, expected=None):
    value = pointer.get(field)
    if value in (None, "", []):
        ledger.fail(f"{pointer.get('id', '<unknown>')}: missing {field}")
    if expected is not None and not isinstance(value, expected):
        ledger.fail(f"{pointer.get('id', '<unknown>')}: {field} has wrong type")
    return value


def parse_toml_text(text: str, label: str) -> dict:
    try:
        return tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise ledger.LedgerError(f"{label}: {exc}") from exc


def fetch_text(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "signal-ledger-federation/1"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read().decode("utf-8")
    except (OSError, UnicodeError, urllib.error.HTTPError) as exc:
        raise ledger.LedgerError(f"cannot fetch {url}: {exc}") from exc


def safe_remote_path(value: str, label: str) -> str:
    if not isinstance(value, str) or not value:
        ledger.fail(f"{label}: path must be a non-empty string")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        ledger.fail(f"{label}: unsafe remote path {value}")
    return path.as_posix()


def raw_url(repository: str, ref: str, path: str) -> str:
    if not REPOSITORY.fullmatch(repository):
        ledger.fail(f"invalid upstream repository {repository}")
    if not REF.fullmatch(ref) or ".." in PurePosixPath(ref).parts:
        ledger.fail(f"invalid upstream ref {ref}")
    safe_path = safe_remote_path(path, repository)
    encoded_ref = urllib.parse.quote(ref, safe="/")
    encoded_path = urllib.parse.quote(safe_path, safe="/")
    return f"https://raw.githubusercontent.com/{repository}/{encoded_ref}/{encoded_path}"


def validate_pointer(pointer: dict) -> None:
    pointer_id = require(pointer, "id", str)
    if pointer.get("schema") != SCHEMA:
        ledger.fail(f"{pointer_id}: schema must be {SCHEMA}")
    if not ledger.CLAIM_ID.fullmatch(pointer_id):
        ledger.fail(f"{pointer_id}: pointer ID must use uppercase ASCII letters, digits and hyphens")
    require(pointer, "purpose", str)
    repository = require(pointer, "upstream_repository", str)
    ref = require(pointer, "upstream_ref", str)
    safe_remote_path(require(pointer, "upstream_manifest", str), pointer_id)
    claim_id = require(pointer, "claim_id", str)
    if not ledger.CLAIM_ID.fullmatch(claim_id):
        ledger.fail(f"{pointer_id}: non-canonical claim ID")
    claim_hash = require(pointer, "claim_sha256", str)
    if len(claim_hash) != 64 or any(char not in "0123456789abcdef" for char in claim_hash):
        ledger.fail(f"{pointer_id}: claim_sha256 must be lowercase SHA-256")
    reason = require(pointer, "expected_reason", str)
    if reason not in REASONS:
        ledger.fail(f"{pointer_id}: unknown expected_reason {reason}")
    if not isinstance(pointer.get("accept_superseded"), bool):
        ledger.fail(f"{pointer_id}: accept_superseded must be boolean")
    raw_url(repository, ref, pointer["upstream_manifest"])


def pointer_manifest_path(root: Path, value: str = DEFAULT_MANIFEST) -> Path:
    path = ledger.repo_path(root, value, "federation manifest")
    allowed = (root / "data/evidence-ledger").resolve()
    try:
        path.relative_to(allowed)
    except ValueError as exc:
        raise ledger.LedgerError(f"federation manifest must be under {allowed}") from exc
    return path


def pointer_view_path(root: Path, manifest: dict) -> Path:
    path = ledger.repo_path(root, manifest.get("view", DEFAULT_VIEW), "federation view")
    allowed = (root / "docs/reference/evidence-ledger").resolve()
    try:
        path.relative_to(allowed)
    except ValueError as exc:
        raise ledger.LedgerError(f"federation view must be under {allowed}") from exc
    return path


def local_pointer_path(base: Path, value: str) -> Path:
    path = ledger.repo_path(base, value, "pointer manifest")
    allowed = (base / "pointers").resolve()
    try:
        path.relative_to(allowed)
    except ValueError as exc:
        raise ledger.LedgerError(f"pointer must be under {allowed}: {value}") from exc
    return path


def load_local(root: Path, manifest_value: str = DEFAULT_MANIFEST, verify_hashes: bool = True):
    manifest_path = pointer_manifest_path(root, manifest_value)
    manifest = ledger.read_toml(manifest_path)
    if manifest.get("schema") != SCHEMA:
        ledger.fail(f"{manifest_path}: schema must be {SCHEMA}")
    rows = manifest.get("pointers")
    if not isinstance(rows, list) or not rows:
        ledger.fail(f"{manifest_path}: pointers must be a non-empty array")

    pointers = {}
    paths = {}
    hashes = {}
    base = manifest_path.parent
    for row in rows:
        if not isinstance(row, dict):
            ledger.fail(f"{manifest_path}: pointer rows must be tables")
        path = local_pointer_path(base, row.get("path"))
        if not path.is_file():
            ledger.fail(f"pointer is missing: {path}")
        pointer = ledger.read_toml(path)
        validate_pointer(pointer)
        pointer_id = pointer["id"]
        if pointer_id in pointers:
            ledger.fail(f"duplicate pointer ID {pointer_id}")
        actual = ledger.entry_hash(pointer)
        if verify_hashes and row.get("sha256") != actual:
            ledger.fail(f"pointer manifest hash mismatch for {pointer_id}")
        pointers[pointer_id] = pointer
        paths[pointer_id] = path
        hashes[pointer_id] = actual

    listed = {path.resolve() for path in paths.values()}
    present = {path.resolve() for path in (base / "pointers").glob("*.toml")}
    unlisted = sorted(path.name for path in present - listed)
    if unlisted:
        ledger.fail("pointer files missing from manifest: " + ", ".join(unlisted))
    return manifest, pointers, paths, hashes


def remote_claim_path(manifest_path: str, claim_path: str) -> str:
    base = PurePosixPath(safe_remote_path(manifest_path, "upstream manifest")).parent
    relative = PurePosixPath(safe_remote_path(claim_path, "upstream claim"))
    combined = base / relative
    if ".." in combined.parts:
        ledger.fail(f"unsafe upstream claim path {claim_path}")
    return combined.as_posix()


def load_upstream(pointer: dict, fetch=fetch_text):
    repository = pointer["upstream_repository"]
    ref = pointer["upstream_ref"]
    manifest_path = pointer["upstream_manifest"]
    manifest_url = raw_url(repository, ref, manifest_path)
    manifest = parse_toml_text(fetch(manifest_url), manifest_url)
    if manifest.get("schema") != ledger.SCHEMA:
        ledger.fail(f"{manifest_url}: unsupported upstream schema")
    rows = manifest.get("claims")
    if not isinstance(rows, list) or not rows:
        ledger.fail(f"{manifest_url}: no upstream claims")

    entries = {}
    hashes = {}
    paths = {}
    for row in rows:
        if not isinstance(row, dict):
            ledger.fail(f"{manifest_url}: claim rows must be tables")
        path = remote_claim_path(manifest_path, row.get("path"))
        url = raw_url(repository, ref, path)
        entry = parse_toml_text(fetch(url), url)
        claim_id = require(entry, "id", str)
        if claim_id in entries:
            ledger.fail(f"{manifest_url}: duplicate claim ID {claim_id}")
        actual = ledger.entry_hash(entry)
        if row.get("sha256") != actual:
            ledger.fail(f"{manifest_url}: hash mismatch for {claim_id}")
        entries[claim_id] = entry
        hashes[claim_id] = actual
        paths[claim_id] = path
    ledger.validate_graph(entries)
    return entries, hashes, paths, ledger.derive_statuses(entries)


def verify_pointers(pointers: dict[str, dict], fetch=fetch_text):
    upstreams = {}
    results = {}
    for pointer_id in sorted(pointers):
        pointer = pointers[pointer_id]
        key = (
            pointer["upstream_repository"],
            pointer["upstream_ref"],
            pointer["upstream_manifest"],
        )
        if key not in upstreams:
            upstreams[key] = load_upstream(pointer, fetch)
        entries, hashes, paths, statuses = upstreams[key]
        claim_id = pointer["claim_id"]
        if claim_id not in entries:
            ledger.fail(f"{pointer_id}: upstream claim is missing: {claim_id}")
        if hashes[claim_id] != pointer["claim_sha256"]:
            ledger.fail(f"{pointer_id}: upstream claim hash changed: {claim_id}")
        authority, reason, related = statuses[claim_id]
        if reason != pointer["expected_reason"]:
            ledger.fail(
                f"{pointer_id}: expected {pointer['expected_reason']}, got {reason} for {claim_id}"
            )
        if reason in {"CORRECTED", "SUPERSEDED"} and not pointer["accept_superseded"]:
            ledger.fail(f"{pointer_id}: target is {reason.lower()} and pointer rejects stale targets")
        results[pointer_id] = {
            "authority": authority,
            "reason": reason,
            "related": related,
            "claim_path": paths[claim_id],
        }
    return results


def federation_hash(hashes: dict[str, str]) -> str:
    payload = [{"id": key, "sha256": hashes[key]} for key in sorted(hashes)]
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def render_manifest(manifest: dict, paths: dict[str, Path], hashes: dict[str, str], root: Path):
    base = root / "data/evidence-ledger"
    lines = [
        f"schema = {SCHEMA}",
        f'federation = {json.dumps(manifest.get("federation", root.name))}',
        f'view = {json.dumps(manifest.get("view", DEFAULT_VIEW))}',
        "",
    ]
    for pointer_id in sorted(paths):
        lines.extend(
            [
                "[[pointers]]",
                f'path = {json.dumps(paths[pointer_id].relative_to(base).as_posix())}',
                f'sha256 = "{hashes[pointer_id]}"',
                "",
            ]
        )
    return "\n".join(lines)


def render_view(pointers: dict, hashes: dict, results: dict) -> str:
    lines = [
        "# Federated Signal Ledger pointers",
        "",
        "Generated from local pointer files and live upstream append-only ledgers. Do not edit this view.",
        f"Pointer digest: `{federation_hash(hashes)}`.",
        "",
        "| Pointer | Upstream claim | State | Purpose |",
        "|---|---|---|---|",
    ]
    for pointer_id in sorted(pointers):
        pointer = pointers[pointer_id]
        result = results[pointer_id]
        url = (
            f"https://github.com/{pointer['upstream_repository']}/blob/"
            f"{pointer['upstream_ref']}/{result['claim_path']}"
        )
        state = f"{result['authority']} / {result['reason']}"
        lines.append(
            f"| `{pointer_id}` | [{pointer['claim_id']}]({url}) | "
            f"{state} | {ledger.md_escape(pointer['purpose'])} |"
        )
    lines.extend(
        [
            "",
            "Pointers bind the canonical semantic hash of each upstream claim; they do not copy its body.",
            "A changed hash, missing claim, unexpected authority state, or disallowed correction/supersession fails CI.",
            "",
        ]
    )
    return "\n".join(lines)


def source_projection(check: bool) -> None:
    runtime = Path(__file__).resolve()
    source = runtime if runtime.suffix == ".source" else runtime.with_suffix(runtime.suffix + ".source")
    target = source.with_suffix("")
    rendered = ledger.strip_source_comments(source.read_text(encoding="utf-8"))
    if check:
        if not target.is_file() or target.read_text(encoding="utf-8") != rendered:
            ledger.fail(f"runtime projection is stale: {target}")
    else:
        target.write_text(rendered, encoding="utf-8")


def sync(root: Path, manifest_value: str) -> None:
    manifest, pointers, paths, hashes = load_local(root, manifest_value, verify_hashes=False)
    results = verify_pointers(pointers)
    manifest_path = pointer_manifest_path(root, manifest_value)
    view_path = pointer_view_path(root, manifest)
    manifest_path.write_text(render_manifest(manifest, paths, hashes, root), encoding="utf-8")
    view_path.parent.mkdir(parents=True, exist_ok=True)
    view_path.write_text(render_view(pointers, hashes, results), encoding="utf-8")


def check(root: Path, manifest_value: str) -> None:
    manifest, pointers, _, hashes = load_local(root, manifest_value)
    results = verify_pointers(pointers)
    view_path = pointer_view_path(root, manifest)
    expected = render_view(pointers, hashes, results)
    if not view_path.is_file() or view_path.read_text(encoding="utf-8") != expected:
        ledger.fail(f"generated federation view is stale: {view_path}")
    source_projection(check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify federated Signal Ledger pointers")
    parser.add_argument("command", choices=("check", "sync", "compile", "source-check"))
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    try:
        if args.command == "check":
            check(args.root.resolve(), args.manifest)
        elif args.command == "sync":
            sync(args.root.resolve(), args.manifest)
        elif args.command == "compile":
            source_projection(check=False)
        else:
            source_projection(check=True)
    except ledger.LedgerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
