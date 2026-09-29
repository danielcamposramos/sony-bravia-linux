import importlib.util
import tempfile
import tomllib
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
MODULE_PATH = REPO / "tools/evidence-ledger/ledger.py"
SPEC = importlib.util.spec_from_file_location("signal_ledger", MODULE_PATH)
LEDGER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LEDGER)


class SignalLedgerTests(unittest.TestCase):
    def entry(self, **changes):
        value = {
            "schema": 1,
            "id": "TEST-0001",
            "title": "Test claim",
            "assertion": "A bounded test assertion.",
            "epistemic": "supported",
            "basis": "normative-citation",
            "domain": "standard",
            "date": "2026-09-29",
            "scope": "Test scope.",
            "authors": ["Test Partner"],
            "premises": [],
            "corrects": [],
            "supersedes": [],
            "standards": [{"name": "Test", "edition": "1", "section": "1"}],
        }
        value.update(changes)
        return value

    def test_repository_pilot_is_valid_and_fresh(self):
        LEDGER.check(REPO)

    def test_poison_pill_measurement_cannot_claim_visible_sink(self):
        claim = self.entry(
            basis="instrument-measurement",
            domain="visible-sink",
            standards=None,
        )
        with self.assertRaises(LEDGER.DomainViolationError):
            LEDGER.validate_entry(REPO, claim)

    def test_wrong_artifact_hash_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = root / "record.log"
            artifact.write_text("measurement\n", encoding="utf-8")
            claim = self.entry(
                basis="instrument-measurement",
                domain="driver",
                standards=None,
                artifacts=[{"path": "record.log", "sha256": "0" * 64}],
            )
            with self.assertRaisesRegex(LEDGER.LedgerError, "hash mismatch"):
                LEDGER.validate_entry(root, claim)

    def test_canonical_hash_ignores_toml_layout_and_comments(self):
        left = tomllib.loads('id="A"\npremises=["C","B"]\n')
        right = tomllib.loads('# comment\nid = "A"\npremises = [ "B", "C", ]\n')
        self.assertEqual(LEDGER.entry_hash(left), LEDGER.entry_hash(right))

    def test_graph_cycle_is_rejected(self):
        entries = {
            "A": {"domain": "driver", "epistemic": "inferred", "premises": ["B"]},
            "B": {"domain": "driver", "epistemic": "inferred", "premises": ["A"]},
        }
        with self.assertRaisesRegex(LEDGER.LedgerError, "cycle"):
            LEDGER.validate_graph(entries)

    def test_cross_domain_inference_is_rejected(self):
        entries = {
            "A": {"domain": "driver", "epistemic": "supported"},
            "B": {"domain": "hdmi-link", "epistemic": "inferred", "premises": ["A"]},
        }
        with self.assertRaises(LEDGER.DomainViolationError):
            LEDGER.validate_graph(entries)

    def test_standard_can_support_same_domain_inference(self):
        entries = {
            "A": {"domain": "standard", "epistemic": "supported"},
            "B": {"domain": "driver", "epistemic": "supported"},
            "C": {"domain": "driver", "epistemic": "inferred", "premises": ["A", "B"]},
        }
        LEDGER.validate_graph(entries)

    def test_correction_demotes_claim_and_its_inference(self):
        entries = {
            "A": {"epistemic": "supported"},
            "B": {"epistemic": "inferred", "premises": ["A"]},
            "C": {"epistemic": "supported", "corrects": ["A"]},
        }
        statuses = LEDGER.derive_statuses(entries)
        self.assertEqual(statuses["A"][:2], ("refuted", "CORRECTED"))
        self.assertEqual(statuses["B"][:2], ("undetermined", "STALE"))

    def test_refuted_correction_does_not_retain_authority(self):
        entries = {
            "A": {"epistemic": "supported"},
            "B": {"epistemic": "supported", "corrects": ["A"]},
            "C": {"epistemic": "supported", "corrects": ["B"]},
        }
        statuses = LEDGER.derive_statuses(entries)
        self.assertEqual(statuses["B"][:2], ("refuted", "CORRECTED"))
        self.assertEqual(statuses["A"][:2], ("supported", "SUPPORTED"))

    def test_manifest_view_cannot_escape_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(LEDGER.LedgerError, "escapes repository"):
                LEDGER.repo_path(root, "../outside.md", "manifest view")

    def test_manifest_view_cannot_overwrite_other_repository_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(LEDGER.LedgerError, "must be under"):
                LEDGER.manifest_view_path(root, {"view": "README.md"})

    def test_manifest_view_default_is_consistent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            expected = root / LEDGER.DEFAULT_VIEW
            self.assertEqual(LEDGER.manifest_view_path(root, {}), expected)
            rendered = LEDGER.render_manifest({}, {}, {}, root)
            self.assertIn(f'view = "{LEDGER.DEFAULT_VIEW}"', rendered)

    def test_nfc_key_collision_is_rejected(self):
        with self.assertRaisesRegex(LEDGER.LedgerError, "duplicate key"):
            LEDGER.normalize({"é": 1, "e\u0301": 2})

    def test_non_ascii_claim_id_is_rejected(self):
        claim = self.entry(id="TÉST-0001")
        with self.assertRaisesRegex(LEDGER.LedgerError, "uppercase ASCII"):
            LEDGER.validate_entry(REPO, claim)

    def test_manifest_claim_must_live_in_claims_folder(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            with self.assertRaisesRegex(LEDGER.LedgerError, "must be under"):
                LEDGER.manifest_claim_path(base, "elsewhere.toml")

    def test_non_finite_number_is_rejected_cleanly(self):
        with self.assertRaisesRegex(LEDGER.LedgerError, "non-finite"):
            LEDGER.canonical_bytes({"value": float("nan")})


if __name__ == "__main__":
    unittest.main()
