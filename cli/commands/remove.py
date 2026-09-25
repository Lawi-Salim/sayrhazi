#!/usr/bin/env python3
"""CLI remove — retrait prudent de l'integration Sayrhazi (stdlib uniquement).

Par defaut : simulation (liste, ne supprime rien). Avec --yes : supprime
uniquement les fichiers pilotes par le noyau (agent/*.md, watch-work.py).
JAMAIS touches : sayrhazi.yaml, opencode.json, AGENTS.md, resume/, history/,
features/ (suppression manuelle volontaire).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Retirer Sayrhazi (prudent)")
    parser.add_argument("--project", default=".")
    parser.add_argument("--yes", action="store_true", help="supprimer vraiment")
    args = parser.parse_args()

    root = Path(args.project).resolve()
    opencode = root / ".opencode"
    try:
        core = Path(__file__).resolve().parent.parent.parent
        core_names = {p.name for p in (core / "runtimes" / "opencode" / "agents").glob("*.md")}
    except OSError:
        core_names = set()
    targets = [p for p in (opencode / "agent").glob("*.md") if p.name in core_names] if (opencode / "agent").is_dir() else []
    watcher = opencode / "watch-work.py"
    if watcher.is_file():
        targets.append(watcher)
    if not targets:
        print("Rien a retirer (aucun fichier noyau trouve).")
        return 3
    print("Fichiers noyau concernes :")
    for t in targets:
        print("  " + str(t.relative_to(root)))
    print("JAMAIS touches : sayrhazi.yaml, opencode.json, AGENTS.md, resume/, history/, features/.")
    if not args.yes:
        print("Simulation : relancez avec --yes pour supprimer.")
        return 0
    for t in targets:
        t.unlink()
    print(f"Retires : {len(targets)} fichier(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
