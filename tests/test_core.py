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


class TestReport(unittest.TestCase):
    def test_templates_valides(self):
        from report import parse_report, validate_report, validate_task
        task = parse_report((ROOT / "core" / "templates" / "task.md").read_text(encoding="utf-8"))
        self.assertEqual(validate_task(task), [], validate_task(task))
        rep = parse_report((ROOT / "core" / "templates" / "report.md").read_text(encoding="utf-8"))
        self.assertEqual(validate_report(rep), [], validate_report(rep))

    def test_champs_requis(self):
        from report import parse_report, validate_report
        rep = parse_report("task_id: FEATURE-001\nagent: builder\nstatus: TERMINÉ\ncompleted_at: \"2026-09-26T10:00:00+04:00\"\n")
        self.assertTrue(any("summary" in v for v in validate_report(rep)), validate_report(rep))

    def test_statut_par_role(self):
        from report import parse_report, validate_report
        ok_review = parse_report("task_id: FEATURE-001\nagent: reviewer\nstatus: VALIDÉ\ncompleted_at: \"2026-09-26T10:00:00+04:00\"\nsummary: OK.\n")
        self.assertEqual(validate_report(ok_review), [])
        bad_build = parse_report("task_id: FEATURE-001\nagent: builder\nstatus: VALIDÉ\ncompleted_at: \"2026-09-26T10:00:00+04:00\"\nsummary: Fait.\n")
        self.assertTrue(any("status" in v for v in validate_report(bad_build)))
        bad_qa = parse_report("task_id: FEATURE-001\nagent: builder\nstatus: À COMPLÉTER\ncompleted_at: \"2026-09-26T10:00:00+04:00\"\nsummary: Fait.\n")
        self.assertTrue(any("status" in v for v in validate_report(bad_qa)))
        ok_qa = parse_report("task_id: FEATURE-001\nagent: qa\nstatus: À COMPLÉTER\ncompleted_at: \"2026-09-26T10:00:00+04:00\"\nsummary: En attente.\n")
        self.assertEqual(validate_report(ok_qa), [])
        underscored = parse_report("task_id: FEATURE-001\nagent: reviewer\nstatus: VALIDÉ_AVEC_RÉSERVES\ncompleted_at: \"2026-09-26T10:00:00+04:00\"\nsummary: OK.\n")
        self.assertEqual(validate_report(underscored), [])

    def test_version_horodatage_refusee(self):
        from report import parse_report, validate_report
        rep = parse_report("task_id: FEATURE-001\nagent: builder\nstatus: TERMINÉ\nversion: \"2026-09-23T19:30:00+04:00\"\nsummary: Fait.\n")
        self.assertTrue(any("version" in v for v in validate_report(rep)))

    def test_task_id_formats(self):
        from report import parse_report, validate_report
        for tid in ("FEATURE-001", "MPANGO-2026-014"):
            rep = parse_report(f"task_id: {tid}\nagent: builder\nstatus: TERMINÉ\ncompleted_at: \"2026-09-26T10:00:00+04:00\"\nsummary: Fait.\n")
            self.assertEqual(validate_report(rep), [], tid)
        for tid in ("AB", "a b"):
            rep = parse_report(f"task_id: {tid}\nagent: builder\nstatus: TERMINÉ\ncompleted_at: \"2026-09-26T10:00:00+04:00\"\nsummary: Fait.\n")
            self.assertTrue(any("task_id" in v for v in validate_report(rep)), tid)

    def test_coherence_indicateurs(self):
        from report import parse_report, validate_task
        incoherent = parse_report("task_id: FEATURE-001\ntitle: T\nstatus: À IMPLÉMENTER\nagents_required: [builder, reviewer]\nsecurity_required: true\n")
        self.assertTrue(any("security" in v for v in validate_task(incoherent)))
        coherent = parse_report("task_id: FEATURE-001\ntitle: T\nstatus: À IMPLÉMENTER\nagents_required: [builder, reviewer, security]\nsecurity_required: true\n")
        self.assertEqual(validate_task(coherent), [])

    def test_transition(self):
        from report import check_transition, parse_report
        rep = parse_report("task_id: FEATURE-001\nagent: builder\nstatus: TERMINÉ\ncompleted_at: \"2026-09-26T10:00:00+04:00\"\nsummary: Fait.\n")
        self.assertEqual(check_transition(rep, expected_agent="builder", expected_task_id="FEATURE-001",
                                          output_text="review FEATURE-001 ok"), [])
        self.assertTrue(check_transition(rep, expected_agent="builder", expected_task_id="FEATURE-002"))
        self.assertTrue(check_transition(rep, expected_agent="reviewer", expected_task_id="FEATURE-001"))
        stale = parse_report("task_id: FEATURE-001\nagent: builder\nstatus: EN COURS\ncompleted_at: \"2026-09-26T10:00:00+04:00\"\nsummary: WIP.\n")
        self.assertTrue(check_transition(stale, expected_agent="builder", expected_task_id="FEATURE-001",
                                         allowed_statuses=("TERMINÉ",)))
        self.assertTrue(check_transition(rep, expected_agent="builder", expected_task_id="FEATURE-001",
                                         output_text="review sans identifiant"))


class TestAgentContracts(unittest.TestCase):
    def test_bloc_contrat_machine_exige(self):
        import re as _re
        for trio in sorted((ROOT / "core" / "agents").iterdir()):
            if not trio.is_dir():
                continue
            agent_yaml = (trio / "agent.yaml").read_text(encoding="utf-8")
            role = _re.search(r"^role:\s*(.+)$", agent_yaml, _re.M)
            self.assertIsNotNone(role, trio.name)
            body = (trio / "instructions.md").read_text(encoding="utf-8")
            for marker in ("task_id:", "completed_at:", "summary:"):
                self.assertIn(marker, body, f"{trio.name} : `{marker}` absent des instructions")
            self.assertIn(f"agent: {role.group(1).strip()}", body, f"{trio.name} : `agent: {role.group(1).strip()}` absent")
            contract = (trio / "contract.yaml").read_text(encoding="utf-8")
            for marker in ("- task_id", "- agent", "- completed_at", "- summary"):
                self.assertIn(marker, contract, f"{trio.name} : `{marker}` absent du contrat")


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
