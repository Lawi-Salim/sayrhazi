# Règles de développement du dépôt Sayrhazi

Ce dépôt contient le noyau générique du workflow Sayrhazi. Il ne contient pas de code métier de projet utilisateur.

## Séparation des responsabilités

Les fichiers `core/`, `runtimes/`, `engine/`, `cli/`, `tests/` et `docs/` définissent le système portable. Les rapports d'une instance réelle (`plan.txt`, `design.txt`, `build.txt`, `review.txt`, `security.txt`, `qa.txt`) ne doivent jamais être ajoutés à ce dépôt.

Les règles destinées aux projets qui installent Sayrhazi se trouvent dans `runtimes/opencode/templates/AGENTS.md`. Ne pas confondre ce fichier avec les règles de contribution du présent dépôt.

## Modification du noyau

Avant toute modification, identifier le problème que la modification résout, vérifier son impact sur les installations existantes et mettre à jour la documentation concernée. Les agents génériques ne doivent pas contenir de nom de projet en dur.

Toute modification du contrat de configuration, des statuts, des rapports ou des chemins doit être répercutée dans le modèle, le validateur et la documentation. Toute modification du comportement public doit être inscrite dans `CHANGELOG.md`.

## Validation minimale

Avant un commit :

1. exécuter `python tests/test_core.py`, `python tests/test_integration.py` et `python tests/test_cli.py` ;

1. exécuter `python engine/checker.py` sur une instance de test complète ;
1. vérifier la syntaxe JSON avec un parseur JSON ;
1. vérifier les scripts shell avec `bash -n` ;
1. contrôler que les scripts d'installation ne suppriment jamais les rapports ni l'historique d'un projet ;
1. rechercher les références spécifiques à un projet dans `core/` et `runtimes/`.

## Versionnement

Les changements doivent utiliser un commit descriptif. Les versions publiques du noyau sont documentées dans `CHANGELOG.md` et peuvent être marquées par des tags Git tels que `v0.1.0`.
