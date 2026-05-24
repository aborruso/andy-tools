#!/usr/bin/env bash
# Pulisce cache e file temporanei sicuri su Linux (ottimizzato per WSL2).
# Uso: linux-cleanup.sh [--dry-run] [--no-sudo]

set -euo pipefail

DRY_RUN=false
NO_SUDO=false

for arg in "$@"; do
    case $arg in
        --dry-run) DRY_RUN=true ;;
        --no-sudo) NO_SUDO=true ;;
        --help|-h)
            echo "Uso: $0 [--dry-run] [--no-sudo]"
            echo "  --dry-run   Mostra cosa verrebbe rimosso senza agire"
            echo "  --no-sudo   Salta la sezione che richiede sudo (apt, journal)"
            exit 0 ;;
        *) echo "Opzione sconosciuta: $arg"; exit 1 ;;
    esac
done

# ── colori ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

FREED_TOTAL=0

# ── helper: dimensione in byte di un path ───────────────────────────────────
path_bytes() {
    local size
    size=$(du -sb "$1" 2>/dev/null | awk 'NR==1{print $1}')
    printf '%s' "${size:-0}"
}

human_size() {
    local bytes=${1:-0}
    # rimuove eventuale newline residua
    bytes="${bytes%%$'\n'*}"
    [[ "$bytes" =~ ^[0-9]+$ ]] || bytes=0
    if   (( bytes >= 1073741824 )); then printf "%.1f GB" "$(echo "scale=1; $bytes/1073741824" | bc)"
    elif (( bytes >= 1048576 ));    then printf "%.0f MB"  "$(echo "scale=0; $bytes/1048576"    | bc)"
    elif (( bytes >= 1024 ));       then printf "%.0f KB"  "$(echo "scale=0; $bytes/1024"       | bc)"
    else printf "%d B" "$bytes"
    fi
}

section() { echo -e "\n${BOLD}${CYAN}══ $1 ══${NC}"; }

# ── helper: rimuove una directory ───────────────────────────────────────────
clean_dir() {
    local path="$1" label="$2"
    [[ ! -e "$path" ]] && return
    local size; size=$(path_bytes "$path")
    local human; human=$(human_size "$size")
    if $DRY_RUN; then
        echo -e "  ${YELLOW}[dry-run]${NC} $label  ${RED}$human${NC}"
    else
        echo -e "  ${GREEN}✓${NC} $label  ${RED}$human${NC}"
        rm -rf "$path"
        FREED_TOTAL=$(( FREED_TOTAL + size ))
    fi
}

# ── helper: esegue un comando di pulizia con etichetta ──────────────────────
clean_cmd() {
    local label="$1" cmd="$2" size_path="${3:-}"
    local size=0 human=""
    if [[ -n "$size_path" && -e "$size_path" ]]; then
        size=$(path_bytes "$size_path")
        human=$(human_size "$size")
    fi
    if $DRY_RUN; then
        echo -e "  ${YELLOW}[dry-run]${NC} $label${human:+  ${RED}$human${NC}}"
    else
        echo -e "  ${GREEN}✓${NC} $label${human:+  ${RED}$human${NC}}"
        eval "$cmd"
        FREED_TOTAL=$(( FREED_TOTAL + size ))
    fi
}

# ════════════════════════════════════════════════════════════════════════════
section "Cache utente (~/.cache)"

# uv
if command -v uv &>/dev/null && [[ -d ~/.cache/uv ]]; then
    clean_cmd "uv cache" "uv cache clean -q" ~/.cache/uv
fi

# Go build cache
if command -v go &>/dev/null && [[ -d ~/.cache/go-build ]]; then
    clean_cmd "go build cache" "go clean -cache" ~/.cache/go-build
fi

# Go build cache di printing-press
clean_dir ~/.cache/printing-press "printing-press go-build cache"

# pip
if command -v pip3 &>/dev/null; then
    clean_cmd "pip cache" "pip3 cache purge -q 2>/dev/null || true" ~/.cache/pip
fi

# pnpm
if command -v pnpm &>/dev/null; then
    clean_cmd "pnpm store prune" "pnpm store prune --force -q 2>/dev/null || true" ~/.cache/pnpm
fi

# Directory rimosse direttamente
clean_dir ~/.cache/ort.pyke.io       "ONNX Runtime cache"
clean_dir ~/.cache/ms-playwright-go  "Playwright Go browser binaries"
clean_dir ~/.cache/ms-playwright     "Playwright browser binaries"
clean_dir ~/.cache/node-gyp          "node-gyp build cache"
clean_dir ~/.cache/pyright-python    "Pyright Python cache"
clean_dir ~/.cache/opencode          "OpenCode cache"
clean_dir ~/.cache/typescript        "TypeScript language server cache"
clean_dir ~/.cache/deno              "Deno cache"

# ════════════════════════════════════════════════════════════════════════════
section "/tmp — file temporanei (>1 giorno)"

# Escludi la sessione Claude attiva e i socket dbus in uso
TMP_FREED=0
while IFS= read -r item; do
    size=$(path_bytes "$item")
    human=$(human_size "$size")
    if $DRY_RUN; then
        echo -e "  ${YELLOW}[dry-run]${NC} $item  ${RED}$human${NC}"
    else
        echo -e "  ${GREEN}✓${NC} $item  ${RED}$human${NC}"
        rm -rf "$item" 2>/dev/null || { echo -e "  ${YELLOW}(skip, permesso negato)${NC} $item"; continue; }
        TMP_FREED=$(( TMP_FREED + size ))
    fi
done < <(find /tmp -maxdepth 1 -mtime +1 \
    ! -name "claude-*" \
    ! -name ".org.chromium*" \
    ! -name "dbus-*" \
    ! -name "*.sock" \
    2>/dev/null)

FREED_TOTAL=$(( FREED_TOTAL + TMP_FREED ))

# ════════════════════════════════════════════════════════════════════════════
if ! $NO_SUDO; then
    section "Sistema (richiede sudo)"

    if sudo -n true 2>/dev/null || { echo -e "  ${YELLOW}Inserisci la password sudo:${NC}"; sudo true 2>/dev/null; }; then
        # APT package cache
        if command -v apt-get &>/dev/null && [[ -d /var/cache/apt/archives ]]; then
            clean_cmd "apt-get clean" "sudo apt-get clean -q" /var/cache/apt/archives
        fi

        # Journal logs vecchi (tieni ultima settimana)
        if command -v journalctl &>/dev/null; then
            clean_cmd "journalctl vacuum (>7d)" "sudo journalctl --vacuum-time=7d -q 2>/dev/null || true"
        fi
    else
        echo -e "  ${YELLOW}sudo non disponibile — sezione sistema saltata${NC}"
    fi
else
    echo -e "  (saltata con --no-sudo)"
fi

# ════════════════════════════════════════════════════════════════════════════
echo ""
if $DRY_RUN; then
    echo -e "${BOLD}Modalità dry-run: nessuna modifica effettuata.${NC}"
    echo -e "Esegui senza ${YELLOW}--dry-run${NC} per applicare la pulizia."
else
    echo -e "${BOLD}Spazio liberato:${NC} ${RED}$(human_size $FREED_TOTAL)${NC}"
fi

echo ""
echo -e "${BOLD}Nota WSL2:${NC} per compattare il file ext4.vhdx su Windows (recupero reale su disco host):"
echo -e "  1. Chiudi WSL:  ${CYAN}wsl --shutdown${NC}"
echo -e "  2. Da PowerShell admin:"
echo -e "     ${CYAN}Get-ChildItem \"\$env:LOCALAPPDATA\\Packages\" -Recurse -Filter ext4.vhdx | Select FullName${NC}"
echo -e "     ${CYAN}Optimize-VHD -Path <path> -Mode Full${NC}"
