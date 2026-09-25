#!/usr/bin/env python3
"""Tests core Sayrhazi : parser YAML, schema, renderer, state. Stdlib uniquement.

Usage : python tests/test_core.py
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine"))
sys.path.insert(0, str(ROOT / "cli" / "commands"))

from sayrhazi_config import load_schema, parse_simple_yaml, validate_against_schema  # noqa: E402


class TestParser(unittest.TestCase):
    def test_template_se_parse(self):
        text = (ROOT / "runtimes" / "opencode" / "templates" / "sayrhazi.yaml").read_text(encoding="utf-8")
        data, err = parse_simple_yaml(text)
        self.assertIsNone(err, err)
        for key in ("workflow", "project", "agents", "technical", "commands", "runtime", "quality", "integration"):
            self.assertIn(key, data)

    def test_scalaires(self):
        data, err = parse_simple_yaml("a: 1\nb: true\nc: null\nd: [x, y]\ne: \"0.2.5\"\n")
        self.assertIsNone(err, err)
        self.assertEqual(data, {"a": 1, "b": True, "c": None, "d": ["x", "y"], "e": "0.2.5"})

    def test_erreurs(self):
        for bad in ("cle sans deux points\n", "- item\n", "a:\n   b: 1\n"):
            _, err = parse_simple_yaml(bad)
            self.assertIsNotNone(err, bad)


class TestSchema(unittest.TestCase):
    def test_template_conforme(self):
        schema, err = load_schema(ROOT)
        self.assertIsNone(err, err)
        text = (ROOT / "runtimes" / "opencode" / "templates" / "sayrhazi.yaml").read_text(encoding="utf-8")
        text = text.replace("A_COMPLETER", "test")
        data, perr = parse_simple_yaml(text)
        self.assertIsNone(perr, perr)
        violations = validate_against_schema(data, schema)
        self.assertEqual(violations, [], violations)

    def test_enum_refuse(self):
        schema, _ = load_schema(ROOT)
        data, _ = parse_simple_yaml("workflow:\n  name: Sayrhazi\n  version: x\nproject:\n  name: P\n  type: api\nagents:\n  architect: A\n  designer: D\n  builder: B\n  reviewer: R\n  security: S\n  qa: Q\ntechnical:\n  language: L\n  framework: F\n  database_type: oracle\n  database_driver: none\n  database_name: null\n  package_manager: yarn\ncommands:\n  install: i\n  dev: d\n  build: b\n  test: t\n  lint: l\nquality:\n  security_audit_required_by_default: true\n  visual_qa_required: false\n  required_checks: []\n")
        violations = validate_against_schema(data, schema)
        self.assertTrue(any("database_type" in v for v in violations), violations)


class TestRenderer(unittest.TestCase):
    def test_zero_derive(self):
        sys.path.insert(0, str(ROOT / "engine"))
        from renderer import render_one
        for trio in sorted((ROOT / "core" / "agents").iterdir()):
            if trio.is_dir():
                expected = (ROOT / "runtimes" / "opencode" / "agents" / (trio.name + ".md")).read_text(encoding="utf-8")
                self.assertEqual(render_one(trio), expected, trio.name)


class TestState(unittest.TestCase):
    def test_roundtrip(self):
        from state import default_state, load_state, save_state
        with tempfile.TemporaryDirectory() as tmp:
            st = default_state("FEATURE-001")
            st["workflow"]["pending_stages"] = ["review", "visual_qa"]
            save_state(tmp, st)
            back = load_state(tmp)
            self.assertEqual(back["workflow"]["task_id"], "FEATURE-001")
            self.assertEqual(back["workflow"]["pending_stages"], ["review", "visual_qa"])

    def test_absent(self):
        from state import load_state
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(load_state(tmp))


if __name__ == "__main__":
    unittest.main(verbosity=1)
