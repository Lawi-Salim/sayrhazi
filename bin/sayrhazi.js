#!/usr/bin/env node
// Lanceur `sayrhazi` : appelle le Python local sur cli/main.py.
// Noyau résolu relativement au paquet (auto-localisé, pas de SAYRHAZI_HOME).
"use strict";

const { spawnSync } = require("child_process");
const path = require("path");

const root = path.resolve(__dirname, "..");
const entry = path.join(root, "cli", "main.py");
const py = process.platform === "win32" ? "python" : "python3";

const result = spawnSync(py, [entry, ...process.argv.slice(2)], { stdio: "inherit" });
if (result.error) {
  console.error("sayrhazi : Python introuvable (requis >= 3.10).");
  process.exit(2);
}
process.exit(result.status === null || result.status === undefined ? 1 : result.status);
