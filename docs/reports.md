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

## Contrat minimal d'un rapport

Chaque rapport doit indiquer la date et l'heure système, le projet, la tâche examinée, la version ou l'état concerné, les vérifications réalisées, les problèmes, les limites, les actions suivantes et le verdict autorisé par le rôle.

Les problèmes sont classés `CRITIQUE`, `HAUTE`, `MOYENNE` ou `FAIBLE`. Un rapport ne doit contenir aucun secret, token ou mot de passe.

## Statuts

Bamse utilise `EN COURS`, `TERMINÉ` ou `BLOQUÉ`. Ali utilise `PROPOSÉ` ou `VALIDÉ`. Hadji et Hifadhui utilisent `VALIDÉ`, `VALIDÉ AVEC RÉSERVES` ou `CORRECTIONS NÉCESSAIRES`. Zawadi peut également utiliser `À COMPLÉTER` lorsque l'observation réelle manque.

## Identité de tâche

Pour une utilisation automatisée, chaque rapport contient un identifiant stable et un statut sur leurs propres lignes :

```text
task_id: FEATURE-001
status: TERMINÉ
```

L'identifiant permet de vérifier que les rapports concernent la même tâche et évite de déclencher une étape sur un ancien fichier. Le watcher exige `task_id` présent et `status: TERMINÉ` (Bamse) avant de lancer Hadji.
