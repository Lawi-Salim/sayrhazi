# Changelog Sayrhazi

## 0.4.1 — 2026-09-26

- Fix `task_id` : les instructions des six agents exigent désormais le bloc contrat machine en tête de rapport (`task_id:`, `agent:`, `status:` du rôle, `completed_at:`, `summary:`, sans gras ni puces) — sans lui le watcher refusait (cas Bamse/Sarhi). Contrats `contract.yaml` alignés, coquille `A IMPLÉMENTER` corrigée, `VALIDÉ` ajouté aux verdicts plan. Nouveau test `TestAgentContracts`. `renderer.py` force le LF (corrige la régénération CRLF sous Windows). `watch-work.py` : minuteur visible (tick toutes les 30 s pendant l'appel, durée `5s`/`1m`/`2m14s` à la fin) + ligne `En attente d'une autre tâche...` après chaque transition réussie (fini l'impression de freeze).

## 0.4.0 — 2026-09-26

- Lot 1 contrats : statuts figés (`TERMINÉ` = achèvement, `VALIDÉ` = verdict, `VALIDÉ` ajouté pour `plan.txt`), `completed_at` ISO remplace `version` comme horodatage (refusé avec message), `task_id` stable (`FEATURE-001` ou `MPANGO-2026-014`), `agents_required` + indicateurs `security/visual_qa/design_required` avec règle de cohérence.
- Nouveau `engine/report.py` (stdlib) : `parse_report`, `validate_report`, `validate_task`, `check_transition` (points 3/4/5/7). `tunda` et `checker.py` signalent les rapports non conformes en `[WARN]`/notes, jamais bloquant (anciens rapports sans `task_id` ignorés).
- Docs : `docs/reports.md` étendu (contrat, statuts, tâche, validation 8 points), `docs/automation.md` et `core/rules/reporting.md` alignés, template projet `AGENTS.md` §3 à jour. 7 nouveaux tests (`TestReport`).

## 0.3.0 — 2026-09-25

- Présentation : uniquement à l'ouverture ou sur demande, jamais à chaque réponse ; contexte utilisé sans être réaffiché, interdiction de commencer par « En tant que ... pour le projet ... ».
- Typographie française exigée dans chaque fichier agent (accents, apostrophes, cédilles).

- `remove sayrhazi` interactif : simulation + confirmation `yes`, `--yes` direct pour scripts.

- Banner ASCII affiché par `sayrhazi` et `info sayrhazi` (`engine/banner.py`, version lue depuis `VERSION`, autres sorties gardées analysables).

- Nouvelle arborescence : `core/` (agents en trios + workflow + schemas + rules + templates), `runtimes/opencode/` (adaptateur : agents .md, templates, scripts), `engine/` (installer, checker, updater, renderer, resolver, state), `cli/` (install, check, update, remove, info), `tests/`, `pyproject.toml`, `VERSION`. `engine/renderer.py` régénère les adaptateurs depuis les trios (vérifié byte-identique, `--check`). 13 tests stdlib (`tests/test_core.py`, `test_cli.py`, `test_integration.py`). Recâblage complet des chemins ; install/update/check validés en non-régression.

## 0.2.4 — 2026-09-22

- Fix validation : `technical:` ajouté aux clés explicites de `validate` et `tunda` (une config sans section `technical` passait silencieusement).
- Doc : « 5 agents » → 6, et distinction explicite workflow prescrit vs transitions automatiques (`automation.md`, `README`).

- MCP Playwright pré-câblé dans `template/opencode.json` (local via `npx`, `enabled`, `deny` global conservé — seuls Ali et Zawadi en `allow`). Nouveaux projets QA-ready sans chemin machine en dur (`--executable-path` reste une surcharge locale, ex. Mpango).

- Nouvel agent **Ali** (UI/UX, `agents/ali.md`, bleu `#3B82F6`, vision + Playwright observation) : maquettes, écrans, composants, responsive, thèmes → `design.txt` (`PROPOSÉ`/`VALIDÉ` + `design-log.md`). Il pose les briques visuelles neuves, Bamse solidifie sans re-maquetter. Flux si visuel : `Lawibrahim → Ali → Bamse`, précédé de `Bamse (squelette)` sur projet vierge. Nom configurable via `agents.designer` (schéma, modèle, validateurs, migration auto).

## 0.2.3 — 2026-09-21

- Schéma fonctionnel sans dépendance : nouveau `scripts/sayrhazi_config.py` (mini-parseur YAML + vérificateur JSON-Schema, stdlib uniquement), branché sur `validate` et `tunda` (`[OK] schema conforme` ou violations `schema : $.chemin : ...`). `schemas/sayrhazi.schema.json` aligné sur le template (8 sections typées).

## 0.2.2 — 2026-09-20

- Scaffolding initial : Lawibrahim propose une structure type dans un projet vide (défaut `frontend/` + `backend/` pour une `application` TypeScript, variantes selon `project.type`, préférences demandées) ; Bamse ne scaffold qu'après validation dans `plan.txt`.
- Identité visuelle : couleur hexadécimale en frontmatter (`Lawibrahim #8B5CF6`, `Bamse #22C55E`, `Hadji #F59E0B`, `Hifadhui #EF4444`, `Zawadi #14B8A6`, format exigé par OpenCode), reprise dans `docs/agents.md` et le `README`.
- Config BDD clarifiée : `technical.database` scindé en `database_type` (moteur), `database_driver` (librairie d'accès) et `database_name` (nom ou `null`). Ton exemple : `postgresql` + `sequelize` + `matinma`.
- Règle français/emojis désormais explicite dans chaque fichier agent : français toujours, emojis proscrits dans le travail mais tolérés en blague (Bamse en affichait un en présentation malgré la règle commune).
- Nouveau `scripts/update-sayrhazi.py` : la mise à jour devient un script versionné et multi-plateforme (agents + watcher, config préservée, orphelins signalés, exit 2 si non installé). La fonction `update sayrhazi` délègue dessus.
- Migration douce : `update` ajoute les clés manquantes du template (`agents:`, `database:` → `database_type/driver/name` avec reprise de l'ancien nom), backup horodaté dans `history/`, valeurs existantes jamais écrasées.

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
