"""
watch-work.py — orchestrateur Sayrhazi build.txt TERMINÉ -> Hadji.

Surveille `.opencode/resume/build.txt`. Déclenche Hadji uniquement si :
- le fichier est stable (pas en cours d'écriture),
- il contient un `task_id` stable et un statut `TERMINÉ`,
- ce couple (task_id + hash) n'a pas déjà été déclenché.

Ne déclenche jamais Bamse, ne boucle pas après review négative,
ne publie / supprime rien. Vérifie que `review.txt` est produit.

Sans dépendance externe. Windows / macOS / Linux.

Usage :
    python .opencode/watch-work.py [--once] [--check] [--timeout SEC]
    --once    : une seule vérification puis sortie (0 = déclenché, 1 = rien)
    --check   : valide la config sans surveiller (idéal pour tests)
    --timeout : durée max de surveillance en secondes (0 = infini)
"""

import argparse
import hashlib
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

IS_WINDOWS = os.name == "nt"
AGENT_TO_TRIGGER = "hadji"
POLL_INTERVAL_SECONDS = 3
DEBOUNCE_SECONDS = 2

TASK_RE = re.compile(r"^\s*task_id\s*:\s*(\S+)\s*$", re.MULTILINE | re.IGNORECASE)
STATUS_RE = re.compile(r"^\s*status\s*:\s*(\S.*?)\s*$", re.MULTILINE | re.IGNORECASE)


def log(message: str) -> None:
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}", flush=True)


def find_project_root(start: Path) -> Optional[Path]:
    """Remonte depuis start jusqu'à trouver .opencode/sayrhazi.yaml."""
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / ".opencode" / "sayrhazi.yaml").is_file():
            return candidate
        if (candidate / ".opencode" / "agent").is_dir() and (candidate / "AGENTS.md").is_file():
            return candidate
    # Cas script installé dans .opencode/ : racine = parent de .opencode/
    if start.name == ".opencode" and (start / "sayrhazi.yaml").is_file():
        return start.parent
    try:
        script_parent = Path(__file__).resolve().parent
        if script_parent.name == ".opencode":
            return script_parent.parent
        if (script_parent.parent / ".opencode" / "sayrhazi.yaml").is_file():
            return script_parent.parent
    except NameError:
        pass
    return None


def file_hash(path: Path) -> Optional[str]:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except FileNotFoundError:
        return None
    except OSError as exc:
        log(f"ERREUR lecture {path}: {exc}")
        return None


def parse_build_report(path: Path) -> Tuple[Optional[str], Optional[str]]:
    """Extrait (task_id, status) depuis build.txt. Retourne (None, None) si absent."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return None, None
    except OSError as exc:
        log(f"ERREUR lecture {path}: {exc}")
        return None, None
    task = TASK_RE.search(text)
    status = STATUS_RE.search(text)
    task_id = task.group(1).strip() if task else None
    stat = status.group(1).strip().upper() if status else None
    return task_id, stat


def check_opencode_available() -> bool:
    try:
        cmd = "opencode --version" if IS_WINDOWS else ["opencode", "--version"]
        result = subprocess.run(cmd, capture_output=True, text=True, shell=IS_WINDOWS, encoding="utf-8", errors="replace")
        if result.returncode == 0:
            log(f"opencode détecté : {result.stdout.strip()}")
            return True
        log("ATTENTION : 'opencode --version' a échoué.")
        return False
    except FileNotFoundError:
        log("ATTENTION : commande 'opencode' introuvable dans le PATH.")
        return False


def trigger_agent(project_root: Path, task_id: str) -> bool:
    prompt = f"Review Sayrhazi task {task_id} : lis .opencode/resume/build.txt et produis review.txt"
    log(f"build.txt TERMINÉ ({task_id}) -> appel de {AGENT_TO_TRIGGER}...")
    try:
        if IS_WINDOWS:
            command_str = f'opencode run --agent {AGENT_TO_TRIGGER} "{prompt}"'
            result = subprocess.run(command_str, cwd=str(project_root), capture_output=True, text=True, shell=True, timeout=600, encoding="utf-8", errors="replace")
        else:
            result = subprocess.run(["opencode", "run", "--agent", AGENT_TO_TRIGGER, prompt], cwd=str(project_root), capture_output=True, text=True, timeout=600, encoding="utf-8", errors="replace")
    except FileNotFoundError:
        log("ERREUR : commande 'opencode' introuvable.")
        return False
    except subprocess.TimeoutExpired:
        log("ERREUR : timeout 600s sur appel Hadji.")
        return False
    except Exception as exc:
        log(f"ERREUR inattendue : {exc}")
        return False
    if result.stdout:
        print(result.stdout)
    if result.returncode != 0:
        log(f"opencode erreur {result.returncode} :")
        if result.stderr:
            print(result.stderr)
        return False
    log(f"{AGENT_TO_TRIGGER} terminé pour {task_id}.")
    review = project_root / ".opencode" / "resume" / "review.txt"
    if not review.is_file():
        log("ATTENTION : review.txt absent après déclenchement. Vérifie la session Hadji.")
        return False
    text = review.read_text(encoding="utf-8", errors="replace")
    if task_id not in text:
        log(f"ATTENTION : review.txt ne mentionne pas {task_id}.")
        return False
    log(f"review.txt vérifié pour {task_id}.")
    return True


def should_trigger(build_file: Path, last_trigger: str) -> Tuple[bool, str, Optional[str]]:
    """Retourne (déclencher?, clé_unique, raison)."""
    current_hash = file_hash(build_file)
    if current_hash is None:
        return False, last_trigger, "build.txt absent"
    # Stabilité : relire après debounce
    time.sleep(DEBOUNCE_SECONDS)
    stable_hash = file_hash(build_file)
    if stable_hash != current_hash:
        return False, last_trigger, "fichier instable (écriture en cours)"
    task_id, status = parse_build_report(build_file)
    if not task_id:
        return False, last_trigger, "task_id absent — rapport incomplet, refusé"
    if status != "TERMINÉ":
        return False, last_trigger, f"status={status or 'absent'} — attendu TERMINÉ, refusé"
    key = f"{task_id}:{stable_hash}"
    if key == last_trigger:
        return False, last_trigger, f"{task_id} déjà déclenché"
    return True, key, f"{task_id} prêt"


def main() -> int:
    parser = argparse.ArgumentParser(description="Watcher Sayrhazi build.txt -> Hadji")
    parser.add_argument("--once", action="store_true", help="une seule vérification")
    parser.add_argument("--check", action="store_true", help="valide config sans surveiller")
    parser.add_argument("--timeout", type=int, default=0, help="durée max en secondes (0=infini)")
    args = parser.parse_args()

    root = find_project_root(Path.cwd())
    if root is None:
        log("ERREUR : racine projet introuvable (.opencode/sayrhazi.yaml absent). Lance depuis le projet.")
        return 2
    log(f"Racine du projet : {root}")
    build_file = root / ".opencode" / "resume" / "build.txt"
    log(f"Surveillance de : {build_file}")

    if not (root / ".opencode" / "sayrhazi.yaml").is_file():
        log("ERREUR : .opencode/sayrhazi.yaml absent.")
        return 2
    if args.check:
        ok = check_opencode_available()
        task_id, status = parse_build_report(build_file) if build_file.is_file() else (None, None)
        log(f"check: build.txt task_id={task_id} status={status}")
        log("check OK" if ok else "check OK (opencode absent, surveillance possible)")
        return 0

    check_opencode_available()
    if not os.access(root, os.W_OK):
        log("ERREUR : racine projet non inscriptible.")
        return 2

    last_trigger = ""
    start = time.time()

    def one_pass() -> bool:
        nonlocal last_trigger
        trigger, key, reason = should_trigger(build_file, last_trigger)
        log(f"État : {reason}")
        if trigger and trigger_agent(root, parse_build_report(build_file)[0] or "UNKNOWN"):
            last_trigger = key
            return True
        if trigger:
            log("Échec déclenchement, on réessaiera au prochain passage.")
        return False

    if args.once:
        return 0 if one_pass() else 1

    log("En attente... (Ctrl+C pour arrêter)")
    last_hash_seen: Optional[str] = None
    try:
        while True:
            if args.timeout and (time.time() - start) > args.timeout:
                log("Timeout atteint, arrêt.")
                return 1
            current = file_hash(build_file)
            if current != last_hash_seen:
                last_hash_seen = current
                one_pass()
            time.sleep(POLL_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        log("Arrêt (Ctrl+C).")
        return 0


if __name__ == "__main__":
    sys.exit(main())
