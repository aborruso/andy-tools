## Why

Quando si lavora nel terminale WSL, è spesso utile copiare il contenuto di un file negli appunti di Windows per incollarlo in un'altra applicazione. Oggi non esiste un modo diretto in `wopen` per farlo.

## What Changes

- Aggiunta del flag `-c` / `--copy` al comando `wopen`
- Con `-c <file>`, il contenuto del file viene inviato agli appunti di Windows tramite `clip.exe`
- Il flag funziona solo con file locali (no directory, no URL, no percorsi Windows)
- Aggiornamento di `usage()` e `--help`
- Aggiornamento del README

## Capabilities

### New Capabilities

- `copy-to-clipboard`: Copia il contenuto di un file WSL/Linux negli appunti di Windows

### Modified Capabilities

## Impact

- Script `tools/wopen/wopen` (flag e logica nuova)
- `tools/wopen/README.md` (documentazione)
- Dipendenza runtime: `clip.exe` (già disponibile in WSL con Windows interop abilitato)
