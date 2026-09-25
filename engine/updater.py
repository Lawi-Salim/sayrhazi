#!/usr/bin/env python3
"""Update Sayrhazi — met a jour agents + watcher + migre la config.

Copie les fichiers pilotes par le noyau (agent/*.md, watch-work.py) avec
ecrasement. Migre `.opencode/sayrhazi.yaml` en douceur : cles manquantes du
template ajoutees (avec backup horodate dans history/), valeurs existantes
jamais ecrasees, ligne `version:` alignee sur le noyau. Preserve le reste
(opencode.json, AGENTS.md, resume/, history/, features/). Signale les
agent/*.md orphelins.

Usage :
    python update-sayrhazi.py [--project .]

Sorties ASCII uniquement (console Windows PS 5.1). Exit 0 = OK, 2 = NON INSTALLE.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

VERSION_RE = re.compile(r'^\s*version:\s*"([^"]+)"\s*(#.*)?$', re.MULTILINE)
TOP_KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):")


def read_version(yaml_path: Path) -> str | None:
    try:
        m = VERSION_RE.search(yaml_path.read_text(encoding="utf-8", errors="replace"))
    except OSError:
        return None
    return m.group(1).strip() if m else None


def template_block(tmpl_lines: list[str], key: str) -> list[str]:
    """Extrait le bloc `key:` du template (jusqu'a la prochaine cle top-level)."""
    out: list[str] = []
    inside = False
    for line in tmpl_lines:
        if not inside:
            if TOP_KEY_RE.match(line) and line.split(":")[0] == key:
                inside = True
                out.append(line)
        else:
            if TOP_KEY_RE.match(line):
                break
            out.append(line)
    while out and not out[-1].strip():
        out.pop()
    return out


def migrate_config(inst_path: Path, tmpl_path: Path, history_dir: Path) -> tuple[list[str], str | None, list[str]]:
    """Ajoute les cles manquantes sans ecraser. Retourne (ajouts, backup, alertes)."""
    inst_lines = inst_path.read_text(encoding="utf-8", errors="replace").splitlines()
    tmpl_lines = tmpl_path.read_text(encoding="utf-8", errors="replace").splitlines()
    added: list[str] = []
    warns: list[str] = []
    changed = False

    def has(pat: str) -> bool:
        return any(re.search(pat, l) for l in inst_lines)

    # 1. Ancienne cle `database:` -> 3 nouvelles cles (valeur reprise si nom reel).
    if not has(r"^\s*database_type\s*:") and has(r"^\s*database\s*:"):
        idx = next(i for i, l in enumerate(inst_lines) if re.search(r"^\s*database\s*:", l))
        old_val = inst_lines[idx].split(":", 1)[1].split("#", 1)[0].strip().strip("\"'")
        new_block = [l for l in template_block(tmpl_lines, "technical") if re.search(r"^\s*database_(type|driver|name)\s*:", l)]
        if new_block:
            if old_val.lower() not in ("", "none", "null", "~"):
                new_block = [re.sub(r"^(\s*database_name\s*:).*", r"\1 " + old_val, l) if re.search(r"^\s*database_name\s*:", l) else l for l in new_block]
                warns.append(f"ancienne cle database={old_val} reprise comme database_name (a verifier)")
            inst_lines[idx:idx + 1] = new_block
            added.append("technical.database_type/driver/name (remplace database:)")
            changed = True

    # 1b. Cle `designer:` manquante dans une section agents existante.
    if has(r"^\s*architect\s*:") and not has(r"^\s*designer\s*:"):
        idx = next(i for i, l in enumerate(inst_lines) if re.search(r"^\s*architect\s*:", l))
        tmpl_designer = next((l for l in tmpl_lines if re.search(r"^\s*designer\s*:", l)), None)
        if tmpl_designer:
            inst_lines[idx + 1:idx + 1] = [tmpl_designer]
            added.append("agents.designer (cle ajoutee, defaut Ali)")
            changed = True

    # 2. Sections top-level du template integralement absentes -> ajout.
    inst_tops = {m.group(1) for l in inst_lines if (m := TOP_KEY_RE.match(l))}
    tmpl_tops = [m.group(1) for l in tmpl_lines if (m := TOP_KEY_RE.match(l))]
    for key in tmpl_tops:
        if key in ("workflow",) or key in inst_tops:
            continue
        block = template_block(tmpl_lines, key)
        if block:
            anchor = next((i for i, l in enumerate(inst_lines) if TOP_KEY_RE.match(l) and tmpl_tops.index(l.split(":")[0]) > tmpl_tops.index(key)), len(inst_lines))
            inst_lines[anchor:anchor] = ([""] if inst_lines and inst_lines[anchor - 1].strip() else []) + block + [""]
            added.append(key + " (section ajoutee)")
            changed = True
            inst_tops.add(key)

    backup = None
    if changed:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        history_dir.mkdir(parents=True, exist_ok=True)
        backup = str(history_dir / f"sayrhazi-backup-{stamp}.yaml")
        shutil.copy2(inst_path, backup)
        inst_path.write_text("\n".join(inst_lines) + "\n", encoding="utf-8")
    return added, backup, warns


def main() -> int:
    parser = argparse.ArgumentParser(description="Update Sayrhazi (agents + watcher)")
    parser.add_argument("--project", default=".", help="racine du projet a mettre a jour")
    args = parser.parse_args()

    try:
        core = Path(__file__).resolve().parent.parent
    except NameError:
        print("ERREUR : noyau Sayrhazi introuvable.")
        return 2
    if not (core / "runtimes" / "opencode" / "templates" / "sayrhazi.yaml").is_file():
        print("ERREUR : noyau Sayrhazi introuvable (templates/sayrhazi.yaml absent).")
        return 2

    root = Path(args.project).resolve()
    opencode = root / ".opencode"
    markers = {
        ".opencode/sayrhazi.yaml": (opencode / "sayrhazi.yaml").is_file(),
        ".opencode/agent": (opencode / "agent").is_dir(),
        "AGENTS.md": (root / "AGENTS.md").is_file(),
    }
    if not all(markers.values()):
        print("Sayrhazi n'est pas initialise dans : " + str(root))
        for marker, present in markers.items():
            if not present:
                print("  manquant : " + marker)
        print("Lancez d'abord l'installation (fonction `sayrhazi`), pas la mise a jour.")
        return 2

    before = read_version(opencode / "sayrhazi.yaml") or "(illisible)"
    tmpl_yaml = core / "runtimes" / "opencode" / "templates" / "sayrhazi.yaml"
    latest = read_version(tmpl_yaml) or "(inconnue)"

    for d in ("agent", "resume", "history", "features"):
        (opencode / d).mkdir(parents=True, exist_ok=True)

    updated = 0
    adapter_agents = core / "runtimes" / "opencode" / "agents"
    for src in sorted(adapter_agents.glob("*.md")):
        shutil.copy2(src, opencode / "agent" / src.name)
        updated += 1
    watcher = core / "runtimes" / "opencode" / "scripts" / "watch-work.py"
    if watcher.is_file():
        shutil.copy2(watcher, opencode / "watch-work.py")
        updated += 1

    print(f"Sayrhazi mis a jour : version projet={before} -> noyau={latest} (rapports et historique preserves).")
    print(f"Fichiers noyau recopies : {updated}.")

    added, backup, mwarns = migrate_config(opencode / "sayrhazi.yaml", tmpl_yaml, opencode / "history")
    if backup:
        print(f"Config migree (backup: {backup}) :")
        for a in added:
            print("  +" + a)
    for w in mwarns:
        print("  ALERTE: " + w)
    cur = read_version(opencode / "sayrhazi.yaml")
    if cur != latest:
        lines = (opencode / "sayrhazi.yaml").read_text(encoding="utf-8", errors="replace").splitlines()
        for i, l in enumerate(lines):
            m = VERSION_RE.search(l)
            if m:
                tail = " " + m.group(2).strip() if m.group(2) else ""
                lines[i] = '  version: "' + latest + '"' + tail
                break
        (opencode / "sayrhazi.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"version alignee : {cur} -> {latest}")

    core_names = {p.name for p in adapter_agents.glob("*.md")}
    orphans = sorted(p.name for p in (opencode / "agent").glob("*.md") if p.name not in core_names)
    if orphans:
        print("Fichiers agent inconnus du noyau (suppression manuelle conseillee) :")
        for name in orphans:
            print("  " + name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
