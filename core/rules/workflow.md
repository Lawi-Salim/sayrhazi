# Règles de workflow Sayrhazi (runtime-agnostiques).

- Flux : planification → design (si visuel) → implémentation → review → sécurité (si risque) → QA (si observable). Projet vierge : squelette d'abord, via l'implémentation.
- Seule la transition `build.txt TERMINÉ + task_id → review` peut être automatique ; le reste est orchestré par l'humain.
- Un verdict `CORRECTIONS NÉCESSAIRES` renvoie vers l'implémentation, jamais vers l'étape suivante.
- Les agents conditionnels (design, sécurité, QA) ne sont lancés que si requis.
- Déploiement, suppression et migrations de données : toujours validation humaine.
