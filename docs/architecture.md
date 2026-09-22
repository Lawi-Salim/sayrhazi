# Architecture de Sayrhazi

## Rôle du système

Sayrhazi est un workflow multi-agents portable. Il organise le cycle de développement autour de rôles spécialisés, de rapports courts et d'un historique local au projet. Sayrhazi n'est pas une application métier et n'impose ni base de données, ni serveur, ni Docker.

Le noyau est versionné séparément des applications qui l'utilisent. Une application installe une copie locale des agents et des modèles dans son propre dossier `.opencode/`.

## Deux niveaux

Le dépôt Sayrhazi contient les éléments réutilisables : agents, modèles, schéma, scripts et documentation. Le projet utilisateur contient son code, ses règles locales, sa configuration `sayrhazi.yaml`, ses rapports et son historique.

```text
Sayrhazi/
├── agents/       rôles génériques
├── template/     fichiers installés dans un projet
├── schemas/      contrats de configuration (appliqués par validate et tunda)
├── scripts/      installation, validation, mise à jour, watcher et check
├── docs/         documentation
└── AGENTS.md     règles de contribution au noyau

Projet/
├── AGENTS.md
└── .opencode/
    ├── agent/          5 agents installés
    ├── sayrhazi.yaml   configuration locale
    ├── opencode.json   permissions locales
    ├── watch-work.py   orchestrateur build.txt → Hadji
    ├── resume/
    ├── history/
    └── features/
```

## Rôles

Lawibrahim clarifie le besoin et consigne les décisions validées. Bamse implémente et vérifie le code. Hadji contrôle la qualité générale, sans remplacer l'audit sécurité. Hifadhui examine les risques de sécurité. Zawadi vérifie le comportement réel et l'expérience visuelle lorsqu'un navigateur ou des captures sont disponibles.

Les rôles sont séparés pour éviter l'auto-validation. Les agents de review, sécurité et QA analysent et rapportent ; ils ne modifient pas le code source.

## Projet courant

Le nom du projet n'est jamais codé dans les agents. Il est lu dans `.opencode/sayrhazi.yaml`. Les règles techniques et métier spécifiques restent dans le `AGENTS.md` du projet utilisateur.
