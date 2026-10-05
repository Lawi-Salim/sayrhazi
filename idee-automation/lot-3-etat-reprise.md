# Lot 3 — État persistant et reprise (brouillon local, non suivi)

Source : `Idee-Automation-Sayrhazi.md` §6. Dépend des Lots 1-2. Résout : « Hadji oublié après une nuit ».

## 3.1 `.opencode/state/workflow-state.yaml`

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

Vue de coordination ; les rapports restent les preuves détaillées. Distinguer : terminées, en cours, prêtes, en attente, bloquées, échouées.

## 3.2 Reprise au redémarrage

1. lire l'état ; 2. relire la config ; 3. vérifier les rapports du `task_id` actif ; 4. réconcilier rapports ↔ étapes ; 5. reprendre les seules étapes éligibles ; 6. ne jamais relancer une étape terminée ; 7. signaler toute incohérence.

## 3.3 États normalisés (à figer)

`PENDING, READY, RUNNING, TERMINÉ, VALIDÉ, VALIDÉ_AVEC_RÉSERVES, CORRECTIONS_NÉCESSAIRES, BLOCKED, FAILED, CANCELLED`. Voir écart 0.2.2 : `TERMINÉ` vs `VALIDÉ` (Lot 1).

## Impacts noyau à prévoir

Nouveau dossier `.opencode/state/` : install (créer), `.gitignore` (état local = ignorer ? à trancher : reprise multi-postes vs bruit git), tunda (présence non bloquante).
