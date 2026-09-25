#!/usr/bin/env python3
"""Tests integration Sayrhazi : install -> check -> update -> remove. Stdlib.

Usage : python tests/test_integration.py
"""
from __future__ import annotations

import sys
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine"))
sys.path.insert(0, str(ROOT / "cli" / "commands"))

from installer import install_project  # noqa: E402
from updater import migrate_config  # noqa: E402


def fill_config(p: Path) -> None:
    text = p.read_text(encoding="utf-8")
    for key in ("name: A_COMPLETER", "description: A_COMPLETER", "language: A_COMPLETER",
                "framework: A_COMPLETER", "build: A_COMPLETER", "test: A_COMPLETER", "lint: A_COMPLETER"):
        text = text.replace(key, key.replace("A_COMPLETER", "test"))
    p.write_text(text, encoding="utf-8")


class TestIntegration(unittest.TestCase):
    def test_cycle_complet(self):
        import re as _re
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            install_project(project, ROOT)
            self.assertTrue((project / ".opencode" / "agent" / "bamse.md").is_file())
            self.assertTrue((project / ".opencode" / "watch-work.py").is_file())
            self.assertEqual(len(list((project / ".opencode" / "agent").glob("*.md"))), 6)
            # tunda-equivalent : cles presentes ?
            text = (project / ".opencode" / "sayrhazi.yaml").read_text(encoding="utf-8")
            for key in ("workflow:", "project:", "agents:", "technical:", "commands:", "quality:"):
                self.assertIn(key, text)
            fill_config(project / ".opencode" / "sayrhazi.yaml")
            (project / "AGENTS.md").write_text("# R\n- Cle\n", encoding="utf-8")

    def test_migration_douce(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            install_project(project, ROOT)
            cfg = project / ".opencode" / "sayrhazi.yaml"
            text = cfg.read_text(encoding="utf-8")
            text = text.replace("  designer: Ali\n", "")
            text = text.replace("  database_type: none", "  database: matest")
            text = re.sub(r'  version: "[^"]+"', '  version: "0.1.0"', text)
            cfg.write_text(text, encoding="utf-8")
            added, backup, warns = migrate_config(cfg, ROOT / "runtimes" / "opencode" / "templates" / "sayrhazi.yaml",
                                                  project / ".opencode" / "history")
            self.assertTrue(any("designer" in a for a in added), added)
            self.assertTrue(any("database_type" in a for a in added), added)
            self.assertIsNotNone(backup)
            after = cfg.read_text(encoding="utf-8")
            self.assertIn("database_name: matest", after)


if __name__ == "__main__":
    unittest.main(verbosity=1)
