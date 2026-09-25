#!/usr/bin/env python3
"""CLI Sayrhazi — point d'entree multi-plateforme (stdlib uniquement).

Usage :
    python cli/main.py install [--project .]
    python cli/main.py check [sayrhazi] [--project .]
    python cli/main.py update [--project .]
    python cli/main.py remove [--project .] [--yes]
    python cli/main.py info [--project .]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

COMMANDS = ("install", "check", "update", "remove", "info")


def main() -> int:
    parser = argparse.ArgumentParser(description="CLI Sayrhazi")
    parser.add_argument("command", choices=COMMANDS)
    parser.add_argument("--project", default=".")
    parser.add_argument("--yes", action="store_true", help="remove : supprimer vraiment (defaut : simulation)")
    args = parser.parse_args()

    here = Path(__file__).resolve().parent
    target = here / "commands" / (args.command + ".py")
    cmd = [sys.executable, str(target)]
    if args.command == "check":
        cmd += ["sayrhazi", "--project", args.project]
    else:
        cmd += ["--project", args.project]
    if args.command == "remove" and args.yes:
        cmd += ["--yes"]
    return subprocess.run(cmd).returncode


if __name__ == "__main__":
    sys.exit(main())
