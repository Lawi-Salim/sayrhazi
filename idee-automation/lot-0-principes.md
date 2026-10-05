# Lot 0 — Principes (brouillon local, non suivi)

Source : `Idee-Automation-Sayrhazi.md` §3 + §11. Zéro code : décisions à valider.

## 0.1 Automatiser les transitions, pas les décisions métier

Règle explicite appliquée par le moteur :

```text
un rapport identifié
+ un statut autorisé
+ une condition satisfaite
+ une transition déclarée
= un agent éligible
```

Le moteur orchestre les étapes prévues ; il ne remplace ni Lawibrahim ni l'utilisateur (architecture, périmètre, déploiement).

## 0.2 Agents conditionnels jamais systématiques

Jamais de parcours automatique `Bamse → Hadji → Hifadhui → Zawadi → Ali`. Chaque tâche déclare ses rôles nécessaires (ex. interface : Bamse/Hadji/Zawadi ; auth : Bamse/Hadji/Hifadhui sans Zawadi).

## 0.3 Terminaux ≠ mémoire du workflow

Terminaux = observation + intervention. L'état indispensable à la reprise vit dans des fichiers projet, lisible après fermeture IDE, arrêt machine ou absence prolongée.

## 0.4 Mode supervisé initial (+ `auto_start: false`)

- Transitions techniques prévues : automatiques.
- Création/lancement de tâche importante : validation humaine.
- Déploiement, suppression, migrations de données : toujours validation humaine.
- Blocage/ambiguïté : signalé, jamais deviné.

## 0.5 Ce qui reste humain (validations obligatoires)

Décision finale Lawibrahim/utilisateur ; lancement tâche importante (si supervisé) ; changement périmètre/critères ; déploiement ; migration/suppression données ; correction à solutions multiples ; blocage/incohérence non déterministe.

## 0.6 Transitions automatisables (si déclarées + vérifiées)

`plan validé → Bamse` ; `build terminé → Hadji` ; `build + security_required → Hifadhui` ; `build + visual_qa_required → Zawadi` ; `plan validé + design_required → Ali` ; `review avec corrections → Bamse`.

## Critère de sortie

Principes validés par l'utilisateur, sans ambiguïté avec le flux actuel.
