#!/usr/bin/env python3
"""Contrats Sayrhazi Lot 1 — parsing tolerant et validation des rapports/taches.

Reference normative : core/schemas/report.schema.yaml et task.schema.yaml.
Stdlib uniquement. Utilise par `tunda`/`checker` (section rapports, non bloquante)
et par le watcher (Lot 4, points 3/4/5/7 du contrat).

Points de validation avant transition (docs/reports.md) :
  1. fichier attendu existe, 2. stable apres ecriture -> runtime (watcher Lot 4) ;
  3. task_id = tache active, 4. statut autorise, 5. auteur = role attendu -> ici ;
  6. pas d'execution identique en cours, 8. delai max -> runtime (watcher Lot 4) ;
  7. pas de rapport de sortie equivalent -> ici via `output_text`.
"""

from __future__ import annotations

import re
from datetime import datetime

ROLES = ("architect", "designer", "builder", "reviewer", "security", "qa")

TASK_STATUSES = ("À IMPLÉMENTER", "INFORMATIF", "EN COURS", "TERMINÉ", "BLOQUÉ", "VALIDÉ")

ROLE_STATUSES: dict[str, tuple[str, ...]] = {
    # plan.txt (Lawibrahim)
    "architect": ("À IMPLÉMENTER", "INFORMATIF", "VALIDÉ"),
    # design.txt (Ali)
    "designer": ("PROPOSÉ", "VALIDÉ"),
    # build.txt (Bamse)
    "builder": ("EN COURS", "TERMINÉ", "BLOQUÉ"),
    # review.txt (Hadji), security.txt (Hifadhui)
    "reviewer": ("VALIDÉ", "VALIDÉ AVEC RÉSERVES", "CORRECTIONS NÉCESSAIRES"),
    "security": ("VALIDÉ", "VALIDÉ AVEC RÉSERVES", "CORRECTIONS NÉCESSAIRES"),
    # qa.txt (Zawadi)
    "qa": ("VALIDÉ", "VALIDÉ AVEC RÉSERVES", "CORRECTIONS NÉCESSAIRES", "À COMPLÉTER"),
}

REQUIRED_REPORT_FIELDS = ("task_id", "agent", "status", "completed_at", "summary")
REQUIRED_TASK_FIELDS = ("task_id", "title", "status")

TASK_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{2,}$")
KEY_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$")
ITEM_RE = re.compile(r"^\s*-\s+(.*)$")

# Indicateur de tache -> role exige dans agents_required (Lot 1, coherence).
INDICATOR_ROLES = (
    ("security_required", "security"),
    ("visual_qa_required", "qa"),
    ("design_required", "designer"),
)


def normalize_status(value: object) -> str:
    """`VALIDÉ_AVEC_RÉSERVES` -> `VALIDÉ AVEC RÉSERVES` (casse/espaces normalises)."""
    text = str(value).strip().upper().replace("_", " ")
    return re.sub(r"\s+", " ", text)


def _clean(value: str) -> str:
    text = value.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in ("'", '"'):
        text = text[1:-1]
    return text.strip()


def _flow_list(value: str) -> list[str] | None:
    text = value.strip()
    if not (text.startswith("[") and text.endswith("]")):
        return None
    inner = text[1:-1].strip()
    if not inner:
        return []
    return [_coerce(_clean(p)) for p in inner.split(",")]


def _coerce(value: str):
    """`true`/`false` -> bool, `null`/`~` -> None, sinon la chaine telle quelle."""
    low = value.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    if low in ("null", "~"):
        return None
    return value


def parse_report(text: str) -> dict:
    """Parse tolerant d'un rapport/tache : lignes `cle: valeur`, listes `- ` ou `[a, b]`.

    Titres `#`, lignes libres et puces hors cle ignores. Premiere occurrence gagne
    (le corps du rapport peut rementionner un champ). Cles en minuscules.
    """
    data: dict = {}
    pending_key: str | None = None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            pending_key = None
            continue
        item = ITEM_RE.match(raw)
        if item and pending_key and pending_key not in data:
            data[pending_key].append(_coerce(_clean(item.group(1))))
            continue
        match = KEY_RE.match(raw)
        pending_key = None
        if not match:
            continue
        key = match.group(1).lower()
        if key in data:
            continue
        value = match.group(2).strip()
        if value == "":
            data[key] = []
            pending_key = key
            continue
        flow = _flow_list(value)
        data[key] = flow if flow is not None else _coerce(_clean(value))
    return data


def _parse_moment(value: object) -> bool:
    try:
        datetime.fromisoformat(str(value).strip().strip("\"'").replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def validate_report(data: dict) -> list[str]:
    """Valide un rapport contre le contrat Lot 1. Retourne les violations."""
    errors: list[str] = []
    for field in REQUIRED_REPORT_FIELDS:
        if field not in data or data[field] in ("", [], None):
            errors.append(f"champ requis manquant `{field}`")
    task_id = data.get("task_id")
    if task_id and not TASK_ID_RE.match(str(task_id)):
        errors.append(f"task_id `{task_id}` instable (lettres/chiffres/._-, min 3 caracteres)")
    agent = str(data.get("agent", "")).strip().lower()
    if agent and agent not in ROLES:
        errors.append(f"agent `{data.get('agent')}` inconnu (attendu : {list(ROLES)})")
    status = data.get("status")
    if status and agent in ROLES and normalize_status(status) not in ROLE_STATUSES[agent]:
        errors.append(
            f"status `{status}` non autorise pour {agent} "
            f"(attendu : {list(ROLE_STATUSES[agent])})"
        )
    completed = data.get("completed_at")
    if completed and not _parse_moment(completed):
        errors.append(f"completed_at `{completed}` non ISO 8601")
    version = data.get("version")
    if version and _parse_moment(version):
        errors.append("champ `version` horodatage refuse, utiliser `completed_at`")
    next_agents = data.get("next_agents")
    if next_agents:
        agents = next_agents if isinstance(next_agents, list) else [next_agents]
        for name in agents:
            if str(name).strip().lower() not in ROLES:
                errors.append(f"next_agents `{name}` inconnu (attendu : {list(ROLES)})")
    return errors


def validate_task(data: dict) -> list[str]:
    """Valide une tache contre le contrat Lot 1 (champs + coherence indicateurs)."""
    errors: list[str] = []
    for field in REQUIRED_TASK_FIELDS:
        if field not in data or data[field] in ("", [], None):
            errors.append(f"champ requis manquant `{field}`")
    task_id = data.get("task_id")
    if task_id and not TASK_ID_RE.match(str(task_id)):
        errors.append(f"task_id `{task_id}` instable (lettres/chiffres/._-, min 3 caracteres)")
    status = data.get("status")
    if status and normalize_status(status) not in TASK_STATUSES:
        errors.append(f"status `{status}` non autorise (attendu : {list(TASK_STATUSES)})")
    required = data.get("agents_required")
    if required is not None:
        agents = required if isinstance(required, list) else [required]
        for name in agents:
            if str(name).strip().lower() not in ROLES:
                errors.append(f"agents_required `{name}` inconnu (attendu : {list(ROLES)})")
        for indicator, role in INDICATOR_ROLES:
            if data.get(indicator) is True and role not in [str(a).strip().lower() for a in agents]:
                errors.append(f"{indicator}: true exige `{role}` dans agents_required")
    return errors


def check_transition(
    data: dict,
    *,
    expected_agent: str,
    expected_task_id: str,
    allowed_statuses: tuple[str, ...] | None = None,
    output_text: str | None = None,
) -> list[str]:
    """Points 3/4/5/7 du contrat avant transition. Retourne les violations."""
    errors: list[str] = []
    if str(data.get("task_id", "")).strip() != expected_task_id:
        errors.append(f"task_id `{data.get('task_id')}` != tache active {expected_task_id} (point 3)")
    if str(data.get("agent", "")).strip().lower() != expected_agent:
        errors.append(f"agent `{data.get('agent')}` != role attendu {expected_agent} (point 5)")
    allowed = allowed_statuses or ROLE_STATUSES.get(expected_agent, ())
    if normalize_status(data.get("status", "")) not in [normalize_status(s) for s in allowed]:
        errors.append(f"status `{data.get('status')}` non autorise pour cette transition (point 4)")
    if output_text is not None and expected_task_id not in output_text:
        errors.append("rapport de sortie absent ou sans le task_id actif (point 7)")
    return errors
