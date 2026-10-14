#!/usr/bin/env node
// Supprime les __pycache__ récursivement (régénérés par Python au besoin).
// Utilisé en `prepack` pour un tarball propre. Jamais bloquant.
"use strict";

const fs = require("fs");
const path = require("path");

function clean(dir) {
  let removed = 0;
  let entries;
  try {
    entries = fs.readdirSync(dir, { withFileTypes: true });
  } catch {
    return 0;
  }
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (!entry.isDirectory()) {
      continue;
    }
    if (entry.name === "__pycache__" || entry.name === "node_modules") {
      try {
        fs.rmSync(full, { recursive: true, force: true });
        removed += 1;
      } catch {
        /* ignore */
      }
    } else if (entry.name !== ".git") {
      removed += clean(full);
    }
  }
  return removed;
}

const count = clean(process.cwd());
console.log(`sayrhazi : ${count} dossier(s) __pycache__ supprimé(s).`);
