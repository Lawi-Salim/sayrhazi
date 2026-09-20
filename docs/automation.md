# Automatisation de Sayrhazi

## Principe

Le cœur de Sayrhazi fonctionne manuellement. L'automatisation est une extension facultative destinée à réduire les transitions répétitives, pas à remplacer les décisions de l'utilisateur.

Une première automatisation raisonnable consiste à surveiller `build.txt` et à lancer Hadji lorsque Bamse a produit un rapport complet. Le script doit vérifier un statut explicite et un identifiant de tâche ; une simple modification de fichier ne suffit pas.

## Watcher actuel (`scripts/watch-work.py`)

Le watcher surveille `.opencode/resume/build.txt` et lance Hadji uniquement si le rapport est complet : fichier stable (anti écriture en cours), `task_id` présent et `status: TERMINÉ`. Il refuse les statuts incomplets (`EN COURS`, `BLOQUÉ`, absent), empêche les doubles déclenchements (`task_id` + hash déjà traité), applique un timeout et vérifie que `review.txt` mentionne le même `task_id`.

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

Chaque rapport devrait contenir `task_id`, `status`, `agent`, `version` et éventuellement `next_agent`. L'orchestrateur doit attendre que le fichier soit stable, refuser les statuts incomplets, empêcher les doubles déclenchements, appliquer un timeout et signaler les erreurs au lieu de les masquer.

Un agent superviseur doté de raisonnement n'est pas nécessaire pour ces transitions déterministes. Il ne devrait être envisagé qu'après stabilisation d'un orchestrateur scripté et seulement pour les cas ambigus.
