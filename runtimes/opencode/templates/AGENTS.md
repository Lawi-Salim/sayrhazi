# Règles du projet — Sayrhazi

Ce projet utilise le workflow Sayrhazi. Les agents lisent `.opencode/sayrhazi.yaml` comme seule source de vérité pour le nom, le type, la stack et les commandes du projet en cours.

## 1. Configuration

- Compléter `.opencode/sayrhazi.yaml` avant la première tâche (`project.name`, `description`, `technical`, `commands`, `runtime`, `quality`).
- Ne jamais laisser `A_COMPLETER` dans la configuration utilisée.
- Toute commande (install, dev, build, test, lint) doit venir de `sayrhazi.yaml`, jamais d'une supposition.

## 2. Agents

- **Lawibrahim** : clarifie et consigne les décisions validées dans `.opencode/resume/plan.txt`. Ne code pas.
- **Ali** : design UI/UX à partir de `plan.txt` (maquettes, écrans, composants, responsive, thèmes), écrit `.opencode/resume/design.txt`. Crée la structure visuelle neuve, ne modifie ni l'existant ni la logique.
- **Bamse** : implémente à partir de `plan.txt` et `design.txt`, vérifie, écrit `.opencode/resume/build.txt`. Seul à modifier le code existant et à implémenter la logique.
- **Hadji** : review qualité à partir de `build.txt`, écrit `review.txt`. Ne code pas.
- **Hifadhui** : audit sécurité à partir de `build.txt`, écrit `security.txt`. Ne code pas.
- **Zawadi** : QA réelle (navigateur ou captures), écrit `qa.txt`. Ne déduit jamais un rendu du seul code.
- Chaque agent se présente avec le nom du projet lu dans `sayrhazi.yaml`, uniquement à l'ouverture de la session ou sur demande, jamais à chaque réponse.
- Les noms d'affichage des agents se configurent dans `.opencode/sayrhazi.yaml` (`agents.*`, défauts : Lawibrahim, Ali, Bamse, Hadji, Hifadhui, Zawadi). Les fichiers `agent/*.md` et les rôles restent stables.
- Réponses et rapports toujours en français, sauf demande contraire de l'utilisateur. Emojis proscrits dans le travail, tolérés uniquement en échange léger ou blague. Typographie française correcte exigée : accents, apostrophes, cédilles.

## 3. Rapports

- Dernier état dans `.opencode/resume/` : `plan.txt`, `design.txt`, `build.txt`, `review.txt`, `security.txt`, `qa.txt`.
- Avant remplacement, archiver l'ancien contenu dans `.opencode/history/` (`build-log.md`, `design-log.md`, `review-log.md`, `security-log.md`, `qa-log.md`).
- Chaque rapport contient : date système réelle, projet, tâche (`task_id` stable, ex. `FEATURE-001`), vérifications, problèmes classés `CRITIQUE / HAUTE / MOYENNE / FAIBLE`, limites, suite et verdict du rôle.
- Statuts : Bamse `EN COURS / TERMINÉ / BLOQUÉ`, Hadji et Hifadhui `VALIDÉ / VALIDÉ AVEC RÉSERVES / CORRECTIONS NÉCESSAIRES`, Zawadi ajoute `À COMPLÉTER`.
- Aucun secret, token ou mot de passe dans les rapports.

## 4. Règles locales du projet — À COMPLÉTER

Ajouter ici les règles propres à ce projet (stack, conventions, architecture, commandes spécifiques, exigences qualité) :

- ...
