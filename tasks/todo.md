# projump — lista a 40 + fuzzy search

## Contesto

Il selettore attuale mostra i primi 20 repo per attività; navigazione con ↑/k ↓/j, uscita con q/Esc. Richiesta: default a 40 item e filtro fuzzy digitando, con il match migliore adiacente al cursore (in cima).

## Fase 1 — default a 40

- [x] `limit` default da `"20"` a `"40"` in `src/index.js`
- [x] Aggiornare la descrizione dell'opzione e il README del tool

## Fase 2 — fuzzy search nel selettore

- [x] Scorer fuzzy senza dipendenze (~30 righe): match a sottosequenza sul path "pretty", bonus per caratteri consecutivi e per inizio segmento/parola
- [x] Digitando si filtra la lista; risultati ordinati per score (tie-break: attività recente); il migliore in cima, cursore che riparte da 0 → l'elemento più "fuzzy" è sempre adiacente al cursore
- [x] Riga query visibile nell'header (es. `> quer_`)
- [x] Tasti: caratteri stampabili → query · Backspace cancella · ↑/↓ navigano · Enter seleziona · Esc svuota la query se piena, altrimenti annulla · Ctrl+C annulla sempre
- [x] Rimuovere `j`/`k` (navigazione) e `q` (uscita): confliggono con la digitazione
- [x] A query vuota: comportamento identico a oggi (lista per attività)

## Fase 3 — documentazione (prima del commit)

- [x] `tools/projump/README.md`: nuovi tasti, default 40, sezione fuzzy
- [x] README principale: riga projump se serve
- [x] `LOG.md`: voce datata

## Decisioni prese

1. Fuzzy su **tutta** la lista in cache, risultati mostrati max `limit` (confermato dall'utente)
2. Rimossi `j`/`k`/`q` (confermato dall'utente); restano ↑/↓, Enter, Esc, Ctrl+C
3. Versione 0.2.0 → 0.3.0

## Review

- Scorer fuzzy senza dipendenze: sottosequenza case-insensitive greedy con bonus (consecutivo +5, inizio segmento/parola +10, altrimenti +1) e penalità 0,01/carattere sulla lunghezza del path per preferire i path corti a parità di score.
- Test su pty: "andytools"+Enter seleziona `~/git/idee/andy-tools` (match a sottosequenza attraverso il trattino); query senza match mostra "no match" e ignora Enter; primo Esc svuota la query, secondo Esc esce con 130; ↓↓↑+Enter a query vuota seleziona il secondo repo per attività.
- Nota readline: un Esc solitario viene emesso da Node dopo ~500 ms (timeout interno per distinguere le sequenze escape) e con `meta: true`; l'handler controlla solo `key.name === "escape"`, quindi funziona. Due Esc a meno di 500 ms l'uno dall'altro vengono fusi in un solo evento: in quel caso serve un terzo Esc per uscire — limite noto e accettato.
- `node --check` pulito; nessuna nuova dipendenza.
