# Tool: stale-repos — trova repo git abbandonati e ingombranti

## Obiettivo
Listare cartelle git abbandonate (candidate allo spostamento) sul disco WSL ext4.

## Criterio
Un repo è candidato se TUTTE le condizioni valgono:
- nessun commit recente (`git log --all --since`)
- nessun file sorgente modificato di recente (mtime, escludendo build/deps)
- dimensione > soglia (`du -sx`)
- NON dirty (modifiche non committate → escluso per sicurezza)

## Parametri
- `-d/--days` (default 180)
- `-s/--size-mb` (default 100)
- `-r/--root` (default $HOME)

## Fasi
- [x] Script `tools/stale-repos/stale-repos.sh`
- [x] Discovery repo: `find -xdev` con prune dir pesanti, cerca `.git`
- [x] Gate in ordine: commit recente → mtime recente → dirty → size
- [x] Output ordinato per dimensione + totale recuperabile
- [x] README del tool
- [x] Riga nel README principale
- [x] Test su disco reale (solo lettura)

## Note
- `-xdev` esclude automaticamente /mnt e mount 9p (filesystem diversi)
- Prune: node_modules .venv venv target build dist .next .cache __pycache__ .git
- Solo lista, mai sposta

## Review
- Discovery: due liste di prune separate. Bug iniziale: `.git` nella lista di
  discovery → potato prima di essere stampato (0 repo). Risolto separando
  `PRUNE_BUILD` (discovery) da prune+`.git` (check mtime).
- Gate in ordine di costo: commit (veloce) → mtime con `-quit` (esce al 1° hit)
  → dirty (`status --porcelain`) → `du -sx` solo sui finalisti.
- `--all` su git log così conta i branch non-HEAD; repo senza commit gestiti.
- Test reale su `~`: 428 repo in ~36s → 23 candidati, 11.4 GB recuperabili.
- Solo elenco, nessuna azione distruttiva.
- Possibili estensioni future: flag `--json`, `--move DIR` opzionale.
