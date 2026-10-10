# Lot 1 — Contrats et données minimales (brouillon local, non suivi)

> **Statut :** clos (v0.4.0)

Source : `Idee-Automation-Sayrhazi.md` §4. Fondation prioritaire : sans contrats stables, aucun moteur ne distingue un nouveau rapport d'un ancien fichier.

## 1.1 `task_id` obligatoire (à trancher : format)

```yaml
task_id: MPANGO-2026-014
status: VALIDÉ
title: Ajouter le filtre par date dans la liste des engagements
```

Recopié dans chaque rapport de la tâche. Écart : convention actuelle `FEATURE-001` vs `MPANGO-2026-014` → garder ou namespacer par projet.

## 1.2 Besoins de la tâche déclarés

```yaml
agents_required:
  - bamse
  - hadji
  - zawadi

security_required: false
visual_qa_required: true
design_required: false
```

Listes explicites = source de vérité ; indicateurs = raccourcis, jamais en contradiction. Noms d'agents : utiliser les identifiants stables (fichiers), pas les noms d'affichage configurables.

## 1.3 Critères d'acceptation

Résultats attendus listés (ex. filtre dates, état vide, mobile). Permettent de distinguer « étape terminée » de « fichier modifié ».

## 1.4 Contrat minimal d'un rapport

```yaml
task_id: MPANGO-2026-014
agent: bamse
status: TERMINÉ
completed_at: "2026-09-23T19:30:00+04:00"
summary: "Fonctionnalité implémentée et vérifiée localement."
next_agents:
  - hadji
  - zawadi
```

À trancher : `version` comme horodatage → préférer `completed_at` (évite la confusion avec `workflow.version`).

## 1.5 Validation avant transition (8 points)

1. fichier attendu existe ; 2. stable après écriture ; 3. `task_id` = tâche active ; 4. statut autorisé ; 5. auteur déclaré = agent attendu ; 6. pas d'exécution identique en cours ; 7. pas de rapport de sortie équivalent présent ; 8. délai max respecté. Le hash ne prouve ni la tâche, ni la validité, ni l'autorisation.

État actuel : `watch-work.py` couvre 1, 2, 3, 4, 6 + partiel 8. Manquent : 5 (auteur), 7 (sortie existante).

## 1.6 À trancher aussi

- Statut `VALIDÉ` pour `plan.txt` (contrat actuel : `À IMPLÉMENTER`/`INFORMATIF`).
- `TERMINÉ` (achèvement) vs `VALIDÉ` (verdict) figés et distincts.

## Critère de sortie

`docs/reports.md` étendu (contrat + statuts figés + format `task_id`), validateurs capables de vérifier les nouveaux champs.
