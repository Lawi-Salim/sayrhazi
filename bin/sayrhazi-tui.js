#!/usr/bin/env node
// Lanceur `sayrhazi-tui` : dashboard du projet Sayrhazi le plus proche.
//
// Exists pour que la commande marche sans dépendre d'un profil PowerShell :
// une fonction de profil n'est définie qu'au démarrage du terminal, donc
// `sayrhazi-tui` restait introuvable après `npm i -g sayrhazi@latest` tant que
// l'utilisateur n'avait pas rouvert son terminal.
//
//   sayrhazi-tui                      projet courant
//   sayrhazi-tui C:\mon\projet        n'importe où dans le terminal
//   sayrhazi-tui . --once             une capture, puis sortie
//   sayrhazi-tui . --interval 2       rafraîchissement toutes les 2 s
//
// Les flags après le chemin sont transmis tels quels à watch-tui.py.
"use strict";

const { spawnSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const argv = process.argv.slice(2);
const py = process.platform === "win32" ? "python" : "python3";

// Premier argument non-flag = point de départ. Seul le premier : sinon la
// valeur d'un flag (`--lines 0`) serait prise pour un chemin.
let start = ".";
let i = 0;
if (argv.length > 0 && !argv[0].startsWith("-")) {
  start = argv[0];
  i = 1;
}
const flags = argv.slice(i);

let dir = path.resolve(start);
if (!fs.existsSync(dir) || !fs.statSync(dir).isDirectory()) {
  console.error(`sayrhazi-tui : chemin introuvable (${start}).`);
  process.exit(2);
}

// Remonte jusqu'a `.opencode/watch-tui.py`, comme le dashboard lui-meme : sans
// cela, rester dans `.opencode` chercherait `.opencode/.opencode`.
let root = null;
for (;;) {
  if (fs.existsSync(path.join(dir, ".opencode", "watch-tui.py"))) {
    root = dir;
    break;
  }
  const parent = path.dirname(dir);
  if (parent === dir) break;
  dir = parent;
}
if (root === null) {
  console.error(
    `sayrhazi-tui : aucun projet Sayrhazi (pas de .opencode/watch-tui.py) au-dessus de ${start}.`);
  console.error("  Lance d'abord 'sayrhazi <projet>' pour installer.");
  process.exit(2);
}

const tui = path.join(root, ".opencode", "watch-tui.py");
// `cwd` = racine : watch-tui.py resout son projet depuis le repertoire courant.
const result = spawnSync(py, [tui, ...flags], { stdio: "inherit", cwd: root });
if (result.error) {
  console.error("sayrhazi-tui : Python introuvable (requis >= 3.10).");
  process.exit(2);
}
process.exit(result.status === null || result.status === undefined ? 1 : result.status);