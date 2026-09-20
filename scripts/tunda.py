#!/usr/bin/env python3
"""Tunda — petit check optionnel de la configuration Sayrhazi d'un projet.

Usage :
    python tunda.py sayrhazi [--project .]
    tunda sayrhazi        (via alias PowerShell, depuis n'importe quel projet)

Sorties ASCII uniquement (console Windows PS 5.1). Exit 0 = VALIDE, 1 = INVALIDE.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_AGENTS = ("bamse.md", "hadji.md", "hifadhui.md", "lawibrahim.md", "zawadi.md")
REQUIRED_DIRS = ("agent", "resume", "history", "features")
REQUIRED_CONFIG_KEYS = ("workflow:", "  name: Sayrhazi", "project:", "  name:", "agents:", "commands:", "quality:")


def main() -> int:
    parser = argparse.ArgumentParser(description="Tunda Sayrhazi config check")
    parser.add_argument("sub", nargs="?", default="sayrhazi", help="sous-commande (seule 'sayrhazi' supportee)")
    parser.add_argument("--project", default=".", help="racine du projet a controler")
    args = parser.parse_args()

    if args.sub != "sayrhazi":
        print(f"[KO] sous-commande inconnue: {args.sub} (usage: tunda sayrhazi)")
        return 1

    root = Path(args.project).resolve()
    opencode = root / ".opencode"
    problems: list[str] = []
    warns: list[str] = []

    def ok(msg: str) -> None:
        print(f"[OK] {msg}")

    def ko(msg: str) -> None:
        print(f"[KO] {msg}")
        problems.append(msg)

    def warn(msg: str) -> None:
        print(f"[WARN] {msg}")
        warns.append(msg)

    print(f"Tunda sayrhazi — projet : {root}")

    # 0. Porte d'entree : Sayrhazi est-il initialise dans ce projet ?
    init_markers = {
        ".opencode/sayrhazi.yaml": (opencode / "sayrhazi.yaml").is_file(),
        ".opencode/agent": (opencode / "agent").is_dir(),
        "AGENTS.md": (root / "AGENTS.md").is_file(),
    }
    if not all(init_markers.values()):
        print("[KO] Sayrhazi n'est pas initialise dans ce projet.")
        for marker, present in init_markers.items():
            if not present:
                print(f"  manquant : {marker}")
        print("Veuillez integrer Sayrhazi avec `sayrhazi`, puis completer .opencode/sayrhazi.yaml.")
        print("Tunda sayrhazi: NON INSTALLE")
        return 2

    # 1. Structure
    ok(".opencode present")

    for d in REQUIRED_DIRS:
        if (opencode / d).is_dir():
            ok(f".opencode/{d} present")
        else:
            ko(f".opencode/{d} absent")

    # 2. Agents
    agent_dir = opencode / "agent"
    if agent_dir.is_dir():
        actual = {p.name for p in agent_dir.glob("*.md")}
        missing = [a for a in REQUIRED_AGENTS if a not in actual]
        if not missing:
            ok("5 agents presents")
        else:
            for m in missing:
                ko(f"agent absent: {m}")
    else:
        ko(".opencode/agent absent")

    # 3. AGENTS.md
    agents_md = root / "AGENTS.md"
    if agents_md.is_file():
        ok("AGENTS.md present")
        try:
            am = agents_md.read_text(encoding="utf-8", errors="replace")
            am_sans_code = re.sub(r"`[^`]*`", "", am)
            if "A_COMPLETER" in am_sans_code:
                ko("AGENTS.md contient encore A_COMPLETER")
            if re.search(r"^\s*-\s*\.\.\.\s*$", am, re.MULTILINE):
                warn("AGENTS.md §4 local non rempli ('- ...' restant)")
        except OSError as exc:
            ko(f"AGENTS.md illisible: {exc}")
    else:
        ko("AGENTS.md absent a la racine du projet")

    # 4. sayrhazi.yaml
    config = opencode / "sayrhazi.yaml"
    if not config.is_file():
        ko(".opencode/sayrhazi.yaml absent")
    else:
        try:
            text = config.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            ko(f"sayrhazi.yaml illisible: {exc}")
            text = ""
        if text:
            for key in REQUIRED_CONFIG_KEYS:
                if key in text:
                    ok(f"cle config presente: {key.strip()}")
                else:
                    ko(f"cle config absente: {key.strip()}")
            remaining = [(i + 1, l.strip()) for i, l in enumerate(text.splitlines()) if re.search(r"(^|:\s*)A_COMPLETER\b", l)]
            if not remaining:
                ok("0 A_COMPLETER dans sayrhazi.yaml")
            else:
                ko(f"{len(remaining)} A_COMPLETER restants dans sayrhazi.yaml:")
                for lineno, line in remaining:
                    print(f"  sayrhazi.yaml:{lineno}: {line}")
            if re.search(r"^\s*name:\s*$", text, re.MULTILINE):
                ko("project.name est vide")

    # 5. opencode.json
    oj = opencode / "opencode.json"
    if not oj.is_file():
        ko(".opencode/opencode.json absent")
    else:
        try:
            json.loads(oj.read_text(encoding="utf-8", errors="replace"))
            ok("opencode.json JSON valide")
        except (OSError, json.JSONDecodeError) as exc:
            ko(f"opencode.json invalide: {exc}")

    # 6. watcher (recommande, non bloquant strict)
    if (opencode / "watch-work.py").is_file():
        ok("watch-work.py present")
    else:
        warn("watch-work.py absent (relance Sayrhazi-Install pour l'ajouter)")

    if problems:
        print(f"Tunda sayrhazi: INVALIDE ({len(problems)} probleme(s), {len(warns)} alerte(s))")
        return 1
    if warns:
        print(f"Tunda sayrhazi: VALIDE avec {len(warns)} alerte(s)")
    else:
        print("Tunda sayrhazi: VALIDE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
