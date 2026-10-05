# Perspectives d’architecture — Sayrhazi

> **Statut :** trajectoire d’évolution de l’architecture actuelle ; OpenCode reste l’unique runtime visé à court terme.
> **Priorité actuelle :** stabiliser et modulariser Sayrhazi pour OpenCode, en conservant l’accès aux modèles gratuits proposés par OpenCode.
> **Intention à long terme :** rendre possible l’ajout d’autres runtimes sans imposer leur développement aujourd’hui, ni abonnement ou modèle payant.

## 1. Vision générale

Sayrhazi est né pour permettre un workflow de développement multi-agents avec les modèles gratuits proposés par OpenCode. La priorité est donc de consolider l’architecture **autour d’OpenCode**, qui correspond à la situation et aux moyens actuels du projet.

La cible consiste à mieux séparer les concepts Sayrhazi de leur implémentation OpenCode. Cette séparation prépare une éventuelle portabilité ultérieure, mais **n’implique ni intégration de Claude/Gemini maintenant, ni abonnement payant, ni changement de modèles**. OpenCode est le seul runtime à implémenter et à tester dans la trajectoire immédiate.

La règle structurante est donc :

> **À terme, `core/` ne devrait pas dépendre des détails propres à OpenCode.** Pour l’instant, l’adaptateur OpenCode est le seul runtime concret et constitue la priorité de développement.

Dans l’architecture visée, un adaptateur relie le cœur à chaque runtime. **À court terme, seul l’adaptateur OpenCode existe et doit être rendu fiable.** Le CLI conserve les parcours déjà utilisés ; le moteur (`engine/`) est une séparation de responsabilités à introduire progressivement pour organiser l’installation, la vérification, le rendu, la mise à jour et l’état du projet.

À terme, les agents, les workflows, les schémas, les règles, les tâches et les rapports pourraient rester communs entre runtimes. La première étape est de distinguer ces concepts des formats et métadonnées OpenCode, sans dégrader le workflow actuel ni perdre l’accès aux modèles gratuits. La portabilité ne sera validée que si un autre runtime est réellement envisagé et testé.

### Point de départ dans le dépôt actuel

Le dépôt s’organise aujourd’hui autour de `agents/`, `template/`, `schemas/`, `scripts/` et `docs/`. L’installation place les agents et la configuration dans `.opencode/` ; les commandes d’installation, de diagnostic, de mise à jour et le watcher existent déjà. La refactorisation proposée doit donc **réorganiser et clarifier l’existant**, pas repartir de zéro ni remplacer les usages qui fonctionnent.

## 2. Principes d’architecture

1. **Séparation progressive :** isoler les concepts et comportements Sayrhazi des métadonnées et formats OpenCode, sans exiger dès maintenant un cœur totalement indépendant.

1. **Contrats explicites :** les agents, les données et les workflows ont des entrées, sorties, prérequis et critères de réussite définis.

1. **OpenCode d’abord :** l’adaptateur OpenCode est le seul adaptateur à construire et maintenir pour l’instant ; les autres restent une possibilité future.

1. **État explicite :** un projet conserve une configuration et un état Sayrhazi propres ; le runtime ne doit pas être deviné à partir de fichiers présents par hasard.

1. **Maturité déclarée :** aujourd’hui, les critères servent d’abord à vérifier la qualité du parcours OpenCode. Des statuts comparatifs entre runtimes ne seront utiles que si d’autres adaptateurs sont entrepris.

1. **Évolution incrémentale :** stabiliser le cœur, le moteur et OpenCode avant toute décision d’ajouter un autre runtime. Cette décision dépendra des besoins et des moyens disponibles à ce moment-là.

## 3. Architecture cible

```
sayrhazi/
├── core/
│   ├── agents/
│   │   ├── lawibrahim/
│   │   │   ├── agent.yaml
│   │   │   ├── instructions.md
│   │   │   └── contract.yaml
│   │   ├── ali/
│   │   ├── bamse/
│   │   ├── hadji/
│   │   ├── hifadhui/
│   │   └── zawadi/
│   ├── workflow/
│   │   ├── workflow.yaml
│   │   ├── stages/
│   │   │   ├── planning.yaml
│   │   │   ├── design.yaml
│   │   │   ├── implementation.yaml
│   │   │   ├── review.yaml
│   │   │   ├── security.yaml
│   │   │   └── qa.yaml
│   │   └── transitions.yaml
│   ├── schemas/
│   │   ├── task.schema.yaml
│   │   ├── report.schema.yaml
│   │   ├── feature.schema.yaml
│   │   ├── resume.schema.yaml
│   │   └── config.schema.yaml
│   ├── rules/
│   │   ├── global.md
│   │   ├── workflow.md
│   │   ├── agents.md
│   │   └── reporting.md
│   └── templates/
│       ├── task.md
│       ├── report.md
│       ├── feature.md
│       └── resume.md
├── runtimes/
│   └── opencode/                 # seul runtime visé et testé à court terme
│   │   ├── manifest.yaml
│   │   ├── agents/
│   │   ├── commands/
│   │   ├── instructions/
│   │   ├── scripts/
│   │   └── templates/
├── cli/
│   ├── commands/
│   │   ├── install.py
│   │   ├── check.py
│   │   ├── update.py
│   │   ├── remove.py
│   │   └── info.py
│   └── main.py
├── engine/
│   ├── installer.py
│   ├── updater.py
│   ├── checker.py
│   ├── renderer.py
│   ├── resolver.py
│   └── state.py
├── scripts/
├── tests/
│   ├── core/
│   ├── cli/
│   ├── runtimes/
│   │   └── opencode/
│   └── integration/
├── docs/
│   ├── architecture.md
│   ├── runtimes.md
│   ├── agents.md
│   ├── workflow.md
│   └── development.md
├── pyproject.toml
├── README.md
└── VERSION
```

Cette arborescence est une **cible de conception**, pas une liste de travaux à lancer immédiatement. Elle ne demande ni la création immédiate de tous les répertoires, ni l’ajout de Claude ou Gemini. Les dossiers actuels peuvent être déplacés ou renommés par étapes, avec OpenCode comme seul cas fonctionnel à préserver.

## 4. Responsabilités des couches

### 4.1 `core/` — l’identité de Sayrhazi

À terme, le cœur décrira les concepts Sayrhazi sans porter les détails de format propres à OpenCode. La transition doit être graduelle : extraire d’abord les rôles, contrats, règles, workflows et formats partagés, tout en gardant les fichiers d’exécution OpenCode fonctionnels.

#### Agents et contrats

Un fichier d’agent décrit son identité, son rôle, ses responsabilités, les données dont il a besoin et les résultats attendus. Il ne dit pas que l’agent appartient à OpenCode ou à un autre runtime.

Exemple de description :

```yaml
id: bamse
name: Bamse
role: developer

responsibilities:
  - implementation
  - testing

inputs:
  - task
  - plan
  - project_context

outputs:
  - implementation
  - test_results
  - report
```

Le fichier `contract.yaml` formalise les obligations de l’agent :

```yaml
id: bamse

input:
  required:
    - task
    - plan

output:
  required:
    - status
    - summary
    - changed_files

permissions:
  filesystem: write
  git: write

success:
  required:
    - tests_passed
```

Pour l’instant, l’adaptateur OpenCode traduit ce contrat vers les métadonnées, commandes et permissions comprises par OpenCode. Cette séparation permettra éventuellement d’ajouter un autre adaptateur ; elle n’oblige pas à le développer maintenant.

#### Workflows

Le workflow décrit la séquence de travail et les transitions, pas son implémentation dans un runtime. Les étapes envisagées sont : planification, conception, implémentation, revue, sécurité et assurance qualité.

Exemple d’étape :

```yaml
id: implementation

agent: bamse

requires:
  - plan

produces:
  - implementation
  - report

next:
  success: review
  failure: implementation
```

#### Schémas, règles et modèles

- **`schemas/`** définit les formats communs de tâches, fonctionnalités, rapports, reprises et configuration.

- **`rules/`** rassemble les règles globales indépendantes du runtime. Exemples : une tâche n’est pas terminée sans rapport de validation ; un agent ne modifie pas les responsabilités d’un autre ; toute correction est associée à un `task_id`.

- **`templates/`** définit une fois les formats des tâches, rapports, fonctionnalités et reprises. Un adaptateur peut modifier leur mode de présentation sans changer leur sens.

Les schémas partagés évitent que chaque runtime invente un format incompatible et que le cœur devienne difficile à maintenir.

### 4.2 `runtimes/` — les adaptateurs

Le répertoire `runtimes/opencode/` doit, à terme, regrouper ou générer les éléments nécessaires à l’exécution de Sayrhazi dans OpenCode : manifeste, agents, commandes, instructions, scripts et modèles adaptés. C’est le seul adaptateur visé à court terme. D’autres sous-répertoires n’apparaîtront que si l’ajout d’un autre runtime devient une décision concrète.

Exemple indicatif de manifeste :

```yaml
runtime:
  id: opencode
  name: OpenCode

version:
  minimum: "1.x"

capabilities:
  agents: true
  commands: true
  instructions: true
  scripts: true

paths:
  config: ".opencode"
```

Les détails propres à OpenCode — par exemple les métadonnées de modèle, les modes d’agent, les permissions et les fichiers de configuration attendus — doivent rester dans cette couche ou dans les fichiers générés pour OpenCode, plutôt que contaminer les contrats communs. La manière exacte de préserver les modèles gratuits OpenCode fait partie des exigences de cet adaptateur. La traduction vers d’autres outils est hors du périmètre immédiat.

### 4.3 `cli/` — l’interface utilisateur

Le CLI expose les commandes de Sayrhazi et orchestre les opérations. Les usages existants (`Sayrhazi .`, `tunda sayrhazi`, `update sayrhazi`) doivent continuer à fonctionner pendant la refactorisation. Puisqu’OpenCode est le seul runtime pris en charge pour l’instant, un menu de sélection de runtime n’est pas nécessaire à court terme.

Si plusieurs runtimes sont un jour pris en charge, un registre central pourra éviter de multiplier les conditions spécifiques (`if runtime == ...`). À court terme, ne pas introduire cette abstraction simplement pour anticiper une intégration non planifiée. Exemple futur éventuel :

```yaml
runtimes:
  opencode:
    adapter: opencode
    status: stable

  claude:
    adapter: claude
    status: experimental

  gemini:
    adapter: gemini
    status: planned
```

Les statuts doivent pouvoir évoluer indépendamment du cœur : OpenCode peut être stable, Claude expérimental et Gemini planifié.

### 4.4 `engine/` — les opérations concrètes

Le moteur est distinct du cœur : le cœur définit les concepts et les règles ; le moteur les installe, les vérifie, les met à jour et les transforme. Cette distinction est une cible de modularisation : elle peut d’abord être reflétée dans les responsabilités et les tests, sans imposer une réécriture complète des scripts existants.

- **`installer.py`** combine le cœur et l’adaptateur choisi pour produire les fichiers dans le projet utilisateur.

- **`checker.py`** vérifie les composants attendus, la configuration, la compatibilité des versions et la présence des fichiers.

- **`updater.py`** compare l’installation et la version courante de Sayrhazi, puis applique les changements appropriés sans toucher inutilement au code du projet.

- **`renderer.py`** transforme les objets du cœur (agent, workflow, règles, modèles) en fichiers compréhensibles par le runtime sélectionné.

- **`resolver.py`** détermine les versions compatibles du cœur, de l’adaptateur et du runtime, en tenant compte de la configuration du projet.

- **`state.py`** lit et écrit l’état Sayrhazi du projet ; cet état ne doit pas être confondu avec les fichiers propres au runtime.

Exemple de résolution : Sayrhazi `0.8` + OpenCode + configuration du projet conduit à la version compatible de l’adaptateur OpenCode, par exemple `0.8`, et vérifie que la version minimale du runtime est satisfaite.

## 5. État conservé dans chaque projet

Une évolution possible est de distinguer l’état propre à Sayrhazi des fichiers d’exécution OpenCode. Aujourd’hui, la configuration réside dans `.opencode/sayrhazi.yaml` ; la proposition ci-dessous de créer `.sayrhazi/` est donc **un changement de conception et de migration à évaluer**, pas une description de l’existant ni une exigence immédiate :

```
mon-projet/
├── .sayrhazi/
│   ├── config.yaml
│   ├── state.yaml
│   └── version
├── .opencode/
│   ├── agents/
│   ├── commands/
│   └── ...
└── src/
```

Exemple de `.sayrhazi/config.yaml` :

```yaml
version: 0.8.0

runtime:
  id: opencode

project:
  name: my-project
```

Si `.sayrhazi/` est adopté, il pourra enregistrer la configuration et l’état de Sayrhazi, tandis que `.opencode/` conservera les éléments attendus par OpenCode. La migration devra préserver les projets installés, les rapports, l’historique et la configuration existants. Tant qu’OpenCode est l’unique runtime, la valeur de cette migration doit être pesée face à la complexité et au coût de compatibilité.

## 6. Parcours utilisateur envisagés

### Installation

Le parcours utilisateur actuel doit rester centré sur OpenCode : l’installation existante initialise la structure OpenCode dans le projet. La refactorisation peut séparer ses opérations en composants sans demander à l’utilisateur de choisir un runtime. Une sélection ne se justifierait qu’après décision d’en prendre un second en charge.

Flux cible :

```
core + adaptateur OpenCode + projet
                 ↓
              resolver
                 ↓
              renderer
                 ↓
              installer
                 ↓
       .sayrhazi/config.yaml (si cette migration est retenue)
```

### Diagnostic

`tunda sayrhazi` existe déjà et vérifie l’installation OpenCode : structure, six agents, configuration et schéma, fichier JSON, watcher et cohérence de version. La trajectoire consiste à conserver cette commande et à clarifier/étendre progressivement ses contrôles, pas à inventer un nouveau diagnostic.

### Mise à jour

`update sayrhazi` existe déjà et met à jour les agents et le watcher, migre la configuration avec précaution et préserve les rapports, l’historique et les fichiers contrôlés par le projet. La modularisation doit conserver ces garanties et améliorer la visibilité des changements sans modifier inutilement le code applicatif.

## 7. Tests et critères de conformité

Les tests devraient couvrir le cœur, le CLI, l’adaptateur OpenCode et les scénarios d’intégration. La priorité est de tester les usages et mises à jour OpenCode ; des tests pour un autre runtime ne seront ajoutés que si celui-ci entre réellement dans le périmètre.

Une suite commune de conformité pourrait vérifier si un runtime sait :

- installer les agents ;

- exécuter un workflow ;

- persister l’état ;

- reprendre une tâche ;

- produire un rapport ;

- exécuter l’assurance qualité ;

- se mettre à jour ;

- récupérer après une erreur.

Dans l’immédiat, ces tests servent à fiabiliser Sayrhazi **sur OpenCode**, y compris l’installation, les modèles gratuits configurés et les workflows réellement utilisés. Les statuts comparatifs (stable/expérimental/planifié) ne deviennent pertinents que si un deuxième runtime est effectivement entrepris ; ils ne constituent pas un objectif de court terme.

## 8. Progression de mise en œuvre proposée

Cette progression transforme la vision en étapes raisonnables. Elle est proposée pour faciliter la planification ; elle ne prétend pas figer les priorités du produit.

### Étape 1 — Consolider l’architecture OpenCode existante

- Stabiliser les concepts du cœur qui sont déjà nécessaires.

- Séparer progressivement les définitions indépendantes du runtime des fichiers spécifiques à OpenCode.

- Formaliser les contrats d’agents et les formats partagés les plus utiles.

- Préserver et tester les parcours existants : installation, `tunda sayrhazi`, `update sayrhazi` et watcher.
- Vérifier que les modèles gratuits OpenCode restent utilisables et que la refactorisation ne nécessite aucun abonnement payant.

### Étape 2 — Introduire l’état et les responsabilités du moteur

- Étudier la valeur d’un état centralisé et de `.sayrhazi/`, sans déplacer la configuration actuelle avant d’avoir défini une migration sûre et justifiée.

- Séparer les commandes du CLI des opérations du moteur, sans ajouter de sélection multi-runtime tant qu’OpenCode est le seul runtime pris en charge.

- Clarifier et isoler les opérations d’installation, de vérification, de rendu et de résolution.

- Ajouter des tests d’intégration pour le parcours utilisateur principal.

### Étape 3 — Fiabiliser les mises à jour et la conformité OpenCode

- Définir et tester la compatibilité entre le cœur, l’adaptateur OpenCode et les versions d’OpenCode prises en charge.

- Tester les mises à jour et la récupération après erreur.

- Établir une suite de conformité pour l’intégration OpenCode et des critères de stabilité explicites.

### Étape 4 — Décider éventuellement d’un autre runtime, plus tard

- N’envisager un autre runtime qu’une fois Sayrhazi stable sur OpenCode et si les besoins, les moyens et les modèles disponibles le justifient.

- Si cette décision est prise, réutiliser les concepts communs et créer un adaptateur séparé ; Claude ou Gemini ne sont ni promis ni requis.

- Attribuer à chaque adaptateur un statut conforme à ses tests.

**Conséquence importante :** Sayrhazi peut adopter dès maintenant une meilleure séparation interne tout en restant un outil OpenCode. Aucun abonnement à Claude, Gemini ou à des modèles payants n’est nécessaire pour les étapes actuelles. Un autre runtime ne sera qu’une possibilité ultérieure, après stabilisation d’OpenCode et si cela devient souhaitable et accessible.

## 9. Résumé des distinctions à préserver

| Couche | Question à laquelle elle répond | Exemples de contenu |
| --- | --- | --- |
| `core/` | Qu’est-ce que Sayrhazi ? | Agents, workflows, schémas, règles, modèles |
| `engine/` | Comment Sayrhazi agit-il sur un projet ? | Installation, vérification, mise à jour, rendu, résolution, état |
| `runtimes/` | Où isoler les détails d’exécution propres à un runtime ? | Adaptateur OpenCode maintenant ; autres éventuels plus tard |
| `cli/` | Comment l’utilisateur demande-t-il une action à Sayrhazi ? | Commandes actuelles d’installation, diagnostic et mise à jour pour OpenCode |

```
                    SAYRHAZI
                       │
        ┌──────────────┼──────────────┐
        │              │              │
       CORE          ENGINE           CLI
        │       install/check/update   │
        └──────────────┼──────────────┘
                       │
                 ADAPTATEUR OPENCODE
                         │
                         ▼
                    OpenCode

       Autres runtimes : éventualité ultérieure, hors périmètre actuel
```

L’architecture visée doit d’abord préserver le fonctionnement actuel sur OpenCode, ses workflows et l’accès aux modèles gratuits. La portabilité future viendra de contrats communs éprouvés et d’un adaptateur isolé, pas du simple fait de créer plusieurs dossiers. Elle n’est pas un prérequis au succès actuel de Sayrhazi.

## 10. Points à préciser avant ou pendant l’implémentation

- Les limites exactes du cœur indépendant et de l’adaptateur OpenCode, notamment les métadonnées de modèle, les permissions et les modes d’agents.

- Le format définitif des manifestes, contrats et schémas, ainsi que leur validation.

- La politique de mise à jour et de préservation des fichiers modifiés par l’utilisateur.

- Les compatibilités exactes de versions entre le cœur, l’adaptateur OpenCode et OpenCode lui-même.

- Les critères de stabilité de l’intégration OpenCode ; les critères multi-runtime pourront être définis plus tard si nécessaire.

- La frontière entre état persistant, configuration et fichiers générés ; l’intérêt réel et le plan de migration éventuel de `.sayrhazi/`.
- Les critères garantissant que la refactorisation conserve l’usage des modèles gratuits OpenCode et ne crée aucune dépendance à un abonnement.

---

*Document de perspectives issu du contenu fourni. Les exemples de versions et de statuts sont illustratifs et ne constituent pas des engagements de compatibilité.*
