# Lot 4 — Watcher généralisé (brouillon local, non suivi)

Source : `Idee-Automation-Sayrhazi.md` §8 (étapes 5.1-5.4). Dépend des Lots 1-3.

## 4.1 Généraliser le déclenchement (garder `build.txt → Hadji`)

Extraire les opérations communes : stabilité, validation rapport (8 points Lot 1), verrouillage, journalisation.

## 4.2 Lire `.opencode/workflow.yaml`

Plus d'agents ni conditions en dur dans le watcher. Inconnue → signalée, jamais devinée.

## 4.3 Ajouter l'état

Écrire `state/workflow-state.yaml`, archiver les événements (journal dédié).

## 4.4 Ajouter les conditions

`sécurité`, `QA visuelle`, `design` et futures exigences — déclarées uniquement.

## 4.5 Renommage éventuel (non prioritaire)

`watch-work.py` → `workflow-runner.py` ou `sayrhazi-runner.py`. Compatibilité avec projets installés d'abord (chemin `.opencode/watch-work.py` déjà déployé).

## Critère de sortie

Plusieurs transitions séquentielles gérées, sans doublons, avec journal ; V1 réaliste : `plan validé → Bamse (1x) → build valide → Hadji auto → review → Zawadi si requis`, `task_id` conservé, reprise OK, Hifadhui/Ali jamais sans condition.
