#!/usr/bin/env node
// Vérification post-install (jamais bloquante) : Python, OpenCode, yarn.
// Guide l'utilisateur, n'installe rien à sa place.
"use strict";

const { execSync } = require("child_process");

function check(cmd, minMsg) {
  try {
    const out = execSync(cmd, { encoding: "utf-8", stdio: ["ignore", "pipe", "ignore"] }).trim().split("\n")[0];
    console.log(`[ok] ${minMsg} : ${out}`);
    return true;
  } catch {
    return false;
  }
}

let ok = true;
console.log("sayrhazi : vérification de l'environnement...");
if (!check("python --version", "Python (>= 3.10 requis)")) {
  if (!check("python3 --version", "Python (>= 3.10 requis)")) {
    console.log("[manquant] Python >= 3.10 — Windows : winget install Python.Python.3 | Ubuntu : apt install python3");
    ok = false;
  }
}
if (!check("opencode --version", "OpenCode")) {
  console.log("[manquant] OpenCode — npm install -g opencode-ai (tier gratuit, sans login manuel)");
  ok = false;
}
if (!check("yarn --version", "yarn")) {
  console.log("[optionnel] yarn — npm install -g yarn (requis seulement si vos projets l'utilisent)");
}
if (!check("git --version", "Git")) {
  console.log("[optionnel] Git — conseillé pour la lecture frugale (repli horodatages sinon)");
}
console.log(ok ? "sayrhazi : prêt." : "sayrhazi : installé, complétez les prérequis ci-dessus.");
(function profileHint() {
  const path = require("path");
  const script = path.join(__dirname, "..", "runtimes", "opencode", "scripts", "Sayrhazi-Profile.ps1");
  console.log("Fonctions terminal (Sayrhazi/tunda/update/info) : sourcez le profil versionné,");
  if (process.platform === "win32") {
    console.log('  . "' + script + '"');
  } else {
    const sh = path.join(__dirname, "..", "runtimes", "opencode", "scripts", "Sayrhazi-Profile.sh");
    console.log("  export SAYRHAZI_HOME=$(npm root -g)/sayrhazi  # dans ~/.bashrc");
    console.log('  . "' + sh + '"  # idem');
  }
})();
