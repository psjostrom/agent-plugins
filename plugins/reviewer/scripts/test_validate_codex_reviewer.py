#!/usr/bin/env python3

from __future__ import annotations

import contextlib
import io
import importlib.util
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT_PATH = Path(__file__).with_name("validate_codex_reviewer.py")
SPEC = importlib.util.spec_from_file_location("validate_codex_reviewer", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)
REPO_ROOT = VALIDATOR.REPO_ROOT
INSTALL_CURSOR = REPO_ROOT / "install-cursor.sh"


class DomainReviewerWiringTests(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_path = VALIDATOR.SKILL_ROOT / "SKILL.md"
        self.skill_text = self.skill_path.read_text(encoding="utf-8")

    def validate(self, text: str) -> list[str]:
        errors: list[str] = []
        VALIDATOR.validate_domain_reviewer_wiring(text, self.skill_path, errors)
        return errors

    def test_accepts_active_frontload_mapping_and_panel_wiring(self) -> None:
        self.assertEqual(self.validate(self.skill_text), [])

    def test_rejects_missing_strimma_detection(self) -> None:
        text = self.skill_text.replace("**Strimma** — basename contains `Strimma`", "**Strimma** — omitted")
        self.assertTrue(self.validate(text))

    def test_rejects_standard_panel_without_matching_domain_reviewers(self) -> None:
        text = self.skill_text.replace(
            "Test Reviewer when source changed, all matching domain reviewers",
            "Test Reviewer when source changed",
        )
        self.assertTrue(self.validate(text))

    def test_rejects_missing_harness_transport_split(self) -> None:
        text = self.skill_text.replace("**Codex / Cursor:** inline both into the child prompt", "inline always")
        self.assertTrue(self.validate(text))


class ReviewerParityTests(unittest.TestCase):
    def test_rejects_reviewer_missing_from_claude_surface(self) -> None:
        errors: list[str] = []
        VALIDATOR.validate_reviewer_surface_parity(
            codex_reviewers={"bug-hunter", "frontload-core"},
            claude_reviewers={"bug-hunter"},
            opencode_reviewers={"bug-hunter", "frontload-core"},
            errors=errors,
        )

        self.assertIn("missing Claude reviewer agents: frontload-core", errors)

    def test_rejects_reviewer_missing_from_opencode_surface(self) -> None:
        errors: list[str] = []
        VALIDATOR.validate_reviewer_surface_parity(
            codex_reviewers={"bug-hunter", "frontload-core"},
            claude_reviewers={"bug-hunter", "frontload-core"},
            opencode_reviewers={"bug-hunter"},
            errors=errors,
        )

        self.assertIn("missing opencode reviewer agents: frontload-core", errors)


class SharedCoreTests(unittest.TestCase):
    def test_accepts_harness_adapter_wiring(self) -> None:
        errors: list[str] = []
        VALIDATOR.validate_harness_adapters(errors)
        self.assertEqual(errors, [])

    def test_rejects_missing_role_in_cursor_adapter(self) -> None:
        path = VALIDATOR.SKILL_ROOT / "references" / "cursor.md"
        original = path.read_text(encoding="utf-8")
        try:
            path.write_text(original.replace("| `bug-hunter.md` |", "| `removed.md` |"), encoding="utf-8")
            errors: list[str] = []
            VALIDATOR.validate_harness_adapters(errors)
            self.assertTrue(any("'bug-hunter'" in error for error in errors))
        finally:
            path.write_text(original, encoding="utf-8")


class ThinShellTests(unittest.TestCase):
    def test_accepts_current_specialist_shells(self) -> None:
        errors: list[str] = []
        VALIDATOR.validate_thin_shells(errors)
        self.assertEqual(errors, [])

    def test_rejects_fat_specialist_body(self) -> None:
        path = VALIDATOR.PLUGIN_ROOT / "agents" / "bug-hunter.md"
        original = path.read_text(encoding="utf-8")
        try:
            path.write_text(original + ("\n" + "x" * VALIDATOR.MAX_SHELL_BODY_CHARS), encoding="utf-8")
            errors: list[str] = []
            VALIDATOR.validate_thin_shells(errors)
            self.assertTrue(any("exceeds" in error for error in errors))
        finally:
            path.write_text(original, encoding="utf-8")

    def test_rejects_repo_relative_specialist_prompt_marker(self) -> None:
        path = VALIDATOR.PLUGIN_ROOT / "agents" / "bug-hunter.md"
        original = path.read_text(encoding="utf-8")
        try:
            path.write_text(
                original.replace(
                    "${CLAUDE_PLUGIN_ROOT}/skills/parallel-review/references/reviewers/bug-hunter.md",
                    "skills/parallel-review/references/reviewers/bug-hunter.md",
                ),
                encoding="utf-8",
            )
            errors: list[str] = []
            VALIDATOR.validate_thin_shells(errors)
            self.assertTrue(any("plugin-absolute path" in error for error in errors))
        finally:
            path.write_text(original, encoding="utf-8")

    def test_rejects_opencode_orchestrator_repo_local_fallback(self) -> None:
        path = VALIDATOR.PLUGIN_ROOT / "opencode" / "commands" / "parallel-review.md"
        original = path.read_text(encoding="utf-8")
        try:
            path.write_text(original + '\nAlso try "$(pwd)/.opencode" as fallback.\n', encoding="utf-8")
            errors: list[str] = []
            VALIDATOR.validate_thin_shells(errors)
            self.assertTrue(any("must not trust repo-local" in error for error in errors))
        finally:
            path.write_text(original, encoding="utf-8")


class CursorPackagingTests(unittest.TestCase):
    def test_accepts_cursor_manifest_and_marketplace(self) -> None:
        errors: list[str] = []
        VALIDATOR.validate_cursor_manifest(errors)
        VALIDATOR.validate_cursor_marketplace(errors)
        VALIDATOR.validate_install_cursor(errors)
        self.assertEqual(errors, [])

    def test_install_cursor_symlink_refuse_and_uninstall(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env = {**os.environ, "CURSOR_PLUGINS_LOCAL": tmp}
            install = subprocess.run(
                [str(INSTALL_CURSOR), "install", "reviewer"],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            dest = Path(tmp) / "reviewer"
            self.assertTrue(dest.is_symlink())

            refuse_dir = Path(tmp) / "blocked"
            refuse_dir.mkdir()
            (refuse_dir / "reviewer").mkdir()
            refuse = subprocess.run(
                [str(INSTALL_CURSOR), "install", "reviewer"],
                cwd=REPO_ROOT,
                env={**os.environ, "CURSOR_PLUGINS_LOCAL": str(refuse_dir)},
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(refuse.returncode, 0)
            self.assertIn("Refusing to install", refuse.stdout + refuse.stderr)

            traversal = subprocess.run(
                [str(INSTALL_CURSOR), "install", "../reviewer"],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(traversal.returncode, 0)
            self.assertIn("not an available Cursor plugin name", traversal.stdout + traversal.stderr)

            uninstall = subprocess.run(
                [str(INSTALL_CURSOR), "uninstall", "reviewer"],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(uninstall.returncode, 0, uninstall.stderr)
            self.assertFalse(dest.exists())


class ValidatorOutputTests(unittest.TestCase):
    def test_failure_banner_matches_bundle_scope(self) -> None:
        stderr = io.StringIO()

        def fail_parity(errors: list[str]) -> None:
            errors.append("forced parity failure")

        with mock.patch.object(VALIDATOR, "validate_cross_platform_reviewer_parity", side_effect=fail_parity):
            with contextlib.redirect_stderr(stderr):
                status = VALIDATOR.main()

        self.assertEqual(status, 1)
        self.assertIn("Reviewer validation failed:", stderr.getvalue())
        self.assertNotIn("Codex reviewer validation failed:", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
