# Sayrhazi-Profile.sh — fonctions shell Sayrhazi (versionné dans le dépôt).
#
# Sourcing (une fois, dans ~/.bashrc) — SAYRHAZI_HOME pointe vers le noyau
# (clone ou paquet npm : $(npm root -g)/sayrhazi) :
#   export SAYRHAZI_HOME="$HOME/sayrhazi"
#   . "$SAYRHAZI_HOME/runtimes/opencode/scripts/Sayrhazi-Profile.sh"
#
# Fonctions : Sayrhazi, tunda, update, info, remove, sayrhazi-tui
#             (+ Sayrhazi-Install/Check/Update).
# Les flags (-*, ex. --version) vont au CLI ; un chemin va à l'installeur.
# Bash sensible à la casse : `Sayrhazi` (fonction) et `sayrhazi` (bin npm) coexistent.

Sayrhazi-Install() {
    local project="${1:-.}"
    bash "$SAYRHAZI_HOME/runtimes/opencode/scripts/install-sayrhazi.sh" "$project"
}

Sayrhazi-Check() {
    local project="${1:-.}"
    python3 "$SAYRHAZI_HOME/engine/checker.py" "$project"
}

Sayrhazi-Update() {
    local project="${1:-.}"
    python3 "$SAYRHAZI_HOME/engine/updater.py" --project "$project" || return
    Sayrhazi-Check "$project"
}

sayrhazi-tui() {
    # Dashboard du projet. Le premier argument est le point de depart, pas un
    # flag ; la racine reelle est cherchee en remontant :
    #   sayrhazi-tui                  (projet courant)
    #   sayrhazi-tui /chemin/projet
    #   sayrhazi-tui . --once        (une seule capture, puis sortie)
    # Marcher depuis `.opencode` ou un sous-dossier fonctionne donc aussi.
    local start="."
    if [ $# -gt 0 ]; then
        case "$1" in
            -*) ;;
            *) start="$1"; shift ;;
        esac
    fi
    if [ ! -d "$start" ]; then
        echo "sayrhazi-tui : chemin introuvable ($start)." >&2
        return 1
    fi
    # Remonte jusqu'a trouver un `.opencode/watch-tui.py`, comme le dashboard.
    local dir="$start" racine=""
    while [ -n "$dir" ]; do
        if [ -f "$dir/.opencode/watch-tui.py" ]; then racine="$dir"; break; fi
        [ "$dir" = "/" ] && break
        dir="$(dirname "$dir")"
    done
    if [ -z "$racine" ]; then
        echo "sayrhazi-tui : aucun projet Sayrhazi (pas de .opencode/watch-tui.py) au-dessus de $start." >&2
        echo "  Lance d'abord 'Sayrhazi $start' pour installer." >&2
        return 1
    fi
    # Le dashboard resout sa racine depuis le repertoire courant : le sous-shell
    # change de dossier sans toucher a l'appelant, sans quoi il analyserait le
    # dossier du terminal au lieu du projet demande.
    ( cd "$racine" && python3 .opencode/watch-tui.py "$@" )
}

tunda() {
    local sub="${1:-sayrhazi}" project="${2:-.}"
    if [ "$sub" != "sayrhazi" ]; then echo "Usage: tunda sayrhazi"; return 1; fi
    python3 "$SAYRHAZI_HOME/cli/commands/check.py" "$sub" --project "$project"
}

update() {
    local sub="${1:-sayrhazi}" project="${2:-.}"
    if [ "$sub" != "sayrhazi" ]; then echo "Usage: update sayrhazi"; return 1; fi
    Sayrhazi-Update "$project"
}

info() {
    local sub="${1:-sayrhazi}" project="${2:-.}"
    if [ "$sub" != "sayrhazi" ]; then echo "Usage: info sayrhazi"; return 1; fi
    python3 "$SAYRHAZI_HOME/cli/main.py" info --project "$project"
}

remove() {
    local path="." yes=0 a
    for a in "$@"; do
        if [ "$a" = "--yes" ]; then yes=1;
        elif [ "$a" = "sayrhazi" ]; then :
        elif [ "$path" = "." ]; then path="$a";
        else echo "Usage: remove sayrhazi [chemin] [--yes]"; return 1; fi
    done
    python3 "$SAYRHAZI_HOME/cli/main.py" remove --project "$path" || return
    if [ "$yes" -eq 0 ]; then
        read -r -p "Supprimer vraiment ces fichiers ? (tapez yes) " ans
        [ "$ans" = "yes" ] || { echo "Annule, rien n'a ete supprime."; return 0; }
    fi
    python3 "$SAYRHAZI_HOME/cli/main.py" remove --project "$path" --yes
}

Sayrhazi() {
    if [ $# -ge 1 ]; then
        case "$1" in
            -*) python3 "$SAYRHAZI_HOME/cli/main.py" "$@"; return $? ;;
            check|install)
                local sub="$1"; shift
                Sayrhazi-"${sub^}" "${1:-.}"
                return $? ;;
        esac
    fi
    local path="${1:-.}"
    python3 "$SAYRHAZI_HOME/engine/banner.py" sayrhazi
    Sayrhazi-Install "$path" || { echo "Installation echouee."; return 1; }
    Sayrhazi-Check "$path"
}
