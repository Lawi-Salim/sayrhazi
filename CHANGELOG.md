# Changelog Sayrhazi

## 0.2.1 — 2026-09-20

- Nouvelle commande `update sayrhazi` (fonction de profil) : réinstalle agents + watcher, affiche `version projet -> noyau`, signale les `agent/*.md` orphelins, relance le check. Config, rapports et historique préservés. Documentée dans `docs/installation.md`.
- `tunda sayrhazi` compare la version installée (`workflow.version`) au noyau : `[OK] version a jour` ou simple invitation `[WARN] ... lance 'update sayrhazi'`, jamais bloquant.

## 0.2.0 — 2026-09-19

- Système de nomination des agents : noms d'affichage configurables par projet via `agents:` (`architect`, `builder`, `reviewer`, `security`, `qa`) avec défauts publics ; fichiers `agent/*.md` et rôles stables, références croisées par rôle. `agents` désormais requis (schéma, modèle, validateurs).

## 0.1.8 — 2026-09-19

- `tunda sayrhazi` vérifie d'abord si Sayrhazi est initialisé (porte d'entrée : `sayrhazi.yaml` + `agent/` + `AGENTS.md`). Sinon, verdict `NON INSTALLE` (exit 2) avec consigne d'intégrer via `sayrhazi`, au lieu de noyer l'utilisateur dans la checklist.

## 0.1.7 — 2026-09-19

- `validate-sayrhazi.py` distingue échec d'installation (`Installation Sayrhazi echouee`) et configuration incomplète (`Sayrhazi installe avec succes. Configuration incomplete : N valeur(s)...`) vs succès complet (`Sayrhazi installe et configure avec succes`).

## 0.1.6 — 2026-09-19

- Règle commune : réponses et rapports en français (sauf demande contraire), aucun emoji. Ajoutée dans `agents/zawadi.md`, `template/AGENTS.md` (§2) et `docs/agents.md`.

## 0.1.5 — 2026-09-19

- Docs alignées sur l'état réel : présentation obligatoire (`agents.md`), arborescence avec `opencode.json` + `watch-work.py` (`architecture.md`), watcher actuel au présent (`automation.md`), install depuis n'importe quel projet + `tunda sayrhazi` (`installation.md`), format `task_id:` / `status:` exigé par le watcher (`reports.md`).

## 0.1.4 — 2026-09-19

- Template `sayrhazi.yaml` : `runtime.local_url` vaut désormais `http://localhost:5173` par défaut (modifiable, `null` si aucun serveur local) au lieu de `A_COMPLETER`. Ne s'applique qu'aux nouvelles installations, les configs existantes ne sont jamais écrasées.

## 0.1.3 — 2026-09-19

- Nouveau check optionnel `tunda sayrhazi` (`scripts/tunda.py` + fonction profil) : checklist ASCII point par point, 0 `A_COMPLETER` exige, alertes §4 et watcher.

## 0.1.2 — 2026-09-19

- `Install-Sayrhazi.ps1` : messages ASCII (fix mojibake PowerShell 5.1 sans BOM).
- `validate-sayrhazi.py` : sorties ASCII (fix caracteres bizarres en console Windows) + liste le nombre et les lignes `sayrhazi.yaml:<n>` de chaque `A_COMPLETER` restant.

## 0.1.1 — 2026-09-19

- Tous les agents se présentent avec `project.name`, type et stack lus dans `sayrhazi.yaml` ; suppression des noms en dur.
- Correction Zawadi : chemin `.opencode/resume/build.txt` et verdict toujours avec nom du projet.
- `template/AGENTS.md` réécrit comme vrai template projet ; règles du noyau déplacées vers `AGENTS.md` racine.
- `Install-Sayrhazi.ps1` copie désormais `opencode.json` ; PS + sh installent `watch-work.py` dans `.opencode/`.
- `watch-work.py` durci : détection racine robuste, déclenchement uniquement sur `task_id` + `status: TERMINÉ`, anti-double, vérif `review.txt`, modes `--check` / `--once`.

## 0.1.0 — 2026-09-15

- Création du noyau portable Sayrhazi.
- Ajout des rôles génériques Lawibrahim, Bamse, Hadji, Hifadhui et Zawadi.
- Ajout du modèle `sayrhazi.yaml`.
- Ajout des règles communes et du script d'installation.
- Clarification : Docker est optionnel et appartient au projet qui l'utilise, pas au workflow lui-même.
