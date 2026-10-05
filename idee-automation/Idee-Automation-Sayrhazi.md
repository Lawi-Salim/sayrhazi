# Idées d’automatisation de Sayrhazi

> Document de consolidation et de priorisation des idées d’évolution de l’orchestration multi-agents Sayrhazi.

## 1. Conclusion générale

Le besoin principal de Sayrhazi n’est pas d’ajouter de nouveaux agents, mais de **coordonner automatiquement les agents déjà présents**. L’utilisateur ne devrait plus avoir à mémoriser qu’un agent attend le rapport d’un autre, ni à parcourir plusieurs terminaux pour relancer manuellement la chaîne.

La cible est un moteur de transitions capable de transformer un rapport valide en étape suivante :

```text
RAPPORT → CONDITION → TRANSITION → AGENT CIBLE
```

Le système doit automatiser les transitions mécaniques, tout en conservant une validation humaine pour les décisions importantes. Le watcher actuel, `watch-work.py`, constitue le premier prototype de cette architecture. Il ne doit pas être supprimé, mais généralisé progressivement.

## 2. Redondances regroupées

Le document initial répétait plusieurs fois les mêmes idées. Elles sont regroupées ici afin d’éviter de traiter plusieurs fois un même besoin.

| Idées répétées | Formulation consolidée |
|---|---|
| Appeler Hadji après `build.txt` | Déclencher un agent lorsqu’un rapport attendu satisfait une condition de transition. |
| Invoquer chaque agent « si nécessaire » | Déclarer les agents requis et leurs conditions dans la configuration de la tâche. |
| Reprendre le travail après une nuit ou une interruption | Conserver un état persistant du workflow, séparé des terminaux. |
| Faire travailler Hadji, Hifadhui ou Zawadi ensemble | Supporter les branches parallèles et leurs dépendances de convergence. |
| Vérifier le hash, la stabilité et le statut | Introduire un contrat de rapport vérifiable, dont le hash n’est qu’un élément. |
| Réduire le nombre de terminaux | Séparer l’orchestration des agents de la gestion des services frontend et backend. |
| Ajouter un dashboard | Garder l’interface comme étape ultérieure, après stabilisation du moteur local. |

## 3. Niveau 0 — Principes à fixer avant le code

Ce niveau définit les règles d’architecture. Il ne nécessite encore ni dashboard ni moteur complexe.

### 3.1 Automatiser les transitions, pas les décisions métier

Sayrhazi ne doit pas devenir un agent opaque qui décide librement quel rôle appeler. Le moteur doit appliquer des règles explicites :

```text
un rapport identifié
+ un statut autorisé
+ une condition satisfaite
+ une transition déclarée
= un agent éligible
```

Cette distinction est essentielle. Le moteur orchestre les étapes prévues ; il ne remplace pas Lawibrahim ni l’utilisateur dans les décisions d’architecture, de périmètre ou de déploiement.

### 3.2 Les agents conditionnels ne doivent pas être invoqués systématiquement

Le parcours ne doit pas devenir automatiquement :

```text
Bamse → Hadji → Hifadhui → Zawadi → Ali
```

Pour chaque tâche, Sayrhazi doit savoir quels rôles sont nécessaires. Une fonctionnalité d’interface peut nécessiter Bamse, Hadji et Zawadi. Une modification d’authentification peut nécessiter Bamse, Hadji et Hifadhui, sans faire intervenir Zawadi.

### 3.3 Les terminaux ne doivent pas être la mémoire du workflow

Les terminaux sont des interfaces d’observation et d’intervention. Ils ne doivent pas contenir l’état indispensable à la reprise. Le workflow doit rester compréhensible après la fermeture de Devin Desktop, l’arrêt de la machine ou une absence prolongée.

### 3.4 Le mode initial doit rester supervisé

Le premier moteur doit utiliser un mode supervisé :

- les transitions techniques prévues peuvent être automatiques ;
- la création ou le lancement d’une tâche importante reste soumis à validation humaine ;
- le déploiement, la suppression et les migrations de données restent toujours soumis à validation humaine ;
- un blocage ou une ambiguïté doit être signalé plutôt que deviné.

Le champ `auto_start: false` peut exprimer cette politique dans la configuration.

## 4. Niveau 1 — Contrats et données minimales

Ce niveau est la fondation prioritaire. Sans contrats stables, un moteur d’orchestration ne pourra pas distinguer un nouveau rapport d’un ancien fichier ou interpréter correctement un verdict.

### 4.1 Identifiant obligatoire de tâche

Chaque tâche doit avoir un identifiant stable, par exemple :

```yaml
task_id: MPANGO-2026-014
status: VALIDÉ
title: Ajouter le filtre par date dans la liste des engagements
```

L’identifiant doit être recopié dans chaque rapport produit pour cette tâche.

### 4.2 Déclaration des besoins de la tâche

Les exigences spécifiques doivent être déclarées au début du workflow :

```yaml
agents_required:
  - bamse
  - hadji
  - zawadi

security_required: false
visual_qa_required: true
design_required: false
```

Les listes explicites doivent rester la source de vérité. Les indicateurs comme `security_required` ou `visual_qa_required` peuvent servir de raccourcis lisibles, mais ils ne doivent pas entrer en contradiction avec `agents_required`.

### 4.3 Critères d’acceptation

La tâche doit préciser les résultats attendus :

```yaml
acceptance_criteria:
  - Le filtre accepte une date de début et une date de fin.
  - Les résultats sont correctement filtrés.
  - Un état vide est affiché si aucun résultat n’existe.
  - Le parcours fonctionne sur mobile.
```

Ces critères permettent aux agents et au moteur de distinguer une étape réellement terminée d’un simple fichier modifié.

### 4.4 Contrat minimal d’un rapport

Chaque rapport devrait contenir au minimum :

```yaml
task_id: MPANGO-2026-014
agent: bamse
status: TERMINÉ
version: "2026-09-23T19:30:00+04:00"
summary: "Fonctionnalité implémentée et vérifiée localement."
next_agents:
  - hadji
  - zawadi
```

Le nom `version` peut être remplacé par un champ plus explicite comme `completed_at`. L’important est de disposer d’un marqueur temporel et d’un identifiant de tâche fiables.

### 4.5 Validation d’un rapport avant transition

Avant de déclencher une étape, le moteur doit vérifier :

1. que le fichier attendu existe ;
2. qu’il est stable après écriture ;
3. que son `task_id` correspond à la tâche active ;
4. que son statut est autorisé pour cette transition ;
5. que l’auteur déclaré correspond à l’agent attendu ;
6. qu’aucune exécution identique n’est déjà en cours ;
7. qu’un rapport de sortie équivalent n’est pas déjà présent ;
8. que le délai maximal n’est pas dépassé, si un délai est défini.

Le hash d’un fichier peut aider à détecter une modification, mais il ne remplace pas ce contrat. Un hash ne prouve ni que la tâche est la bonne, ni que le rapport est valide, ni que l’agent est autorisé à le produire.

## 5. Niveau 2 — Configuration déclarative du workflow

Une fois les contrats définis, Sayrhazi peut décrire le parcours dans `.opencode/workflow.yaml`. Cette configuration doit rester lisible par un humain et versionnable avec le projet.

Exemple de base :

```yaml
workflow:
  mode: supervised
  auto_start: false
  max_parallel_agents: 3

stages:
  - id: implementation
    agent: bamse
    trigger:
      report: plan.txt
      status: VALIDÉ

  - id: review
    agent: hadji
    trigger:
      report: build.txt
      status: TERMINÉ

  - id: security
    agent: hifadhui
    condition: security_required
    trigger:
      report: build.txt
      status: TERMINÉ

  - id: visual_qa
    agent: zawadi
    condition: visual_qa_required
    trigger:
      report: build.txt
      status: TERMINÉ

  - id: design
    agent: ali
    condition: design_required
    trigger:
      report: plan.txt
      status: VALIDÉ
```

Cette configuration exprime les rôles, les rapports déclencheurs et les conditions. Elle ne doit pas contenir des règles dispersées dans le code du watcher.

### 5.1 Transitions séquentielles

Le cas de base peut être représenté ainsi :

```text
plan validé
    ↓
Bamse implémente
    ↓
build terminé
    ↓
Hadji vérifie
    ↓
review validée
    ↓
Zawadi effectue la QA si nécessaire
    ↓
terminé
```

Si Hadji renvoie `CORRECTIONS NÉCESSAIRES`, la transition revient vers Bamse au lieu de continuer vers la QA.

### 5.2 Transitions conditionnelles

Hifadhui intervient uniquement lorsqu’un risque de sécurité est déclaré ou détecté selon une règle explicitement autorisée :

```text
build terminé
      ↓
security_required ?
   oui       non
    ↓         │
 Hifadhui     │
    └────┬────┘
         ↓
        QA
```

Le premier prototype doit privilégier les conditions déclarées dans la tâche. La détection automatique d’un risque par analyse du code pourra être ajoutée plus tard, mais elle ne doit pas être introduite avant d’avoir un mécanisme explicable et testable.

## 6. Niveau 3 — Moteur d’état et reprise

C’est le niveau qui résout directement l’oubli de Hadji après une nuit ou une interruption.

### 6.1 État persistant du workflow

Sayrhazi devrait écrire un fichier comme `.opencode/state/workflow-state.yaml` :

```yaml
workflow:
  task_id: MPANGO-2026-014
  status: IN_PROGRESS
  started_at: "2026-09-23T18:30:00+04:00"
  current_stages:
    - implementation
  completed_stages:
    - planning
  pending_stages:
    - review
    - visual_qa
  blocked_stages: []
  running_agents:
    - bamse
```

L’état doit permettre de distinguer les étapes terminées, en cours, prêtes, en attente, bloquées et échouées. Les rapports restent les preuves détaillées ; le fichier d’état constitue la vue de coordination.

### 6.2 Reprise après interruption

Au redémarrage, le moteur doit :

1. lire l’état persistant ;
2. relire la configuration ;
3. vérifier les rapports associés au `task_id` actif ;
4. réconcilier les rapports avec les étapes connues ;
5. reprendre uniquement les étapes éligibles ;
6. éviter de relancer une étape déjà terminée ;
7. signaler toute incohérence au lieu de l’ignorer.

Le workflow doit donc survivre à la fermeture des terminaux et non dépendre de leur ordre d’ouverture.

### 6.3 États minimaux à définir

Avant l’implémentation, les états doivent être normalisés. Une base raisonnable est :

```text
PENDING
READY
RUNNING
TERMINÉ
VALIDÉ
VALIDÉ_AVEC_RÉSERVES
CORRECTIONS_NÉCESSAIRES
BLOCKED
FAILED
CANCELLED
```

Il faudra décider si `TERMINÉ` décrit l’achèvement du travail et si `VALIDÉ` décrit le verdict d’un reviewer. Ces notions ne doivent pas être mélangées.

## 7. Niveau 4 — Parallélisation et convergence

Lorsque plusieurs contrôles sont indépendants, le moteur doit pouvoir les lancer en parallèle.

Exemple :

```text
Bamse terminé
      ├── Hadji
      ├── Hifadhui
      └── Zawadi
```

Le moteur ne doit déclencher l’étape suivante qu’après réception des résultats attendus :

```text
Hadji    ─┐
Hifadhui ─┼── convergence
Zawadi   ─┘
          ↓
     décision suivante
```

La configuration doit donc pouvoir exprimer :

- les étapes qui peuvent démarrer ensemble ;
- les étapes qui dépendent d’un groupe complet ;
- le nombre maximal d’agents parallèles ;
- le comportement en cas d’échec d’une branche ;
- le comportement si une branche n’est pas requise.

Le champ `max_parallel_agents` constitue une première protection contre la surcharge de la machine.

## 8. Niveau 5 — Évolution de `watch-work.py`

`watch-work.py` doit évoluer par étapes plutôt que devenir immédiatement un moteur complet.

### Étape 5.1 — Généraliser le déclenchement existant

Conserver le flux actuel :

```text
build.txt valide → Hadji
```

Puis extraire les opérations communes : stabilité du fichier, validation du rapport, verrouillage et journalisation.

### Étape 5.2 — Lire une configuration

Le watcher doit lire `.opencode/workflow.yaml` au lieu de contenir les agents et conditions en dur.

### Étape 5.3 — Ajouter l’état

Le watcher doit écrire `.opencode/state/workflow-state.yaml` et archiver les événements importants dans un journal dédié.

### Étape 5.4 — Ajouter les conditions

Le moteur doit prendre en charge les conditions déclarées : sécurité, QA visuelle, design et autres exigences futures.

### Étape 5.5 — Ajouter les branches parallèles

La parallélisation ne doit être introduite qu’après stabilisation des transitions séquentielles et du mécanisme de reprise.

### Étape 5.6 — Renommer éventuellement le composant

Une fois son rôle élargi, le fichier pourrait devenir `workflow-runner.py` ou `sayrhazi-runner.py`. Ce renommage n’est pas prioritaire. La compatibilité avec les projets déjà installés doit passer avant le changement de nom.

## 9. Niveau 6 — Séparer les agents des services de développement

Les agents et les serveurs frontend/backend ne doivent pas être gérés par la même logique.

### Agents

Les agents produisent des rapports et progressent dans un workflow :

```text
Lawibrahim, Ali, Bamse, Hadji, Hifadhui, Zawadi
```

### Services

Les services sont des processus persistants :

```text
frontend → yarn dev
backend  → yarn dev
```

Un futur gestionnaire de services pourrait démarrer ces processus en arrière-plan, vérifier leurs ports, capturer leurs logs et signaler un arrêt. Cette fonction est utile pour réduire le nombre de terminaux, mais elle ne doit pas être mélangée au moteur de transitions des agents.

La cible opérationnelle pourrait être :

```text
un terminal de contrôle
+ services frontend/backend en arrière-plan
+ agents invoqués par le moteur
```

Le redémarrage automatique des services doit rester prudent : un service peut s’arrêter volontairement ou nécessiter une intervention humaine.

## 10. Niveau 7 — Interface de contrôle

Un dashboard est une évolution pertinente, mais il ne constitue pas la première étape. Il ajouterait une vue centralisée des tâches, agents, rapports, transitions, erreurs et blocages.

Il faut d’abord stabiliser :

1. le contrat des rapports ;
2. la configuration déclarative ;
3. la machine d’état ;
4. la reprise ;
5. les journaux ;
6. les transitions parallèles.

Sans ces fondations, un dashboard ne ferait qu’afficher un état instable.

## 11. Ce qui doit rester humain

L’automatisation doit supprimer les oublis et les déplacements entre terminaux, pas supprimer le jugement du responsable du projet.

Une validation humaine doit rester obligatoire pour :

- la décision finale de Lawibrahim ou de l’utilisateur ;
- le lancement d’une tâche importante, lorsque le mode supervisé l’exige ;
- le changement de périmètre ou de critères d’acceptation ;
- le déploiement ;
- une migration ou suppression de données ;
- une correction proposée lorsque plusieurs solutions sont possibles ;
- un blocage ou une incohérence que le moteur ne peut pas résoudre de façon déterministe.

Les transitions suivantes peuvent être automatiques lorsqu’elles sont déclarées et vérifiées :

```text
plan validé → Bamse
build terminé → Hadji
build terminé + security_required → Hifadhui
build terminé + visual_qa_required → Zawadi
plan validé + design_required → Ali
review avec corrections → retour vers Bamse
```

## 12. Feuille de route recommandée

### Niveau 0 — Décision d’architecture

Fixer les principes : transitions explicites, mode supervisé, agents conditionnels et état indépendant des terminaux.

### Niveau 1 — Contrats

Normaliser `task_id`, les statuts, l’auteur, la date, les critères d’acceptation et les rapports d’agents.

### Niveau 2 — Configuration

Créer `.opencode/workflow.yaml` et déplacer les règles du code vers cette configuration.

### Niveau 3 — Moteur minimal

Faire évoluer `watch-work.py` pour gérer plusieurs transitions séquentielles, avec verrouillage, journal et prévention des doublons.

### Niveau 4 — Reprise

Ajouter `workflow-state.yaml`, la réconciliation au démarrage et la gestion des étapes bloquées ou échouées.

### Niveau 5 — Conditions

Ajouter Hifadhui, Zawadi et Ali selon les indicateurs de la tâche, sans les invoquer inutilement.

### Niveau 6 — Parallélisation

Ajouter les branches parallèles et la convergence après stabilisation de la reprise.

### Niveau 7 — Services

Créer séparément un gestionnaire des processus frontend/backend afin de réduire le nombre de terminaux.

### Niveau 8 — Dashboard

Construire une interface seulement si la vue texte, les journaux et l’état persistant ne suffisent plus.

## 13. Première version réaliste à viser

La première version utile ne doit pas encore lancer tous les agents en parallèle ni gérer les serveurs frontend/backend. Elle devrait seulement garantir le parcours suivant :

```text
plan.txt validé
      ↓
Bamse invoqué une seule fois
      ↓
build.txt terminé et valide
      ↓
Hadji invoqué automatiquement
      ↓
review validée
      ↓
Zawadi invoquée si visual_qa_required
```

Elle doit également :

- conserver le `task_id` ;
- écrire l’état du workflow ;
- reprendre après interruption ;
- archiver les événements ;
- signaler les erreurs ;
- ne pas lancer Hifadhui ou Ali sans condition explicite.

Cette version résoudrait déjà le problème concret observé : revenir le lendemain sans oublier qu’une review attendait le build de Bamse.

## 14. Critères de réussite

L’automatisation pourra être considérée comme fiable lorsque les conditions suivantes seront vérifiées :

- l’utilisateur n’a plus besoin d’ouvrir un terminal par transition ;
- une tâche possède un identifiant unique et traçable ;
- un ancien rapport ne déclenche pas une nouvelle tâche ;
- un agent n’est jamais invoqué deux fois pour la même étape sans justification ;
- les agents conditionnels ne sont lancés que lorsqu’ils sont requis ;
- le workflow reprend après arrêt sans perdre son état ;
- un verdict de correction retourne vers l’étape appropriée ;
- les erreurs et blocages sont visibles ;
- les validations humaines restent obligatoires aux points sensibles ;
- les services frontend/backend restent séparés du moteur d’agents.

## 15. Verdict consolidé

L’idée centrale est solide et constitue une évolution naturelle de Sayrhazi. Le projet ne doit pas chercher à multiplier les agents, mais à construire une orchestration explicite autour des six agents existants.

La progression recommandée est :

```text
contrats fiables
    ↓
configuration déclarative
    ↓
transitions séquentielles
    ↓
état persistant et reprise
    ↓
conditions d’agents
    ↓
parallélisation
    ↓
gestion séparée des services
    ↓
dashboard éventuel
```

Le principe directeur peut être résumé ainsi :

> **Sayrhazi ne doit pas décider à la place de l’utilisateur ; il doit empêcher que le workflow oublie une étape prévue.**

## Références

[1]: https://github.com/lawi-salim/sayrhazi "Dépôt GitHub du système Sayrhazi"
