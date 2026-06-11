#!/usr/bin/env bash
# Trova repository git abbandonati e ingombranti, candidati allo spostamento.
#
# Un repo è "abbandonato" (candidato) se TUTTE queste condizioni valgono:
#   - nessun commit recente               (git log --all --since)
#   - nessun file sorgente modificato di recente (mtime, escludendo build/deps)
#   - dimensione totale > soglia          (du -sx)
#   - NON ha modifiche non committate     (i repo "dirty" sono esclusi per sicurezza)
#
# Lo script SOLO elenca: non sposta e non cancella nulla.
#
# Uso: stale-repos.sh [-d giorni] [-s size_mb] [-r root]

set -euo pipefail

DAYS=180
SIZE_MB=100
ROOT="$HOME"

usage() {
    cat <<EOF
Uso: $0 [-d giorni] [-s size_mb] [-r root]

  -d, --days N      Soglia di inattività in giorni (default: 180, ~6 mesi)
  -s, --size-mb N   Dimensione minima della cartella in MB (default: 100)
  -r, --root PATH   Cartella da cui partire (default: \$HOME)
  -h, --help        Mostra questo aiuto

Elenca i repo git inattivi da più di N giorni (per commit e per modifica file)
e più grandi di size_mb MB. I repo con modifiche non committate sono esclusi.
Resta sempre sul filesystem di ROOT (-xdev): /mnt e i mount Windows sono ignorati.
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -d|--days)    DAYS="${2:-}"; shift 2 ;;
        -s|--size-mb) SIZE_MB="${2:-}"; shift 2 ;;
        -r|--root)    ROOT="${2:-}"; shift 2 ;;
        -h|--help)    usage; exit 0 ;;
        *) echo "Opzione sconosciuta: $1" >&2; usage >&2; exit 1 ;;
    esac
done

[[ "$DAYS"    =~ ^[0-9]+$ ]] || { echo "Errore: --days deve essere un intero" >&2; exit 1; }
[[ "$SIZE_MB" =~ ^[0-9]+$ ]] || { echo "Errore: --size-mb deve essere un intero" >&2; exit 1; }
[[ -d "$ROOT" ]] || { echo "Errore: root inesistente: $ROOT" >&2; exit 1; }

# ── colori ──────────────────────────────────────────────────────────────────
YELLOW='\033[1;33m'; CYAN='\033[0;36m'; GREEN='\033[0;32m'; BOLD='\033[1m'; NC='\033[0m'

# Directory pesanti/generate da escludere. Per la DISCOVERY non si esclude .git
# (altrimenti verrebbe potato prima di essere stampato); per il check mtime sì.
PRUNE_BUILD=(node_modules .venv venv target build dist .next .cache __pycache__)

# Espressione -prune per la discovery dei repo (senza .git)
disc_expr=()
for d in "${PRUNE_BUILD[@]}"; do disc_expr+=(-name "$d" -o); done
unset 'disc_expr[${#disc_expr[@]}-1]'

# Espressione -prune per il check mtime (build + .git)
mtime_expr=()
for d in "${PRUNE_BUILD[@]}" .git; do mtime_expr+=(-name "$d" -o); done
unset 'mtime_expr[${#mtime_expr[@]}-1]'

human() {  # KB -> stringa leggibile
    local kb=${1:-0}
    if   (( kb >= 1048576 )); then printf "%.1f GB" "$(echo "scale=1; $kb/1048576" | bc)"
    elif (( kb >= 1024 ));    then printf "%.0f MB"  "$(echo "scale=0; $kb/1024"    | bc)"
    else printf "%d KB" "$kb"
    fi
}

echo -e "${BOLD}${CYAN}Scansione di${NC} $ROOT  ${BOLD}(>${DAYS}gg, >${SIZE_MB}MB)${NC}" >&2

# ── discovery: cartelle .git, saltando le dir pesanti e restando sul fs ──────
mapfile -t gitdirs < <(
    find "$ROOT" -xdev \( "${disc_expr[@]}" \) -prune -o -type d -name .git -print -prune 2>/dev/null
)

scanned=0
results=()        # "kb<TAB>last_commit<TAB>path"
total_kb=0

for gd in "${gitdirs[@]}"; do
    repo="${gd%/.git}"
    scanned=$(( scanned + 1 ))

    # 1) commit recente? -> attivo, salta
    if git -C "$repo" log --all --since="${DAYS} days ago" -1 --format=%H >/dev/null 2>&1 \
        && [[ -n "$(git -C "$repo" log --all --since="${DAYS} days ago" -1 --format=%H 2>/dev/null)" ]]; then
        continue
    fi

    # 2) file sorgente modificato di recente? -> attivo, salta (-quit: esce al primo hit)
    if [[ -n "$(find "$repo" -xdev \( "${mtime_expr[@]}" \) -prune -o -type f -mtime -"$DAYS" -print -quit 2>/dev/null)" ]]; then
        continue
    fi

    # 3) modifiche non committate (dirty)? -> escluso per sicurezza
    if [[ -n "$(git -C "$repo" status --porcelain 2>/dev/null)" ]]; then
        continue
    fi

    # 4) dimensione sopra soglia?
    kb=$(du -sx "$repo" 2>/dev/null | awk 'NR==1{print $1}')
    [[ "$kb" =~ ^[0-9]+$ ]] || kb=0
    (( kb / 1024 >= SIZE_MB )) || continue

    last=$(git -C "$repo" log --all -1 --format=%cd --date=short 2>/dev/null || true)
    [[ -n "$last" ]] || last="no-commit"

    results+=("${kb}	${last}	${repo}")
    total_kb=$(( total_kb + kb ))
done

echo -e "${BOLD}Repo git analizzati:${NC} $scanned" >&2

if (( ${#results[@]} == 0 )); then
    echo -e "${GREEN}Nessun repo abbandonato sopra le soglie.${NC}"
    exit 0
fi

echo ""
printf "${BOLD}%-10s  %-12s  %s${NC}\n" "DIMENSIONE" "ULT.COMMIT" "PERCORSO"
# ordina per dimensione decrescente
while IFS=$'\t' read -r kb last path; do
    printf "%-10s  %-12s  %s\n" "$(human "$kb")" "$last" "$path"
done < <(printf '%s\n' "${results[@]}" | sort -t$'\t' -k1,1nr)

echo ""
echo -e "${BOLD}Candidati:${NC} ${#results[@]}   ${BOLD}Spazio recuperabile:${NC} ${YELLOW}$(human "$total_kb")${NC}"
echo -e "(${BOLD}solo elenco${NC} — nessuna cartella è stata spostata o rimossa)"
