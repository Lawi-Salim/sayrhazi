#!/usr/bin/env python3
"""Validation sans dépendance externe d'une instance Sayrhazi."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED_AGENTS = {"bamse.md", "hadji.md", "hifadhui.md", "lawibrahim.md", "zawadi.md"}
REQUIRED_DIRS = ("agent", "resume", "history", "features")
REQUIRED_CONFIG_KEYS = (
    "workflow:",
    "  name: Sayrhazi",
    "project:",
    "  name:",
    "agents:",
    "  architect:",
    "  builder:",
    "  reviewer:",
    "  security:",
    "  qa:",
    "commands:",
    "quality:",
)


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def main() -> int:
    parser = argparse.ArgumentParser(description="Valide une installation Sayrhazi")
    parser.add_argument("project", help="Racine du projet a controler")
    args = parser.parse_args()

    root = Path(args.project).resolve()
    install_errors: list[str] = []
    config_notes: list[str] = []
    opencode = root / ".opencode"
    config = opencode / "sayrhazi.yaml"

    if not root.is_dir():
        fail(f"Projet introuvable: {root}", install_errors)
    if not opencode.is_dir():
        fail("Dossier .opencode absent", install_errors)
    if not config.is_file():
        fail(".opencode/sayrhazi.yaml absent", install_errors)
    else:
        text = config.read_text(encoding="utf-8")
        for key in REQUIRED_CONFIG_KEYS:
            if key not in text:
                fail(f"Cle de configuration absente: {key}", install_errors)
        remaining = [(i + 1, line.strip()) for i, line in enumerate(text.splitlines()) if re.search(r"(^|:\s*)A_COMPLETER\b", line)]
        if remaining:
            fail(f"Configuration incomplete : {len(remaining)} valeur(s) A_COMPLETER restante(s).", config_notes)
            for lineno, line in remaining:
                fail(f"  sayrhazi.yaml:{lineno}: {line}", config_notes)
        if re.search(r"^\s*name:\s*$", text, re.MULTILINE):
            fail("project.name est vide", config_notes)

    agent_dir = opencode / "agent"
    if not agent_dir.is_dir():
        fail("Dossier .opencode/agent absent", install_errors)
    else:
        actual = {p.name for p in agent_dir.glob("*.md")}
        for missing in sorted(REQUIRED_AGENTS - actual):
            fail(f"Agent absent: {missing}", install_errors)

    for directory in REQUIRED_DIRS:
        if not (opencode / directory).is_dir():
            fail(f"Dossier .opencode/{directory} absent", install_errors)

    if not (root / "AGENTS.md").is_file():
        fail("AGENTS.md absent a la racine du projet", install_errors)

    if install_errors:
        print("Installation Sayrhazi echouee :")
        for error in install_errors:
            print(f"- {error}")
        return 1

    if config_notes:
        print("Sayrhazi installe avec succes.")
        for note in config_notes:
            print(f"- {note}")
        print("Completez .opencode/sayrhazi.yaml avant utilisation.")
        return 1

    print(f"Sayrhazi installe et configure avec succes : {root}")
    print("Les cinq agents et les dossiers de suivi sont presents.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
