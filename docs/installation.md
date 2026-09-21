# Installer Sayrhazi

## Prérequis

L'installation nécessite uniquement un projet existant, Git est recommandé, et PowerShell sous Windows ou Bash sous Linux/macOS. Sayrhazi ne nécessite pas Docker. Docker n'est ajouté que si le projet applicatif en a besoin.

## Depuis n'importe quel projet (recommandé)

Inutile d'ouvrir le dépôt Sayrhazi : le script retrouve sa source tout seul. Depuis le projet cible :

```powershell
& "C:\Users\Lawibrahim\Documents\Sayrhazi\scripts\Install-Sayrhazi.ps1" -ProjectPath "."
```

Avec la fonction de profil (voir `SAYRHAZI_HOME`) :

```powershell
Sayrhazi .
tunda sayrhazi
```

## Depuis le dépôt Sayrhazi

```powershell
cd C:\Users\Lawibrahim\Documents\Sayrhazi
.\scripts\Install-Sayrhazi.ps1 -ProjectPath "C:\Users\Lawibrahim\Documents\MonProjet"
```

## Linux et macOS

Rendre le script exécutable puis l'appeler avec la racine du projet :

```bash
chmod +x scripts/install-sayrhazi.sh
./scripts/install-sayrhazi.sh /chemin/vers/MonProjet
```

## Ce que fait l'installation

Le script crée `.opencode/agent/`, `resume/`, `history/` et `features/`, puis copie les cinq agents génériques et `watch-work.py` (mis à jour à chaque install). Il crée `AGENTS.md`, `sayrhazi.yaml` et `opencode.json` uniquement lorsqu'ils sont absents. Il ne supprime ni ne remplace les rapports, historiques, décisions ou configuration déjà présents.

Les fichiers d'agents sont les fichiers fournis par Sayrhazi et peuvent être actualisés par une future version. Pour un projet existant, effectuer un commit ou une sauvegarde avant toute mise à jour et relire les différences.

## Après installation

Compléter `.opencode/sayrhazi.yaml`, notamment `project.name`, les commandes réelles et les options de QA. Vérifier les règles locales dans `AGENTS.md` (§4), puis lancer le check depuis le projet :

```powershell
tunda sayrhazi
# ou sans alias : python "$env:SAYRHAZI_HOME/scripts/tunda.py" sayrhazi --project .
```

Ouvrir ensuite OpenCode depuis la racine du projet utilisateur, pas depuis le dépôt Sayrhazi.

## Mise à jour (`update sayrhazi`)

Quand le noyau évolue, mettre à jour depuis un projet déjà intégré :

```powershell
update sayrhazi
```

Cela réinstalle agents + `watch-work.py` (mis à jour avec `-Force`), affiche `version projet -> noyau`, signale les fichiers `agent/*.md` inconnus du noyau (suppression manuelle), puis relance le check. Configuration, rapports, historiques, décisions et `AGENTS.md` ne sont jamais écrasés.

## Mise à jour prudente

Ne jamais déplacer l'historique d'un projet sans sauvegarde. Pour une migration, conserver les rapports et décisions, comparer les agents existants avec la version Sayrhazi, puis intégrer les changements par commit identifiable.
