# Lot 7 — Services frontend/backend séparés (brouillon local, non suivi)

Source : `Idee-Automation-Sayrhazi.md` §9. Indépendant du moteur d'agents.

Agents (rapports, workflow) et services (processus persistants `yarn dev` × 2) gérés par des logiques séparées. Futur gestionnaire : démarrage arrière-plan, vérification ports, capture logs, signalement d'arrêt. Redémarrage auto prudent (un arrêt peut être volontaire).

Cible : un terminal de contrôle + services en arrière-plan + agents invoqués par le moteur.

## Critère de sortie

Moins de terminaux, logs capturés, arrêts signalés — sans mélanger avec les transitions.
