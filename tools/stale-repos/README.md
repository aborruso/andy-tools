# stale-repos

Trova le cartelle di **repository git abbandonati e ingombranti**, candidate allo spostamento o all'archiviazione. Lo script **solo elenca**: non sposta e non cancella nulla.

Pensato per il disco Linux di WSL2: resta sempre sul filesystem della cartella di partenza (`find -xdev`), quindi `/mnt/*` e i mount Windows (9p/drvfs) vengono ignorati automaticamente.

## Criterio di "abbandono"

Una cartella è candidata se **tutte** queste condizioni valgono:

| Condizione | Come viene misurata |
| --- | --- |
| Nessun commit recente | `git log --all --since="N days ago"` vuoto (conta anche i branch non-HEAD) |
| Nessun file sorgente modificato di recente | `find -mtime -N` vuoto, escludendo `node_modules`, `.venv`, `target`, `build`, `dist`, `.next`, `.cache`, `__pycache__`, `.git` |
| Dimensione sopra soglia | `du -sx` della cartella (include tutto: è lo spazio che recuperi spostandola) |
| **Non** ha modifiche non committate | i repo "dirty" (`git status --porcelain` non vuoto) sono **esclusi per sicurezza** |

Il doppio controllo commit + mtime evita sia i falsi negativi (un repo morto i cui `node_modules` sono stati toccati da un `npm install` recente) sia i falsi positivi (un repo che editi spesso ma non committi mai).

## Uso

```bash
./stale-repos.sh [-d giorni] [-s size_mb] [-r root]
```

| Opzione | Default | Descrizione |
| --- | --- | --- |
| `-d`, `--days N` | `180` (~6 mesi) | Soglia di inattività in giorni |
| `-s`, `--size-mb N` | `100` | Dimensione minima della cartella in MB |
| `-r`, `--root PATH` | `$HOME` | Cartella da cui partire la scansione |
| `-h`, `--help` | | Mostra l'aiuto |

## Esempi

```bash
# Default: repo in ~ inattivi da oltre 6 mesi e più grandi di 100 MB
./stale-repos.sh

# Più aggressivo: 3 mesi, sopra 50 MB, solo dentro ~/git
./stale-repos.sh -d 90 -s 50 -r ~/git
```

## Output

Tabella ordinata per dimensione decrescente con dimensione, data dell'ultimo commit e percorso, seguita dal totale dello spazio recuperabile. I messaggi di avanzamento vanno su `stderr`, l'elenco su `stdout` (così è facile filtrarlo o redirigerlo).

## Note

- Per recuperare davvero lo spazio sul disco host di Windows dopo aver spostato/eliminato cartelle, serve compattare il file `ext4.vhdx` da Windows — vedi le note finali di [`linux-cleanup`](../linux-cleanup/linux-cleanup.sh).
- Richiede `git`, `find`, `du`, `bc`.
