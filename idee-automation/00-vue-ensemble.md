# Automation Sayrhazi — vue d'ensemble (brouillon local, non suivi)

Source : `Idee-Automation-Sayrhazi.md` (brouillon, non suivi).

## Compréhension en une phrase

Le besoin n'est pas de nouveaux agents mais un **moteur de transitions** `RAPPORT → CONDITION → TRANSITION → AGENT` qui supprime les oublis et les terminaux multiples, **sans jamais décider à la place de l'humain**. Le watcher actuel (`watch-work.py`) en est le prototype à généraliser, pas à jeter.

## Principe directeur

> Sayrhazi ne doit pas décider à la place de l'utilisateur ; il doit empêcher que le workflow oublie une étape prévue.

## Découpage en lots (dépendances dans l'ordre)

| Lot | Fiche | Contenu | Nature |
|---|---|---|---|
| 0 | `lot-0-principes.md` | Transitions pas décisions, agents conditionnels, terminaux ≠ mémoire, supervisé, reste humain | Décision doc, zéro code |
| 1 | `lot-1-contrats.md` | `task_id`, `agents_required`, critères d'acceptation, contrat rapport, validation 8 points | Fondation prioritaire |
| 2 | `lot-2-config-declarative.md` | `.opencode/workflow.yaml`, séquentiel + conditionnel | Nouveau fichier contrat |
| 3 | `lot-3-etat-reprise.md` | `state/workflow-state.yaml`, réconciliation, états normalisés | Cœur reprise |
| 4 | `lot-4-watcher-generalise.md` | Multi-transitions séquentielles, verrou, journal | Code |
| 5 | `lot-5-conditions.md` | Hifadhui/Zawadi/Ali selon indicateurs | Code |
| 6 | `lot-6-parallelisme.md` | Branches + convergence + `max_parallel_agents` | Code, après stabilisation |
| 7 | `lot-7-services.md` | Gestionnaire frontend/backend séparé | Code séparé |
| 8 | `lot-8-dashboard.md` | Interface, seulement si le texte ne suffit plus | Dernier |

## Écarts à trancher avant code

1. **`plan.txt` sans statut `VALIDÉ`.** Le workflow déclaratif déclenche Bamse sur `plan.txt`/`VALIDÉ`, mais le contrat actuel ne connaît que `À IMPLÉMENTER`/`INFORMATIF` → ajouter `VALIDÉ` au contrat ou déclencher sur `À IMPLÉMENTER` (Lot 1).
2. **Champ `version` comme horodatage** (`version: "2026-09-23..."`) → confusion avec `workflow.version` → préférer `completed_at` (Lot 1).
3. **`TERMINÉ` (achèvement) vs `VALIDÉ` (verdict)** → à figer (Lot 1).
4. **Nouveaux chemins** (`.opencode/workflow.yaml`, `.opencode/state/`) → install, update, tunda, validate, `.gitignore` devront les connaître (Lot 2).
5. **Format `task_id`** : `MPANGO-2026-014` vs convention `FEATURE-001` → garder ou namespacer par projet (Lot 1).
6. **V1 avec ou sans Hifadhui conditionnel** (§11 vs §13 du source) → aligner.

## Critères de réussite (source §14)

Un terminal par transition en moins ; `task_id` unique traçable ; aucun déclenchement sur ancien rapport ; aucune double invocation sans justification ; conditionnels lancés seulement si requis ; reprise sans perte ; corrections routées ; erreurs visibles ; validations humaines aux points sensibles ; services séparés du moteur.
