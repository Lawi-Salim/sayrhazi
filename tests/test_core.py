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

    def test_bom_ignore(self):
        from report import parse_report, validate_report
        rep = parse_report("\ufeff" + "task_id: FEATURE-001\nagent: builder\nstatus: TERMINÉ\n"
                           'completed_at: "2026-09-26T10:00:00+04:00"\nsummary: Fait.\n')
        self.assertEqual(rep.get("task_id"), "FEATURE-001")
        self.assertEqual(validate_report(rep), [])

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


class TestAliDirective(unittest.TestCase):
    def test_fondations_et_references_exigees(self):
        body = (ROOT / "core" / "agents" / "ali" / "instructions.md").read_text(encoding="utf-8")
        for marker in ("font-family", "palette", "Playwright", "2 à 3", "project.type", "ne copie jamais",
                       "Cible fournie", "Outils indisponibles"):
            self.assertIn(marker, body, f"Ali : `{marker}` absent des instructions")
        contract = (ROOT / "core" / "agents" / "ali" / "contract.yaml").read_text(encoding="utf-8")
        for marker in ("- references citees", "- palette", "- typographie", "- tokens",
                       "- 2 a 3 references reelles citees", "aucun asset copie",
                       "- cible URL visitee via navigateur avant toute adaptation"):
            self.assertIn(marker, contract, f"Ali : `{marker}` absent du contrat")


class TestWorkflow(unittest.TestCase):
    def _load(self, name):
        from workflow import parse_workflow
        text = (ROOT / name).read_text(encoding="utf-8")
        data, err = parse_workflow(text)
        self.assertIsNone(err, err)
        return data

    def test_reference_conforme(self):
        from workflow import validate_workflow
        data = self._load("core/workflow/workflow.yaml")
        self.assertEqual(validate_workflow(data), [])

    def test_template_egal_reference(self):
        ref = self._load("core/workflow/workflow.yaml")
        tmpl = self._load("runtimes/opencode/templates/workflow.yaml")
        self.assertEqual(tmpl, ref)

    def test_invalides(self):
        from workflow import parse_workflow, validate_workflow
        base = ("workflow:\n  mode: supervised\n  auto_start: false\n  max_parallel_agents: 3\n"
                "stages:\n  - id: review\n    agent: reviewer\n    trigger:\n"
                "      report: build.txt\n      status: TERMINÉ\n    auto: true\n")
        self.assertEqual(validate_workflow(parse_workflow(base)[0]), [])
        variants = [
            base.replace("agent: reviewer", "agent: nope"),
            base.replace("status: TERMINÉ", "status: BIDON"),
            base.replace("auto: true", "auto: true\n    condition: magie_required"),
            base.replace("- id: review", "- id: review\n  - id: review"),
            base.replace("auto_start: false", "auto_start: true"),
            base.replace("mode: supervised", "mode: autopilote"),
            base.replace("report: build.txt", "report: inconnu.txt"),
        ]
        for i, text in enumerate(variants):
            data, err = parse_workflow(text)
            problems = [err] if err else validate_workflow(data)
            self.assertTrue(problems, f"variante {i} acceptée à tort")

    def test_coherence_stages(self):
        from workflow import parse_workflow
        data = self._load("core/workflow/workflow.yaml")
        for stage in data["stages"]:
            cand = ROOT / "core" / "workflow" / "stages" / (stage["id"] + ".yaml")
            if not cand.is_file():
                continue
            detail, err = parse_workflow(cand.read_text(encoding="utf-8"))
            self.assertIsNone(err, err)
            self.assertEqual(detail.get("agent"), stage["agent"], stage["id"])
            self.assertEqual(detail.get("condition"), stage.get("condition"), stage["id"])


class TestStateReconcile(unittest.TestCase):
    def _project(self, reports):
        import tempfile
        tmp = tempfile.mkdtemp()
        resume = Path(tmp) / ".opencode" / "resume"
        resume.mkdir(parents=True)
        for name, body in reports.items():
            (resume / name).write_text(body, encoding="utf-8")
        self.addCleanup(__import__("shutil").rmtree, tmp, True)
        return tmp

    def _report(self, tid, agent, status):
        return (f"task_id: {tid}\nagent: {agent}\nstatus: {status}\n"
                'completed_at: "2026-09-26T10:00:00+04:00"\nsummary: Fait.\n')

    def test_frais_adopte_tache(self):
        from state import reconcile
        tmp = self._project({"build.txt": self._report("FEATURE-001", "builder", "TERMINÉ")})
        state, notes = reconcile(tmp)
        wf = state["workflow"]
        self.assertEqual(wf["task_id"], "FEATURE-001")
        self.assertEqual(wf["status"], "IN_PROGRESS")
        self.assertIn("implementation", wf["completed_stages"])
        self.assertIn("review", wf["current_stages"])
        self.assertIn("design", wf["pending_stages"])

    def test_review_validee(self):
        from state import reconcile
        tmp = self._project({"build.txt": self._report("FEATURE-001", "builder", "TERMINÉ"),
                             "review.txt": self._report("FEATURE-001", "reviewer", "VALIDÉ")})
        state, _ = reconcile(tmp)
        self.assertIn("review", state["workflow"]["completed_stages"])

    def test_corrections_rouvrent_implementation(self):
        from state import reconcile
        tmp = self._project({"build.txt": self._report("FEATURE-001", "builder", "TERMINÉ"),
                             "review.txt": self._report("FEATURE-001", "reviewer", "CORRECTIONS NÉCESSAIRES")})
        state, notes = reconcile(tmp, "FEATURE-001")
        wf = state["workflow"]
        self.assertIn("review", wf["completed_stages"])
        self.assertNotIn("implementation", wf["completed_stages"])
        self.assertTrue(any("corrections" in n for n in notes), notes)

    def test_review_sans_build_bloquee(self):
        from state import reconcile
        tmp = self._project({"review.txt": self._report("FEATURE-001", "reviewer", "VALIDÉ")})
        state, notes = reconcile(tmp, "FEATURE-001")
        self.assertIn("review", state["workflow"]["blocked_stages"])
        self.assertTrue(any("bloquée" in n for n in notes), notes)

    def test_autre_tache_ignoree(self):
        from state import reconcile, save_state, default_state
        tmp = self._project({"build.txt": self._report("FEATURE-002", "builder", "TERMINÉ")})
        st = default_state("FEATURE-001")
        save_state(tmp, st)
        state, notes = reconcile(tmp)
        self.assertEqual(state["workflow"]["task_id"], "FEATURE-001")
        self.assertNotIn("implementation", state["workflow"]["completed_stages"])
        self.assertTrue(any("autre tâche" in n for n in notes), notes)

    def test_vide_rien_a_reconcilier(self):
        from state import reconcile
        tmp = self._project({})
        state, notes = reconcile(tmp)
        self.assertIsNone(state)
        self.assertTrue(notes)

    def test_validate_state(self):
        from state import validate_state
        self.assertTrue(validate_state({"workflow": {"task_id": "", "status": "BIZARRE",
                                                     "current_stages": [], "completed_stages": [],
                                                     "pending_stages": [], "blocked_stages": [],
                                                     "running_agents": []}}))


class TestWatcherEngine(unittest.TestCase):
    @classmethod
    def _watcher(cls):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "watch_work", str(ROOT / "runtimes" / "opencode" / "scripts" / "watch-work.py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_config_moteur(self):
        from pathlib import Path as _Path
        w = self._watcher()
        cfg, err = w.parse_workflow_minimal(
            _Path(str(ROOT / "runtimes" / "opencode" / "templates" / "workflow.yaml")))
        self.assertIsNone(err, err)
        usable, notes = w.select_auto_stages(cfg)
        self.assertEqual([s["id"] for s in usable],
                         ["review", "security", "visual_qa", "rework"])
        self.assertEqual(notes, [])

    def test_eligibilite(self):
        w = self._watcher()
        cfg, _ = w.parse_workflow_minimal(
            __import__("pathlib").Path(str(ROOT / "core" / "workflow" / "workflow.yaml")))
        usable, _ = w.select_auto_stages(cfg)
        cfg = {"stages": usable}
        conds = {"security_required": False, "visual_qa_required": False, "design_required": False}
        ready = {"build.txt": {"task_id": "F-1", "status": "TERMINÉ", "mtime": 100.0, "hash": "h"}}
        found = w.eligible_transitions(cfg, ready, conds, {})
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0][1], "F-1")
        stale = {"review.txt": {"task_id": "F-1", "mtime": 200.0}}
        self.assertEqual(w.eligible_transitions(cfg, ready, conds, stale), [])
        fresh = {"review.txt": {"task_id": "F-1", "mtime": 50.0}}
        self.assertEqual(len(w.eligible_transitions(cfg, ready, conds, fresh)), 1)
        encours = {"build.txt": {"task_id": "F-1", "status": "EN COURS", "mtime": 100.0, "hash": "h"}}
        self.assertEqual(w.eligible_transitions(cfg, encours, conds, {}), [])

    def test_config_cassee_jamais_crash(self):
        import tempfile
        from pathlib import Path as _Path
        w = self._watcher()
        bad = _Path(tempfile.mkdtemp()) / "workflow.yaml"
        bad.write_text("stages:\n  - id: x\n    agent: nope\n    auto: true\n    trigger:\n"
                       "      report: build.txt\n      status: TERMINÉ\n", encoding="utf-8")
        cfg, err = w.parse_workflow_minimal(bad)
        self.assertIsNone(err, err)
        usable, notes = w.select_auto_stages(cfg)
        self.assertEqual(usable, [])
        self.assertEqual(len(notes), 1)

    def test_bom_review_couverte(self):
        # Scénario Sarhi : review.txt avec BOM plus récente que build.txt.
        import tempfile
        from pathlib import Path as _Path
        w = self._watcher()
        d = _Path(tempfile.mkdtemp())
        resume = d / ".opencode" / "resume"
        resume.mkdir(parents=True)
        (resume / "build.txt").write_text(
            "task_id: F-1\nagent: builder\nstatus: TERMINÉ\n"
            'completed_at: "2026-09-26T10:00:00+04:00"\nsummary: Fait.\n', encoding="utf-8")
        (resume / "review.txt").write_text(
            "\ufefftask_id: F-1\nagent: reviewer\nstatus: VALIDÉ\n"
            'completed_at: "2026-09-26T11:00:00+04:00"\nsummary: OK.\n', encoding="utf-8")
        import os as _os
        import time as _time
        now = _time.time()
        _os.utime(str(resume / "build.txt"), (now - 100, now - 100))
        _os.utime(str(resume / "review.txt"), (now, now))
        cfg, _ = w.parse_workflow_minimal(
            _Path(str(ROOT / "core" / "workflow" / "workflow.yaml")))
        usable, _ = w.select_auto_stages(cfg)
        triggers, outputs = {}, {}
        for name in ("build.txt", "review.txt"):
            tid, stat, mtime = w.parse_report_file(resume / name)
            self.assertEqual(tid, "F-1", name)
            triggers[name] = {"task_id": tid, "status": stat, "mtime": mtime, "hash": "h"}
            outputs[name] = {"task_id": tid, "mtime": mtime}
        conds = {"security_required": False, "visual_qa_required": False, "design_required": False}
        self.assertEqual(w.eligible_transitions({"stages": usable}, triggers, conds, outputs), [])

    def test_verrou_pid_vivant(self):
        import os as _os
        import tempfile
        import time as _time
        from pathlib import Path as _Path
        w = self._watcher()
        d = _Path(tempfile.mkdtemp())
        self.assertTrue(w.acquire_lock(d))
        self.assertEqual(w.lock_holder_pid(d), _os.getpid())
        self.assertTrue(w.holder_alive(d))
        # Verrou périmé mais détenteur vivant (long run) : jamais purgé.
        old = _time.time() - 3600
        _os.utime(str(d / ".opencode" / "state" / "watcher.lock"), (old, old))
        self.assertFalse(w.acquire_lock(d))
        self.assertEqual(w.lock_holder_pid(d), _os.getpid())
        # Verrou périmé d'un mort : purgé puis acquis.
        (d / ".opencode" / "state" / "watcher.lock").write_text(
            "2147483647 2020-01-01T00:00:00", encoding="utf-8")
        _os.utime(str(d / ".opencode" / "state" / "watcher.lock"), (old, old))
        self.assertFalse(w.holder_alive(d))
        self.assertTrue(w.acquire_lock(d))
        # Release ne supprime jamais le verrou d'autrui.
        (d / ".opencode" / "state" / "watcher.lock").write_text(
            "2147483647 2020-01-01T00:00:00", encoding="utf-8")
        w.release_lock(d)
        self.assertTrue((d / ".opencode" / "state" / "watcher.lock").is_file())

    def test_verrou_et_etat(self):
        import sys
        import tempfile
        from pathlib import Path as _Path
        w = self._watcher()
        d = _Path(tempfile.mkdtemp())
        self.assertTrue(w.acquire_lock(d))
        self.assertFalse(w.acquire_lock(d))
        w.release_lock(d)
        self.assertTrue(w.acquire_lock(d))
        w.release_lock(d)
        w.journal(d, "transition test")
        self.assertTrue((d / ".opencode" / "history" / "workflow-log.md").is_file())
        w.note_state_running(d, "F-9", "reviewer")
        w.note_state_running(d, "F-9", None)
        sys.path.insert(0, str(ROOT / "engine"))
        from state import load_state, validate_state
        st = load_state(d)
        self.assertEqual(st["workflow"]["task_id"], "F-9")
        self.assertEqual(validate_state(st), [])
        self.assertEqual(st["workflow"]["running_agents"], [])


class TestConditions(unittest.TestCase):
    def _cfg(self):
        from workflow import parse_workflow
        data, err = parse_workflow(
            (ROOT / "core" / "workflow" / "workflow.yaml").read_text(encoding="utf-8"))
        self.assertIsNone(err, err)
        return data

    def _watcher(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "watch_work", str(ROOT / "runtimes" / "opencode" / "scripts" / "watch-work.py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_seuls_requis_tournent(self):
        w = self._watcher()
        data = self._cfg()
        usable, _ = w.select_auto_stages(data)
        self.assertEqual([s["id"] for s in usable], ["review", "security", "visual_qa", "rework"])
        cfg = {"stages": usable}
        build = {"build.txt": {"task_id": "F-1", "status": "TERMINÉ", "mtime": 100.0, "hash": "h"}}
        off = {"security_required": False, "visual_qa_required": False, "design_required": False}
        self.assertEqual([s["id"] for s, _, _ in w.eligible_transitions(cfg, build, off, {})],
                         ["review"])
        on = {"security_required": True, "visual_qa_required": True, "design_required": False}
        got = sorted(s["id"] for s, _, _ in w.eligible_transitions(cfg, build, on, {}))
        self.assertEqual(got, ["review", "security", "visual_qa"])

    def test_rework_corrections(self):
        w = self._watcher()
        data = self._cfg()
        usable, _ = w.select_auto_stages(data)
        cfg = {"stages": usable}
        off = {"security_required": False, "visual_qa_required": False, "design_required": False}
        trig = {"review.txt": {"task_id": "F-1", "status": "CORRECTIONS NÉCESSAIRES",
                               "mtime": 200.0, "hash": "h"}}
        outs = {"build.txt": {"task_id": "F-1", "mtime": 100.0}}
        got = [s["id"] for s, _, _ in w.eligible_transitions(cfg, trig, off, outs)]
        self.assertEqual(got, ["rework"])
        # Bamse a déjà re-livré : on ne le rappelle pas, Hadji reprend.
        outs_frais = {"build.txt": {"task_id": "F-1", "mtime": 300.0}}
        trig2 = {"build.txt": {"task_id": "F-1", "status": "TERMINÉ", "mtime": 300.0, "hash": "h2"},
                 "review.txt": {"task_id": "F-1", "status": "CORRECTIONS NÉCESSAIRES",
                                "mtime": 200.0, "hash": "h"}}
        got2 = sorted(s["id"] for s, _, _ in w.eligible_transitions(cfg, trig2, off, outs_frais))
        self.assertEqual(got2, ["review"])

    def test_summarize_agents(self):
        from workflow import summarize_agents
        rows = dict((sid, state) for sid, _, state in summarize_agents(
            self._cfg(), {"security_required": True, "visual_qa_required": False,
                          "design_required": False}))
        self.assertEqual(rows["review"], "requis")
        self.assertEqual(rows["security"], "requis")
        self.assertTrue(rows["visual_qa"].startswith("inactif"))
        self.assertEqual(rows["implementation"], "manuel")
        self.assertEqual(rows["design"], "manuel")


class TestParallel(unittest.TestCase):
    def _stages(self):
        return [{"id": "review", "agent": "reviewer"},
                {"id": "security", "agent": "security"},
                {"id": "visual_qa", "agent": "qa"}]

    def test_parallelisme_reel(self):
        import importlib.util
        import tempfile
        import threading
        import time as _time
        from pathlib import Path as _Path
        spec = importlib.util.spec_from_file_location(
            "watch_work_p", str(ROOT / "runtimes" / "opencode" / "scripts" / "watch-work.py"))
        w = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(w)
        root = _Path(tempfile.mkdtemp())
        lock = threading.Lock()
        current = {"n": 0, "max": 0}

        def stub(_root, stage, _task):
            with lock:
                current["n"] += 1
                current["max"] = max(current["max"], current["n"])
            _time.sleep(0.3)
            with lock:
                current["n"] -= 1
            return True, "ok"

        w.trigger_stage = stub
        items = [(f"k{i}", s, "T", f"{s['id']} prêt (T)") for i, s in enumerate(self._stages())]
        start = _time.time()
        ok, done, failed = w.run_branches(root, items, 3)
        elapsed = _time.time() - start
        self.assertTrue(ok)
        self.assertEqual(len(done), 3)
        self.assertEqual(failed, [])
        self.assertEqual(current["max"], 3)
        self.assertLess(elapsed, 0.9)

    def test_plafond_et_echec_isole(self):
        import importlib.util
        import tempfile
        import threading
        import time as _time
        from pathlib import Path as _Path
        spec = importlib.util.spec_from_file_location(
            "watch_work_q", str(ROOT / "runtimes" / "opencode" / "scripts" / "watch-work.py"))
        w = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(w)
        root = _Path(tempfile.mkdtemp())
        lock = threading.Lock()
        current = {"n": 0, "max": 0}

        def stub(_root, stage, _task):
            with lock:
                current["n"] += 1
                current["max"] = max(current["max"], current["n"])
            _time.sleep(0.1)
            with lock:
                current["n"] -= 1
            if stage["id"] != "security":
                return True, "ok"
            return False, "other"

        w.trigger_stage = stub
        items = [(f"k{i}", s, "T", f"{s['id']} prêt (T)") for i, s in enumerate(self._stages())]
        ok, done, failed = w.run_branches(root, items, 1)
        self.assertEqual(current["max"], 1)
        self.assertTrue(ok)
        self.assertEqual(len(done), 2)
        self.assertEqual(len(failed), 1)

    def test_etat_add_remove(self):
        import importlib.util
        import sys
        import tempfile
        from pathlib import Path as _Path
        spec = importlib.util.spec_from_file_location(
            "watch_work_r", str(ROOT / "runtimes" / "opencode" / "scripts" / "watch-work.py"))
        w = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(w)
        root = _Path(tempfile.mkdtemp())
        w.state_agents_add(root, "F-1", "reviewer")
        w.state_agents_add(root, "F-1", "reviewer")
        w.state_agents_add(root, "F-1", "security")
        sys.path.insert(0, str(ROOT / "engine"))
        from state import load_state
        running = load_state(root)["workflow"]["running_agents"]
        self.assertEqual(sorted(running), ["reviewer", "security"])
        w.state_agents_remove(root, "F-1", "reviewer")
        w.state_agents_remove(root, "F-1", "reviewer")
        running = load_state(root)["workflow"]["running_agents"]
        self.assertEqual(running, ["security"])

    def test_max_parallel_garde_fou(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "watch_work_s", str(ROOT / "runtimes" / "opencode" / "scripts" / "watch-work.py"))
        w = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(w)
        self.assertEqual(w.max_parallel_agents({"workflow": {"max_parallel_agents": 2}}), 2)
        self.assertEqual(w.max_parallel_agents({"workflow": {"max_parallel_agents": 0}}), 3)
        self.assertEqual(w.max_parallel_agents({"workflow": {"max_parallel_agents": True}}), 3)
        self.assertEqual(w.max_parallel_agents({}), 3)
        self.assertEqual(w.max_parallel_agents(None), 3)

    def test_classification_echecs(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "watch_work_c", str(ROOT / "runtimes" / "opencode" / "scripts" / "watch-work.py"))
        w = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(w)

        class R:
            stdout = ""
            stderr = ""

        r = R()
        r.stderr = "Error from provider: Rate limit exceeded. Please try again later."
        self.assertEqual(w.classify_failure(r), "quota")
        r.stderr = "429 Too Many Requests: insufficient_quota"
        self.assertEqual(w.classify_failure(r), "quota")
        r.stderr = ""
        r.stdout = "Connection reset by peer, network unreachable"
        self.assertEqual(w.classify_failure(r), "network")
        r.stdout, r.stderr = "", "timed out while waiting for the model"
        self.assertEqual(w.classify_failure(r), "network")
        r.stdout, r.stderr = "Unknown error from agent", ""
        self.assertEqual(w.classify_failure(r), "other")


class TestServices(unittest.TestCase):
    @classmethod
    def _services(cls):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "services_mod", str(ROOT / "runtimes" / "opencode" / "scripts" / "services.py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    @staticmethod
    def _free_port():
        import socket
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            return sock.getsockname()[1]

    def test_cycle_complet(self):
        import sys
        import tempfile
        from pathlib import Path as _Path
        svc = self._services()
        tmp = _Path(tempfile.mkdtemp())
        (_opencode := tmp / ".opencode").mkdir()
        (_opencode / "sayrhazi.yaml").write_text("workflow:\n  name: Sayrhazi\n", encoding="utf-8")
        port = self._free_port()
        url = f"http://localhost:{port}/"
        ok, message = svc.start_service(tmp, "web", f"{sys.executable} -m http.server {port}",
                                        ".", port, url, wait=15)
        self.assertTrue(ok, message)
        rows = svc.service_status(tmp, "web")
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]["alive"])
        self.assertTrue(rows[0]["port_busy"])
        text, err = svc.tail_logs(tmp, "web")
        self.assertEqual(err, "")
        self.assertTrue(text.strip())
        ok, message = svc.stop_service(tmp, "web")
        self.assertTrue(ok, message)
        self.assertFalse(svc.port_busy(port))
        self.assertFalse((tmp / ".opencode" / "state" / "services-web.pid").is_file())

    def test_port_occupe_refuse(self):
        import socket
        import tempfile
        from pathlib import Path as _Path
        svc = self._services()
        tmp = _Path(tempfile.mkdtemp())
        sock = socket.socket()
        sock.bind(("127.0.0.1", 0))
        sock.listen(1)
        port = sock.getsockname()[1]
        try:
            ok, message = svc.start_service(tmp, "web", "dummy", ".", port, None, wait=1)
            self.assertFalse(ok)
            self.assertIn("occupé", message)
        finally:
            sock.close()

    def test_pidfile_perime(self):
        import tempfile
        from pathlib import Path as _Path
        svc = self._services()
        tmp = _Path(tempfile.mkdtemp())
        state = tmp / ".opencode" / "state"
        state.mkdir(parents=True)
        import json
        (state / "services-web.pid").write_text(
            json.dumps({"pid": 2147483647, "port": None}), encoding="utf-8")
        rows = svc.service_status(tmp, "web")
        self.assertFalse(rows[0]["alive"])
        ok, _ = svc.stop_service(tmp, "web")
        self.assertTrue(ok)
        self.assertFalse((state / "services-web.pid").is_file())

    def test_regle_serveurs_instructions(self):
        for agent in ("bamse", "zawadi"):
            body = (ROOT / "core" / "agents" / agent / "instructions.md").read_text(encoding="utf-8")
            self.assertIn("ne tue jamais un processus", body, agent)


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
