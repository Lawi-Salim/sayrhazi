# Lot 2 — Configuration déclarative (brouillon local, non suivi)

Source : `Idee-Automation-Sayrhazi.md` §5. Dépend du Lot 1.

## 2.1 `.opencode/workflow.yaml`

Parcours lisible, versionnable, sans règles dispersées dans le code :

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

## 2.2 Séquentiel

`plan validé → Bamse → build terminé → Hadji → review validée → Zawadi si nécessaire → terminé`. `CORRECTIONS NÉCESSAIRES` → retour Bamse, pas de continuation vers QA.

## 2.3 Conditionnel

Hifadhui uniquement sur risque déclaré (conditions déclarées d'abord ; détection auto par analyse de code seulement plus tard, avec mécanisme explicable et testable).

## Impacts noyau à prévoir

Nouveau fichier contrat : install (créer si absent), update (ne jamais écraser), tunda/validate (vérifier présence + validité), `.gitignore` (état ? la config se versionne, elle n'est pas ignorée), template + schéma.
