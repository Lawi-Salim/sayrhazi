# Règles de reporting Sayrhazi (runtime-agnostiques).

- Dernier état dans `resume/` : `plan.txt`, `design.txt`, `build.txt`, `review.txt`, `security.txt`, `qa.txt`.
- Avant remplacement, archiver dans `history/` (`build-log.md`, `design-log.md`, `review-log.md`, `security-log.md`, `qa-log.md`).
- Chaque rapport : date système réelle, projet, `task_id` stable, auteur (`agent`, rôle stable), `completed_at` ISO 8601 (jamais `version`), `summary`, vérifications, problèmes classés `CRITIQUE / HAUTE / MOYENNE / FAIBLE`, limites, suite, verdict du rôle. `next_agents` optionnel.
- Statuts : `TERMINÉ` = achèvement, `VALIDÉ` = verdict, ne pas les mélanger. Plan `À IMPLÉMENTER / INFORMATIF / VALIDÉ` ; implémentation `EN COURS / TERMINÉ / BLOQUÉ` ; design `PROPOSÉ / VALIDÉ` ; review/sécurité `VALIDÉ / VALIDÉ AVEC RÉSERVES / CORRECTIONS NÉCESSAIRES` ; QA ajoute `À COMPLÉTER`.
- `plan.txt` cumulatif jusqu'à archivage explicite d'une feature dans `features/<nom-stable>.md`.
