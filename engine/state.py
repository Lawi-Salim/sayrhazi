#!/usr/bin/env python3
"""State Sayrhazi — lecture/ecriture de .opencode/state/workflow-state.yaml.

Fondation (lots automation) : vue de coordination {task_id, status,
current/completed/pending/blocked, running}. Les rapports restent les preuves.
Stdlib uniquement.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from sayrhazi_config import parse_simple_yaml
except ImportError:  # pragma: no cover
    parse_simple_yaml = None  # type: ignore

STATUSES = ("PENDING", "READY", "RUNNING", "TERMINÉ", "VALIDÉ",
            "VALIDÉ_AVEC_RÉSERVES", "CORRECTIONS_NÉCESSAIRES",
            "BLOCKED", "FAILED", "CANCELLED")


def default_state(task_id: str) -> dict:
    return {"workflow": {"task_id": task_id, "status": "PENDING",
                         "current_stages": [], "completed_stages": [],
                         "pending_stages": [], "blocked_stages": [],
                         "running_agents": []}}


def _scalar(value) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    s = str(value)
    if s == "" or any(c in s for c in ":#{}[],&*?|-<>!=@`\"'"):
        return '"' + s.replace('"', '\\"') + '"'
    return s


def _emit(value, indent: int = 0) -> list[str]:
    pad = "  " * indent
    if isinstance(value, dict):
        lines: list[str] = []
        for k, v in value.items():
            if isinstance(v, dict):
                lines.append(pad + str(k) + ":")
                lines.extend(_emit(v, indent + 1))
            elif isinstance(v, list):
                # Listes inline (flow) : le parseur ne supporte que ce format.
                lines.append(pad + str(k) + ": [" + ", ".join(_scalar(x) for x in v) + "]")
            else:
                lines.append(pad + str(k) + ": " + _scalar(v))
        return lines
    if isinstance(value, list):
        # Style flow ([a, b]) : seul format de liste supporte par le parseur.
        return [pad + "[" + ", ".join(_scalar(v) for v in value) + "]"]
    return [pad + _scalar(value)]


def state_path(project_root: Path | str) -> Path:
    return Path(project_root) / ".opencode" / "state" / "workflow-state.yaml"


def save_state(project_root: Path | str, state: dict) -> Path:
    path = state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(_emit(state)) + "\n", encoding="utf-8")
    return path


def load_state(project_root: Path | str) -> dict | None:
    if parse_simple_yaml is None:
        raise RuntimeError("parseur indisponible")
    path = state_path(project_root)
    if not path.is_file():
        return None
    data, err = parse_simple_yaml(path.read_text(encoding="utf-8", errors="replace"))
    if err:
        raise ValueError("etat illisible : " + err)
    return data
