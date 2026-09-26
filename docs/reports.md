# Rapports Sayrhazi

Les rapports courants se trouvent dans `.opencode/resume/`. Ils décrivent uniquement le dernier état utile à l'étape suivante. Avant remplacement, l'ancien contenu est ajouté au journal correspondant dans `.opencode/history/`.

| Fichier | Auteur | Fonction |
|---|---|---|
| `plan.txt` | Lawibrahim | décisions en cours et contexte validé |
| `design.txt` | Ali | maquette et specs visuelles |
| `build.txt` | Bamse | état de l'implémentation et vérifications |
| `review.txt` | Hadji | verdict qualité et corrections |
| `security.txt` | Hifadhui | verdict sécurité et réserves |
| `qa.txt` | Zawadi | observations réelles et verdict QA |

Les journaux recommandés sont `build-log.md`, `design-log.md`, `review-log.md`, `security-log.md` et `qa-log.md`. `plan.txt` reste cumulatif jusqu'à l'archivage explicite d'une feature dans `.opencode/features/`.

## Contrat minimal d'un rapport (Lot 1)

Cinq champs sont requis, sur leurs propres lignes (référence normative : `core/schemas/report.schema.yaml`, validateur : `engine/report.py`) :

```text
task_id: FEATURE-001
agent: builder
status: TERMINÉ
completed_at: "2026-09-26T10:00:00+04:00"
summary: Fonctionnalité implémentée et vérifiée localement.
next_agents: [reviewer]
```

* `task_id` : identifiant stable de la tâche, recopié à l'identique dans chaque rapport (`FEATURE-001` ou `MPANGO-2026-014`, les deux formats acceptés). Il permet de vérifier que les rapports concernent la même tâche et évite de déclencher une étape sur un ancien fichier.
* `agent` : rôle stable de l'auteur (`architect`, `designer`, `builder`, `reviewer`, `security`, `qa`), jamais le nom d'affichage configurable.
* `status` : verdict autorisé par le rôle (voir ci-dessous).
* `completed_at` : horodatage ISO 8601 de fin de travail. L'ancien champ `version` comme horodatage est refusé (confusion avec `workflow.version`).
* `summary` : résumé d'une phrase. `next_agents` (optionnel) annonce les destinataires suggérés, sans déclencher quoi que ce soit à lui seul.

Au-delà du contrat, chaque rapport doit indiquer la date et l'heure système, le projet, la tâche examinée, les vérifications réalisées, les problèmes, les limites, les actions suivantes et le verdict autorisé par le rôle.

Les problèmes sont classés `CRITIQUE`, `HAUTE`, `MOYENNE` ou `FAIBLE`. Un rapport ne doit contenir aucun secret, token ou mot de passe.

## Statuts figés

`TERMINÉ` décrit l'achèvement d'un travail, `VALIDÉ` décrit un verdict : ne pas les mélanger.

* Lawibrahim (`plan.txt`, auteur `architect`) : `À IMPLÉMENTER`, `INFORMATIF`, `VALIDÉ` (décision prise, déclenche l'implémentation).
* Bamse (`build.txt`) : `EN COURS`, `TERMINÉ` ou `BLOQUÉ`.
* Ali (`design.txt`) : `PROPOSÉ` ou `VALIDÉ`.
* Hadji (`review.txt`) et Hifadhui (`security.txt`) : `VALIDÉ`, `VALIDÉ AVEC RÉSERVES` ou `CORRECTIONS NÉCESSAIRES`.
* Zawadi (`qa.txt`) : mêmes verdicts, plus `À COMPLÉTER` lorsque l'observation réelle manque.

## Contrat minimal d'une tâche

Référence : `core/schemas/task.schema.yaml`, modèle : `core/templates/task.md`. Requis : `task_id`, `title`, `status` (`À IMPLÉMENTER`, `INFORMATIF`, `EN COURS`, `TERMINÉ`, `BLOQUÉ`, `VALIDÉ`). Recommandés : `agents_required` (rôles stables, source de vérité), `acceptance_criteria` (résultats observables : distinguent « étape terminée » de « fichier modifié »), et les raccourcis `security_required`, `visual_qa_required`, `design_required`, cohérents avec `agents_required` (ex. `security_required: true` impose `security` dans `agents_required`).

## Validation avant transition (8 points)

Avant de déclencher une étape, le moteur vérifie :

1. que le fichier attendu existe ;
2. qu'il est stable après écriture ;
3. que son `task_id` correspond à la tâche active ;
4. que son statut est autorisé pour cette transition ;
5. que l'auteur déclaré (`agent`) correspond au rôle attendu ;
6. qu'aucune exécution identique n'est déjà en cours ;
7. qu'un rapport de sortie équivalent n'est pas déjà présent ;
8. que le délai maximal n'est pas dépassé, si un délai est défini.

Le hash d'un fichier aide à détecter une modification mais ne prouve ni la tâche, ni la validité, ni l'autorisation : il n'est qu'un élément du contrat.

## Identité de tâche

Le watcher exige `task_id` présent et `status: TERMINÉ` (Bamse) avant de lancer Hadji, puis vérifie que `review.txt` mentionne le même `task_id`.
