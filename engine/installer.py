#!/usr/bin/env python3
"""Installer Sayrhazi — port Python de Install-Sayrhazi.ps1 (multi-plateforme).

Cree .opencode/agent|resume|history|features, recopie agents + watcher
(Force), cree AGENTS.md / sayrhazi.yaml / opencode.json uniquement si
absents. Ne supprime ni ne remplace rapports, historiques ou config.

Usage :
    python engine/installer.py --project <racine>
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def install_project(project: Path, core: Path) -> None:
    opencode = project / ".opencode"
    agent_target = opencode / "agent"
    for d in (agent_target, opencode / "resume", opencode / "history", opencode / "features"):
        d.mkdir(parents=True, exist_ok=True)

    adapter_agents = core / "runtimes" / "opencode" / "agents"
    for src in sorted(adapter_agents.glob("*.md")):
        shutil.copy2(src, agent_target / src.name)

    templates = core / "runtimes" / "opencode" / "templates"
    for name, dest in (("AGENTS.md", project / "AGENTS.md"),
                       ("sayrhazi.yaml", opencode / "sayrhazi.yaml"),
                       ("opencode.json", opencode / "opencode.json")):
        if not dest.is_file():
            shutil.copy2(templates / name, dest)

    watcher = core / "runtimes" / "opencode" / "scripts" / "watch-work.py"
    if watcher.is_file():
        shutil.copy2(watcher, opencode / "watch-work.py")

    readme = project / "SAYRHAZI-README.md"
    if not readme.is_file():
        readme.write_text(
            "# Integration Sayrhazi\n\nLe workflow Sayrhazi est installe dans `.opencode/`. "
            "Completer `.opencode/sayrhazi.yaml` avant la premiere tache.\n",
            encoding="utf-8",
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Installer Sayrhazi")
    parser.add_argument("--project", default=".", help="racine du projet cible")
    args = parser.parse_args()

    try:
        core = Path(__file__).resolve().parent.parent
    except NameError:
        print("ERREUR : noyau introuvable.")
        return 2
    if not (core / "runtimes" / "opencode" / "templates" / "sayrhazi.yaml").is_file():
        print("ERREUR : noyau incomplet (templates/sayrhazi.yaml absent).")
        return 2
    project = Path(args.project).resolve()
    if not project.is_dir():
        print("ERREUR : projet introuvable : " + str(project))
        return 2
    install_project(project, core)
    print("Sayrhazi installe dans : " + str(project))
    print("A completer avant usage : " + str(project / ".opencode" / "sayrhazi.yaml"))
    print("Aucun conteneur Docker n'a ete cree. Docker reste une decision du projet applicatif.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
