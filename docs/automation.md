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

## État persistant et reprise (Lot 3)

Les terminaux ne sont pas la mémoire du workflow : `.opencode/state/workflow-state.yaml` est la vue de coordination (`task_id`, statut, étapes `current/completed/pending/blocked`, agents en cours). Les rapports restent les preuves détaillées. Le dossier `.opencode/state/` est local : à ignorer par git (reprise mono-poste, pas de bruit).

Au redémarrage (ou à tout moment), réconcilier avant de reprendre :

```powershell
python engine/state.py --reconcile --project .
```

La réconciliation lit l'état, relit `workflow.yaml`, vérifie les rapports du `task_id` actif, ne retient que les étapes éligibles, ne relance jamais une étape terminée (sauf retour `CORRECTIONS NÉCESSAIRES` vers l'implémentation) et signale toute incohérence au lieu de la deviner. `tunda sayrhazi` contrôle la présence et la validité de l'état sans bloquer. Depuis le Lot 4, le watcher lit la config et met à jour l'état minimal + le journal (la réconciliation complète reste `engine/state.py --reconcile`).

## Moteur (`runtimes/opencode/scripts/watch-work.py`, installé dans `.opencode/`)

Le watcher est devenu un moteur piloté par `.opencode/workflow.yaml` : pour chaque étape `auto: true`, il vérifie rapport stable, `task_id` + statut autorisés, condition satisfaite et sortie non existante, puis appelle l'agent du rôle (prompt, minuteur, durée, vérification du rapport produit). Verrou d'instance unique, anti-double en mémoire + sortie existante (point 7), journal `history/workflow-log.md`, mise à jour minimale de `state/workflow-state.yaml`. Sans `workflow.yaml` valide, repli sur la transition historique `build.txt TERMINÉ → Hadji`, sans jamais planter.

Les conditions se résolvent depuis `sayrhazi.yaml` (`visual_qa_required` → Zawadi, `security_audit_required_by_default` → Hifadhui ; `design_required` sans indicateur : Ali reste manuel). Sont automatiques : `review` (toujours), `security` et `visual_qa` (si requis), `rework` (retour vers Bamse sur `CORRECTIONS NÉCESSAIRES`, sauf `build.txt` plus récent). Étapes inconnues ou cassées : signalées et ignorées, jamais devinées. `tunda sayrhazi` affiche les agents requis, manuels et inactifs de la configuration.

Les étapes éligibles ensemble partent en parallèle (Lot 6, threads stdlib), bornées par `workflow.max_parallel_agents` (défaut 3, garde-fou machine). La convergence est journalisée (`Convergence : review OK, security OK (2/2)`) : un échec (timeout, erreur) n'empêche jamais les autres branches, qui écrivent chacune leur rapport ; la branche échouée sera réévaluée au prochain changement. `running_agents` reflète l'ensemble en cours. Séquentiel si une seule étape éligible, repli historique sinon.

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
