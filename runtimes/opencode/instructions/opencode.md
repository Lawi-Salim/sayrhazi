# Spécificités OpenCode apprises (adaptateur).

- Frontmatter agent : `description`, `mode: primary`, `model`, `color` (hexadécimal `#RRGGBB` exigé, sinon erreur de configuration au lancement).
- Permissions MCP : `playwright_*: allow` par agent (Ali, Zawadi), `deny` global dans `opencode.json`.
- Les agents se lisent dans `.opencode/agent/` ; OpenCode charge `AGENTS.md` à la racine du dépôt ouvert.
- Console Windows PowerShell 5.1 : sorties scripts en ASCII (UTF-8 sans BOM mal lu) ; `chcp 65001` + `PYTHONIOENCODING=utf-8` dans le profil.
