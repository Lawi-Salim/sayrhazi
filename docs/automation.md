# Automatisation de Sayrhazi

## Principe

Le cœur de Sayrhazi fonctionne manuellement. L'automatisation est une extension facultative destinée à réduire les transitions répétitives, pas à remplacer les décisions de l'utilisateur.

> Sayrhazi ne doit pas décider à la place de l'utilisateur ; il doit empêcher que le workflow oublie une étape prévue.

Le moteur applique une règle explicite, il ne choisit pas un agent librement :

```text
un rapport identifié
+ un statut autorisé
+ une condition satisfaite
+ une transition déclarée
= un agent éligible
```

Le mode initial reste supervisé (`auto_start: false`) : les transitions techniques prévues peuvent être automatiques, la création ou le lancement d'une tâche importante reste soumis à validation humaine, le déploiement, la suppression et les migrations de données restent toujours soumis à validation humaine, et tout blocage ou ambiguïté est signalé plutôt que deviné.

Les terminaux sont des interfaces d'observation et d'intervention, jamais la mémoire du workflow : l'état indispensable à la reprise vit dans des fichiers projet, lisible après fermeture de l'IDE, arrêt de la machine ou absence prolongée.

Les agents conditionnels ne sont jamais invoqués systématiquement : jamais de parcours automatique `Bamse → Hadji → Hifadhui → Zawadi → Ali`. Chaque tâche déclare ses rôles nécessaires (ex. interface : Bamse/Hadji/Zawadi ; authentification : Bamse/Hadji/Hifadhui sans Zawadi).

## Transitions automatisables cibles vs état actuel

Cible (seulement si déclarées et vérifiées, Lots 1-4) :

```text
plan validé → Bamse
build terminé → Hadji
build terminé + security_required → Hifadhui
build terminé + visual_qa_required → Zawadi
plan validé + design_required → Ali
review avec corrections → retour vers Bamse
```

Restent toujours humains : décision finale Lawibrahim/utilisateur, lancement d'une tâche importante en mode supervisé, changement de périmètre ou de critères d'acceptation, déploiement, migration ou suppression de données, correction à solutions multiples, blocage ou incohérence non déterministe.

Une première automatisation raisonnable consiste à surveiller `build.txt` et à lancer Hadji lorsque Bamse a produit un rapport complet. Le script doit vérifier un statut explicite et un identifiant de tâche ; une simple modification de fichier ne suffit pas.

## Workflow prescrit vs transitions automatiques

Ne pas confondre les deux niveaux :

```text
WORKFLOW PRESCRIT (conceptuel, à orchestration humaine) :
Lawibrahim → Ali → Bamse → Hadji → Hifadhui → Zawadi → Terminé

TRANSITIONS AUTOMATIQUES ACTUELLES (réel, watch-work.py) :
build.txt TERMINÉ + task_id → Hadji → vérifier review.txt
```

Seule la transition `build.txt → Hadji` est automatisée. Hifadhui, Zawadi et le retour vers Bamse restent déclenchés manuellement : le moteur n'empêche pas toutes les transitions invalides, ce sont les contrats documentaires (rapports, statuts, `task_id`) qui les cadrent.

## Watcher actuel (`runtimes/opencode/scripts/watch-work.py`, installé dans `.opencode/`)

Le watcher surveille `.opencode/resume/build.txt` et lance Hadji uniquement si le rapport est complet : fichier stable (anti écriture en cours), `task_id` présent et `status: TERMINÉ`. Il refuse les statuts incomplets (`EN COURS`, `BLOQUÉ`, absent), empêche les doubles déclenchements (`task_id` + hash déjà traité en mémoire, plus `review.txt` existant pour le même `task_id` après redémarrage), applique un timeout et vérifie que `review.txt` mentionne le même `task_id`. Un nouveau `build.txt` de Bamse (plus récent que la revue, ex. après `CORRECTIONS NÉCESSAIRES`) relance légitimement la transition.

Modes utiles : `--check` (valide la config sans surveiller), `--once` (une seule vérification, exit `0` si déclenché), `--timeout SEC`.

## Limites connues

L'approche par hash + délai seule ne prouve pas que le rapport est terminé ni que `review.txt` a été produit : c'est pourquoi les contrôles ci-dessus sont obligatoires et le watcher ne doit pas être bricolé en version hash-seul.

Les problèmes déjà rencontrés concernent les permissions en mode headless, les fichiers créés hors du projet et l'interruption d'une session après de nombreuses étapes d'outils. L'orchestrateur doit travailler depuis la racine du projet, utiliser les chemins du projet, vérifier les droits d'écriture et enregistrer les erreurs.

## Périmètre recommandé

Commencer par une seule transition :

```text
build.txt : TERMINÉ → lancer Hadji → vérifier review.txt
```

Ne pas lancer automatiquement Bamse, ne pas boucler automatiquement après une review négative et ne pas publier, supprimer ou modifier des éléments sensibles. Les corrections, conflits de rapports et clôtures importantes restent sous contrôle humain.

## Conditions pour une automatisation fiable

Chaque rapport doit contenir `task_id`, `status`, `agent`, `completed_at` (ISO 8601, jamais `version`) et `summary`, plus éventuellement `next_agents` (voir `docs/reports.md` et `core/schemas/report.schema.yaml`). L'orchestrateur doit attendre que le fichier soit stable, refuser les statuts incomplets, vérifier que l'auteur déclaré correspond au rôle attendu, empêcher les doubles déclenchements, appliquer un timeout et signaler les erreurs au lieu de les masquer.

Un agent superviseur doté de raisonnement n'est pas nécessaire pour ces transitions déterministes. Il ne devrait être envisagé qu'après stabilisation d'un orchestrateur scripté et seulement pour les cas ambigus.
