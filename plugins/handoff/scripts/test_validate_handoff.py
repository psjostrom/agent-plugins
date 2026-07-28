#!/usr/bin/env python3
"""Regression tests for the deterministic Handoff bundle validator."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = SCRIPT_DIR.parents[2]
sys.path.insert(0, str(SCRIPT_DIR))

import validate_handoff as validator  # noqa: E402

validate_bundle = validator.validate_bundle


class HandoffValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.temporary_directory.name)
        src = REPOSITORY_ROOT / "plugins" / "handoff"
        if src.is_dir():
            shutil.copytree(src, self.repo_root / "plugins" / "handoff")
        else:
            (self.repo_root / "plugins" / "handoff").mkdir(parents=True)
        for relative_path in (
            Path(".agents/plugins/marketplace.json"),
            Path(".claude-plugin/marketplace.json"),
            Path(".cursor-plugin/marketplace.json"),
            Path("AGENTS.md"),
            Path("README.md"),
        ):
            destination = self.repo_root / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPOSITORY_ROOT / relative_path, destination)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def path(self, relative_path: str) -> Path:
        return self.repo_root / relative_path

    def write_json(self, relative_path: str, value: object) -> None:
        self.path(relative_path).write_text(
            json.dumps(value, indent=2) + "\n", encoding="utf-8"
        )

    def assert_error(self, fragment: str) -> list[str]:
        errors = validate_bundle(self.repo_root)
        self.assertTrue(
            any(fragment in error for error in errors),
            f"expected error containing {fragment!r}; got {errors!r}",
        )
        return errors

    def test_reports_missing_skill_when_bundle_incomplete(self) -> None:
        skill = self.path("plugins/handoff/skills/handoff/SKILL.md")
        if skill.is_file():
            skill.unlink()
        self.assert_error("plugins/handoff/skills/handoff/SKILL.md")

    def test_reports_missing_marketplace_plugin_entry(self) -> None:
        data = json.loads(
            self.path(".cursor-plugin/marketplace.json").read_text(encoding="utf-8")
        )
        data["plugins"] = [
            entry
            for entry in data["plugins"]
            if not (isinstance(entry, dict) and entry.get("name") == "handoff")
        ]
        self.write_json(".cursor-plugin/marketplace.json", data)
        self.assert_error("missing handoff plugin entry")


if __name__ == "__main__":
    unittest.main()
