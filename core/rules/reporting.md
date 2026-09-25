# Règles de reporting Sayrhazi (runtime-agnostiques).

- Dernier état dans `resume/` : `plan.txt`, `design.txt`, `build.txt`, `review.txt`, `security.txt`, `qa.txt`.
- Avant remplacement, archiver dans `history/` (`build-log.md`, `design-log.md`, `review-log.md`, `security-log.md`, `qa-log.md`).
- Chaque rapport : date système réelle, projet, `task_id` stable, vérifications, problèmes classés `CRITIQUE / HAUTE / MOYENNE / FAIBLE`, limites, suite, verdict du rôle.
- Statuts : implémentation `EN COURS / TERMINÉ / BLOQUÉ` ; design `PROPOSÉ / VALIDÉ` ; review/sécurité `VALIDÉ / VALIDÉ AVEC RÉSERVES / CORRECTIONS NÉCESSAIRES` ; QA ajoute `À COMPLÉTER`.
- `plan.txt` cumulatif jusqu'à archivage explicite d'une feature dans `features/<nom-stable>.md`.
