# Sayrhazi-Profile.ps1 — fonctions de profil Sayrhazi (versionné dans le dépôt).
#
# Sourcing (une fois, dans $PROFILE) — remplace tout bloc Sayrhazi existant :
#   $env:SAYRHAZI_HOME = "C:\chemin\vers\Sayrhazi"
#   . "$env:SAYRHAZI_HOME\runtimes\opencode\scripts\Sayrhazi-Profile.ps1"
#
# Fonctions : Sayrhazi, tunda, update, info, remove, sayrhazi-tui
#             (+ Sayrhazi-Install/Check/Update).
# Les flags (-*, ex. --version) vont au CLI ; un chemin va à l'installeur.

$env:PYTHONIOENCODING = "utf-8"
try { chcp 65001 | Out-Null } catch {}
try { [console]::InputEncoding = [console]::OutputEncoding = [System.Text.UTF8Encoding]::new() } catch {}

function Sayrhazi-Install {
    param([string]$ProjectPath = ".")
    & "$env:SAYRHAZI_HOME\runtimes\opencode\scripts\Install-Sayrhazi.ps1" -ProjectPath $ProjectPath
}

function Sayrhazi-Check {
    param([string]$ProjectPath = ".")
    python "$env:SAYRHAZI_HOME\engine\checker.py" $ProjectPath
}

function Sayrhazi-Update {
    param([string]$ProjectPath = ".")
    python "$env:SAYRHAZI_HOME\engine\updater.py" --project $ProjectPath
    if ($LASTEXITCODE -ne 0) { return }
    Sayrhazi-Check $ProjectPath
    # Une fonction de profil n'existe que dans la session qui l'a definie, et
    # on ne peut pas la pousser vers la session appelante depuis une fonction :
    # `update` ne peut donc pas installer une nouvelle commande pour
    # l'utilisateur. Deux sorties : `npm i -g sayrhazi@latest` (binaire sur le
    # PATH, independant de toute session) ou rechargement manuel du profil.
    $bin = Get-Command sayrhazi-tui -ErrorAction SilentlyContinue
    if (-not $bin) {
        Write-Host "Noyau a jour. Pour utiliser 'sayrhazi-tui' dans cette session :" -ForegroundColor Yellow
        Write-Host "  . `$env:SAYRHAZI_HOME\runtimes\opencode\scripts\Sayrhazi-Profile.ps1" -ForegroundColor Yellow
        Write-Host "ou installez le binaire (independante du profil) :" -ForegroundColor Yellow
        Write-Host "  npm i -g sayrhazi@latest" -ForegroundColor Yellow
    }
}

function sayrhazi-tui {
    # Dashboard du projet. Le premier argument est le point de départ, pas un
    # flag ; la racine reelle est cherchee en remontant :
    #   sayrhazi-tui                          (projet courant)
    #   sayrhazi-tui C:\mon\projet
    #   sayrhazi-tui . --once                 (une seule capture, puis sortie)
    # Marcher depuis `.opencode` ou un sous-dossier fonctionne donc aussi.
    param(
        [Parameter(ValueFromRemainingArguments = $true)][string[]]$Args
    )
    $rest = @($Args)
    $start = "."
    # Seul le premier argument peut etre le projet : sinon la valeur d'un flag
    # (`--lines 0`) serait prise pour un chemin.
    if ($rest.Count -gt 0 -and $rest[0] -notlike "-*") {
        $start = $rest[0]
        $rest = @()
        if ($Args.Count -gt 1) { $rest = @($Args[1..($Args.Count - 1)]) }
    }
    $dir = $null
    try { $dir = (Resolve-Path -LiteralPath $start -ErrorAction Stop).Path } catch {}
    if (-not $dir) {
        Write-Host "sayrhazi-tui : chemin introuvable ($start)." -ForegroundColor Red
        return
    }
    # Remonte jusqu'a trouver un `.opencode/watch-tui.py`, comme le dashboard.
    $racine = $null
    while ($dir) {
        if (Test-Path -LiteralPath (Join-Path $dir ".opencode\watch-tui.py")) { $racine = $dir; break }
        $parent = Split-Path -Parent $dir
        if (-not $parent -or $parent -eq $dir) { break }
        $dir = $parent
    }
    if (-not $racine) {
        Write-Host "sayrhazi-tui : aucun projet Sayrhazi (pas de .opencode\watch-tui.py) au-dessus de $start." -ForegroundColor Red
        Write-Host "  Lance d'abord 'Sayrhazi $start' pour installer." -ForegroundColor Yellow
        return
    }
    # Le dashboard resout sa racine depuis le repertoire courant : sans ce
    # changement, il analyserait le dossier du terminal au lieu du projet.
    Push-Location -LiteralPath $racine
    try { python .opencode\watch-tui.py @rest } finally { Pop-Location }
}

function tunda {
    param([string]$Sub = "sayrhazi", [string]$ProjectPath = ".")
    if ($Sub -ne "sayrhazi") { Write-Host "Usage: tunda sayrhazi" -ForegroundColor Yellow; return }
    python "$env:SAYRHAZI_HOME\cli\commands\check.py" $Sub --project $ProjectPath
}

function update {
    param([string]$Sub = "sayrhazi", [string]$ProjectPath = ".")
    if ($Sub -ne "sayrhazi") { Write-Host "Usage: update sayrhazi" -ForegroundColor Yellow; return }
    Sayrhazi-Update $ProjectPath
}

function info {
    param([string]$Sub = "sayrhazi", [string]$ProjectPath = ".")
    if ($Sub -ne "sayrhazi") { Write-Host "Usage: info sayrhazi" -ForegroundColor Yellow; return }
    python "$env:SAYRHAZI_HOME\cli\main.py" info --project $ProjectPath
}

function remove {
    param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Args)
    $path = "."
    $yes = $false
    foreach ($a in $Args) {
        if ($a -eq "--yes") { $yes = $true }
        elseif ($a -eq "sayrhazi") { }
        elseif ($path -eq ".") { $path = $a }
        else { Write-Host "Usage: remove sayrhazi [chemin] [--yes]" -ForegroundColor Yellow; return }
    }
    python "$env:SAYRHAZI_HOME\cli\main.py" remove --project $path
    if ($LASTEXITCODE -eq 3) { return }
    if ($LASTEXITCODE -ne 0) { return }
    if (-not $yes) {
        $ans = Read-Host "Supprimer vraiment ces fichiers ? (tapez yes)"
        if ($ans -ne "yes") { Write-Host "Annule, rien n'a ete supprime."; return }
    }
    python "$env:SAYRHAZI_HOME\cli\main.py" remove --project $path --yes
}

function Sayrhazi {
    param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Args)
    if ($Args.Count -ge 1 -and $Args[0] -like "-*") {
        python "$env:SAYRHAZI_HOME\cli\main.py" @Args
        return
    }
    $sub = ""
    $path = "."
    if ($Args.Count -ge 1) {
        if ($Args[0] -in @("check", "install")) {
            $sub = $Args[0]
            if ($Args.Count -ge 2) { $path = $Args[1] }
        } else {
            $path = $Args[0]
        }
    }
    switch ($sub) {
        "check" { Sayrhazi-Check $path }
        "install" {
            python "$env:SAYRHAZI_HOME\engine\banner.py" sayrhazi
            Sayrhazi-Install $path
            if (-not $?) { Write-Host "Installation echouee." -ForegroundColor Red; return }
            Sayrhazi-Check $path
        }
        default {
            python "$env:SAYRHAZI_HOME\engine\banner.py" sayrhazi
            Sayrhazi-Install $path
            if (-not $?) {
                Write-Host "Installation echouee." -ForegroundColor Red
                return
            }
            Sayrhazi-Check $path
            if ($LASTEXITCODE -ne 0) {
                Write-Host "Install OK, mais config incomplete : complete .opencode/sayrhazi.yaml (A_COMPLETER restant)." -ForegroundColor Yellow
            }
        }
    }
}
