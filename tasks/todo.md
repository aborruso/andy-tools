# projump — ranking del filtro fuzzy

## Verifica — pi-shell-command cache

### Fase 1 — riproduzione

- [x] Generare un comando con cache isolata → verify: `howcli` reale stampa `uname -s` e scrive la riga
- [x] Cercare lo stesso comando con `howcli -c` → verify: restituisce `COMMAND: uname -s`

### Fase 2 — analisi

- [x] Confrontare wrapper installato e sorgente → verify: `/home/aborruso/bin/howcli` è identico al sorgente

### Fase 3 — clipboard CTRL+V

- [x] Contare i caratteri in memoria dopo un run reale → verify: `date` = 4 caratteri (100,97,116,101), `ls` = 2 (108,115), nessun CRLF finale
- [x] Correggere il ramo `clip.exe` (niente `\n`, priorità su wl-copy/xclip) → verify: reinstall 0.3.1, `bash -n` OK, wrapper in sync

### Fase 4 — fallback automatico modello

- [x] Riprovare con modelli di fallback quando il primario fallisce (usage limit) → verify: run reale con default a quota esaurita stampa avviso e genera via OpenRouter (`rg -l "jiku" …`, exit 0)
- [x] `HOWCLI_NO_FALLBACK=1` disattiva il retry senza avvisi fuorvianti → verify: fallimento pulito exit 1; eval runner lo imposta
- [x] Clipboard pulita anche via fallback → verify: `date +%F` = 8 char (100,97,116,101,32,43,37,70), zero CRLF

### Review

`howcli` salva correttamente il comando dopo una risposta riuscita. Non serve una modifica al tool.

## Problema

Con query `tasca`, `~/git/idee/la-tasca` finisce in fondo: il matching è greedy (nessun backtracking) e non esiste bonus per sottostringa esatta; i +10 di inizio-parola sparsi su path lunghi vincono.

## Fase 1 — scoring

- [x] `fuzzyScore`: se la query è sottostringa del **basename**, punteggio alto (+ extra se su word boundary, + copertura del nome) → verify: `la-tasca` primo per `tasca` (165 vs 30)
- [x] fallback: sottostringa nel path completo, poi sequenza fuzzy attuale (`sequenceScore`) → verify: query senza substring continuano a matchare
- [x] penalità lunghezza da `0.01` a `0.15` per carattere, solo sui rami di fallback → verify: tie-break per attività preservato tra i match sul nome

## Fase 2 — verifica

- [x] `tmp/score-check.mjs`: confronto punteggi sui repo reali dalla cache → verify: `tasca`, `ars`, `iride`, `pnrr`, `andy` ordinati come atteso
- [x] `node src/index.js --help` gira

## Fase 3 — doc

- [x] README projump: sezione "Fuzzy search" con i tre strati di ranking
- [x] LOG.md

## Review

`fuzzyScore()` ora è a strati invece che un solo passaggio greedy: sottostringa nel basename (60 + 20 se word boundary + 60 + 40×copertura) → sottostringa nel path (60/80) → `sequenceScore()` invariato, penalizzato per lunghezza. La logica di ordinamento in `applyFilter()` non è stata toccata.

Non verificato a mano nel selettore interattivo (richiede TTY): il controllo è stato fatto sui punteggi con i path reali in cache.

## Domande aperte

- nessuna
