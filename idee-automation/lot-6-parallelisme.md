# Lot 6 — Parallélisation et convergence (brouillon local, non suivi)

> **Statut :** clos (v0.9.0)

Source : `Idee-Automation-Sayrhazi.md` §7. Après stabilisation Lots 4-5.

```text
Bamse terminé
      ├── Hadji
      ├── Hifadhui
      └── Zawadi

Hadji    ─┐
Hifadhui ─┼── convergence
Zawadi   ─┘
          ↓
     décision suivante
```

Exprimer : étapes parallélisables, dépendances de groupe, `max_parallel_agents` (garde-fou machine), échec d'une branche, branche non requise. Étape suivante seulement après résultats attendus.

## Critère de sortie

Hadji+Hifadhui+Zawadi parallèles testés, convergence vérifiée, pas de surcharge.
