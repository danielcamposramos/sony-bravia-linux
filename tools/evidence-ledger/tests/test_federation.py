import importlib.util
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
TOOL_DIR = REPO / "tools/evidence-ledger"
sys.path.insert(0, str(TOOL_DIR))
import ledger

SPEC = importlib.util.spec_from_file_location("signal_federation", TOOL_DIR / "federation.py")
FEDERATION = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FEDERATION)


class FederationTests(unittest.TestCase):
    def claim(self, claim_id="SBL-TEST-0001", **changes):
        value = {
            "schema": 1,
            "id": claim_id,
            "title": "Test claim",
            "assertion": "A bounded assertion.",
            "epistemic": "supported",
            "basis": "normative-citation",
            "domain": "standard",
            "date": "2026-09-29",
            "scope": "Test scope.",
            "authors": ["Test Partner"],
            "premises": [],
            "corrects": [],
            "supersedes": [],
        }
        value.update(changes)
        return value

    def toml_claim(self, claim):
        lines = []
        for key in (
            "schema", "id", "title", "assertion", "epistemic", "basis", "domain",
            "date", "scope",
        ):
            value = claim[key]
            lines.append(f'{key} = {value}' if isinstance(value, int) else f'{key} = {value!r}')
        for key in ("authors", "premises", "corrects", "supersedes"):
            values = ", ".join(repr(value) for value in claim.get(key, []))
            lines.append(f"{key} = [{values}]")
        return "\n".join(lines).replace("'", '"') + "\n"

    def upstream(self, claims):
        repository = "example/project"
        ref = "main"
        manifest_path = "data/evidence-ledger/ledger.toml"
        manifest_lines = ["schema = 1", 'ledger = "test"', 'view = "view.md"', ""]
        mapping = {}
        for index, claim in enumerate(claims, start=1):
            path = f"claims/claim-{index}.toml"
            manifest_lines.extend(
                [
                    "[[claims]]",
                    f'path = "{path}"',
                    f'sha256 = "{ledger.entry_hash(claim)}"',
                    "",
                ]
            )
            url = FEDERATION.raw_url(repository, ref, f"data/evidence-ledger/{path}")
            mapping[url] = self.toml_claim(claim)
        manifest_url = FEDERATION.raw_url(repository, ref, manifest_path)
        mapping[manifest_url] = "\n".join(manifest_lines)
        return repository, ref, manifest_path, mapping

    def pointer(self, claim, repository, ref, manifest, **changes):
        value = {
            "schema": 1,
            "id": "ALH-SBL-TEST-0001",
            "purpose": "Test immutable federation.",
            "upstream_repository": repository,
            "upstream_ref": ref,
            "upstream_manifest": manifest,
            "claim_id": claim["id"],
            "claim_sha256": ledger.entry_hash(claim),
            "expected_reason": "SUPPORTED",
            "accept_superseded": False,
        }
        value.update(changes)
        return value

    def test_verified_pointer_resolves_by_semantic_hash(self):
        claim = self.claim()
        repository, ref, manifest, mapping = self.upstream([claim])
        pointer = self.pointer(claim, repository, ref, manifest)
        result = FEDERATION.verify_pointers({pointer["id"]: pointer}, mapping.__getitem__)
        self.assertEqual(result[pointer["id"]]["reason"], "SUPPORTED")

    def test_changed_claim_hash_is_rejected(self):
        claim = self.claim()
        repository, ref, manifest, mapping = self.upstream([claim])
        pointer = self.pointer(claim, repository, ref, manifest, claim_sha256="0" * 64)
        with self.assertRaisesRegex(ledger.LedgerError, "hash changed"):
            FEDERATION.verify_pointers({pointer["id"]: pointer}, mapping.__getitem__)

    def test_corrected_target_requires_explicit_historical_policy(self):
        claim = self.claim()
        correction = self.claim(
            "SBL-TEST-0002",
            title="Correction",
            assertion="The first assertion is corrected.",
            corrects=[claim["id"]],
        )
        repository, ref, manifest, mapping = self.upstream([claim, correction])
        pointer = self.pointer(
            claim,
            repository,
            ref,
            manifest,
            expected_reason="CORRECTED",
            accept_superseded=False,
        )
        with self.assertRaisesRegex(ledger.LedgerError, "rejects stale"):
            FEDERATION.verify_pointers({pointer["id"]: pointer}, mapping.__getitem__)

    def test_unsafe_remote_path_is_rejected(self):
        with self.assertRaisesRegex(ledger.LedgerError, "unsafe"):
            FEDERATION.safe_remote_path("../claim.toml", "test")

    def test_federation_runtime_projection_is_fresh(self):
        FEDERATION.source_projection(check=True)

    def test_action_runtime_projection_is_fresh(self):
        folder = REPO / ".github/actions/verify-signal-pointers"
        source_lines = folder.joinpath("action.yml.source").read_text(encoding="utf-8").splitlines()
        rendered = "\n".join(line for line in source_lines if not line.lstrip().startswith("#")) + "\n"
        self.assertEqual(folder.joinpath("action.yml").read_text(encoding="utf-8"), rendered)


if __name__ == "__main__":
    unittest.main()
