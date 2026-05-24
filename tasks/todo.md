# Cleanup Script Linux

## Analisi dell'ambiente

Disco al 97% (231G/251G). Spazio recuperabile stimato: ~3.5 GB sicuri senza toccare modelli AI.

### Esclusi (modelli AI, non cache rigenerabile)
- `~/.cache/whisper` — 2.0 GB — modelli Whisper (richiesta utente)
- `~/.cache/qmd` — 2.2 GB — modelli GGUF per `qmd` (embedding + reranking)

### Esclusi (sessione attiva)
- `/tmp/claude-1000` — sessione Claude Code corrente

## Piano dello script

### Sezione 1 — Cache utente (no sudo)

| Path | Dimensione | Comando |
|---|---|---|
| `~/.cache/uv` | 2.2 GB | `uv cache clean` |
| `~/.cache/go-build` | 674 MB | `go clean -cache` |
| `~/.cache/ort.pyke.io` | 269 MB | `rm -rf` |
| `~/.cache/printing-press` | 151 MB | `rm -rf` |
| `~/.cache/ms-playwright-go` | 128 MB | `rm -rf` |
| `~/.cache/ms-playwright` | 62 MB | `rm -rf` |
| `~/.cache/node-gyp` | 56 MB | `rm -rf` |
| `~/.cache/pyright-python` | 32 MB | `rm -rf` |
| `~/.cache/opencode` | 30 MB | `rm -rf` |
| `~/.cache/typescript` | 22 MB | `rm -rf` |
| `~/.cache/pip` | 1.8 MB | `pip cache purge` |
| `~/.cache/pnpm` | 1.1 MB | `pnpm store prune` |
| `~/.cache/deno` | 9.5 MB | `rm -rf` |

### Sezione 2 — /tmp (file vecchi >1 giorno, no claude-1000)

File e dir in /tmp più vecchi di 1 giorno (escluso claude-1000).
Stima: ~700 MB.

### Sezione 3 — Sistema (richiede sudo)

- `apt-get clean` → ~417 MB
- `journalctl --vacuum-time=7d` → log journal compressi

## Flag dello script

- `--dry-run` — mostra cosa verrebbe rimosso senza agire
- `--no-sudo` — salta la sezione sistema (sezione 3)

## Nota WSL2

Liberare spazio dentro WSL **non** compatta il file `ext4.vhdx` su Windows.
Per recuperare spazio reale sul disco host: `Optimize-VHD` da PowerShell admin con WSL spento.

## Domande aperte

- `~/.cache/ort.pyke.io`: è ONNX Runtime, sicuro? Sì, si rigenera.
- `~/.cache/printing-press`: tool locale, sicuro? Controllare se ha dati non rigenerabili.

---

## TODO

- [x] Chiedere conferma utente su questo piano
- [x] Scrivere lo script `tools/linux-cleanup/linux-cleanup.sh`
- [x] Testare in dry-run
- [x] Aggiornare LOG.md
