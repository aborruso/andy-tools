#!/usr/bin/env bash
set -euo pipefail

VERSION="0.1.0"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CASES="$DIR/cases.json"

usage() {
  cat >&2 <<'EOF'
Usage:
  run-eval.sh [--model <id>] [--filter <substring>] [--out <file>] [--quiet]

Esegue il golden set di howcli (eval/cases.json) e confronta ogni comando
generato con quello atteso.

  --model <id>      modello Pi da usare (HOWCLI_MODEL). Default: quello di howcli
  --filter <sub>    esegue solo i casi con "sub" in id o query
  --out <file>      scrive un report markdown
  --quiet           mostra solo fallimenti e riepilogo
  -h, --help        questo aiuto

Variabili:
  HOWCLI_BIN        binario howcli da testare (default: howcli in PATH)

Exit 0 se nessun DIFF/ERROR, 1 altrimenti.
EOF
}

model=""
filter=""
out_file=""
quiet=false

while [ "$#" -gt 0 ]; do
  case "$1" in
    --model) model="${2:-}"; shift 2 ;;
    --filter) filter="${2:-}"; shift 2 ;;
    --out) out_file="${2:-}"; shift 2 ;;
    --quiet) quiet=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Opzione sconosciuta: $1" >&2; usage; exit 2 ;;
  esac
done

cli="${HOWCLI_BIN:-howcli}"
if [[ "$cli" == */* ]]; then
  if [ ! -x "$cli" ]; then
    echo "howcli non eseguibile: $cli (chmod +x o usa una copia installata)" >&2
    exit 1
  fi
elif ! command -v "$cli" >/dev/null 2>&1; then
  echo "howcli non trovato in PATH (installa con: make -C tools/pi-shell-command install)" >&2
  exit 1
fi
if ! command -v jq >/dev/null 2>&1; then
  echo "jq richiesto" >&2
  exit 1
fi

# Isolamento: cache dedicata, nessuna scrittura in clipboard durante l'eval.
EVAL_TMP="$(mktemp -d)"
trap 'rm -rf "$EVAL_TMP"' EXIT
export XDG_CACHE_HOME="$EVAL_TMP/cache"
export HOWCLI_NO_CLIPBOARD=1
export HOWCLI_NO_FALLBACK=1
if [ -n "$model" ]; then
  export HOWCLI_MODEL="$model"
  model_label="$model"
else
  model_label="${HOWCLI_MODEL:-default}"
fi

printf 'Eval howcli %s — %s — modello: %s — CLI: %s\n' "$VERSION" "$(date +%Y-%m-%d)" "$model_label" "$cli"

ratio() { # $1 atteso, $2 ottenuto
  python3 - "$1" "$2" <<'PY'
import difflib, sys
print(f"{difflib.SequenceMatcher(None, sys.argv[1], sys.argv[2]).ratio():.2f}", end="")
PY
}

# Normalizzazione per il confronto: stile-insensitive.
# Regole: toglie apici singoli/doppi, ignora 2>/dev/null, collassa spazi,
# toglie i prefissi ./, tratta `sort … | uniq` come `sort -u …` e
# `cmd … < file` come `cmd … file`.
norm() {
  printf '%s' "$1" | sed -E \
    -e "s/['\"]//g" \
    -e 's/2>\/dev\/null//g' \
    -e 's/sort ([^|]*)\| uniq/sort -u \1/' \
    -e 's/ < / /g' \
    -e 's/ \.\// /g' -e 's/^\.\///' \
    | tr -s '[:space:]' ' ' \
    | sed -e 's/^ //' -e 's/ $//'
}

total=0; exact=0; norm_count=0; soft_ok=0; diff=0; error=0

CASES_TSV="$EVAL_TMP/cases.tsv"
jq -r '.[] | [.id, .query, .command, (.soft // false), (.note // "")] | @tsv' "$CASES" > "$CASES_TSV"

if [ -n "$out_file" ]; then
  : > "$out_file"
  printf '# Eval howcli — %s — modello: %s\n\n| # | caso | esito | ratio |\n|---|---|---|---|\n' \
    "$(date +%Y-%m-%d)" "$model_label" >> "$out_file"
fi

while IFS=$'\t' read -r id query expect soft note; do
  if [ -n "$filter" ] && [[ "$id $query" != *"$filter"* ]]; then
    continue
  fi
  total=$((total + 1))

  errf="$EVAL_TMP/err-$id"
  # stdin da /dev/null: pi legge stdin e divorerebbe il feed del while
  got="$($cli "$query" </dev/null 2>"$errf" || true)"
  errs="$(cat "$errf" 2>/dev/null || true)"

  if [ -n "$expect" ] && [ "$got" = "$expect" ]; then
    verdict="PASS"; exact=$((exact + 1)); r="1.00"
  elif [ -n "$expect" ] && [ -n "$got" ] && [ "$(norm "$got")" = "$(norm "$expect")" ]; then
    verdict="PASS~"; norm_count=$((norm_count + 1)); r="1.00"
  elif [ "$soft" = "true" ] && [ -n "$got" ]; then
    verdict="SOFT-OK"; soft_ok=$((soft_ok + 1)); r="$(ratio "$expect" "$got")"
  elif [ -z "$got" ] && [ -n "$errs" ]; then
    verdict="ERROR"; error=$((error + 1)); r="-"
  else
    verdict="DIFF"; diff=$((diff + 1)); r="$(ratio "$expect" "$got")"
  fi

  if [ "$verdict" != "PASS" ] || [ "$quiet" != true ]; then
    printf '[%s] %s %s\n' "$verdict" "$id" "$query"
    if [ "$verdict" != "PASS" ]; then
      printf '       atteso:   %s\n' "$expect"
      printf '       ottenuto: %s\n' "$got"
      [ -n "$note" ] && printf '       nota:     %s\n' "$note"
      [ "$verdict" = "ERROR" ] && printf '       stderr:   %s\n' "$errs"
    fi
  fi

  if [ -n "$out_file" ]; then
    printf '| %s | %s | %s | %s |\n' "$id" "$query" "$verdict" "$r" >> "$out_file"
    if [ "$verdict" != "PASS" ]; then
      printf '  - atteso: `%s`\n  - ottenuto: `%s`\n' "$expect" "$got" >> "$out_file"
    fi
  fi
done < "$CASES_TSV"

if [ "$total" -eq 0 ]; then
  echo "Nessun caso selezionato (--filter)." >&2
  exit 1
fi

pct="$(awk -v e="$((exact + norm_count))" -v t="$total" 'BEGIN{ printf "%.0f", e*100/t }')"
printf 'Riepilogo: %d casi — PASS %d (esatti %d, normalizzati %d), SOFT-OK %d, DIFF %d, ERROR %d (esattezza %s%%)\n' \
  "$total" "$((exact + norm_count))" "$exact" "$norm_count" "$soft_ok" "$diff" "$error" "$pct"

if [ "$diff" -eq 0 ] && [ "$error" -eq 0 ]; then
  exit 0
fi
exit 1