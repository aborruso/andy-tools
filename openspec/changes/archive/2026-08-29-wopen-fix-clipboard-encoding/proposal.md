## Why

`wopen -c` corrompe ogni carattere non ASCII. `clip.exe` legge i byte da stdin nella codepage ANSI, quindi un testo UTF-8 arriva negli appunti trasformato: `è` diventa `├¿`, `più` diventa `pi├╣`. Il file su disco resta integro, si rompe solo il passaggio in clipboard, quindi il danno si vede dopo aver incollato. La capability `copy-to-clipboard` non dice nulla sulla codifica, e la sua unica garanzia ("il contenuto viene copiato") oggi è falsa per qualsiasi testo accentato.

## What Changes

- Il contenuto viene convertito in UTF-16LE con `iconv` prima di raggiungere `clip.exe`
- Nessun BOM: `clip.exe` riconosce l'UTF-16LE senza, e se lo riceve lo copia negli appunti come carattere U+FEFF in testa al testo
- Un eventuale BOM UTF-8 nel file sorgente viene rimosso prima della conversione, per la stessa ragione
- La conversione passa da un file temporaneo: se fallisce a metà file non si è già scritta mezza clipboard
- Se il file non è UTF-8 valido, avviso su stderr e fallback ai byte grezzi con exit code 0 (comportamento invariato rispetto a prima)
- Se `iconv` non è nel PATH, si usa il percorso precedente senza errore
- Aggiornamento del README del tool

## Capabilities

### New Capabilities

### Modified Capabilities

- `copy-to-clipboard`: aggiunta la garanzia sulla codifica del contenuto copiato

## Impact

- Script `tools/wopen/wopen` (ramo `-c`)
- `tools/wopen/README.md` (documentazione del comportamento)
- Dipendenza runtime opzionale: `iconv` (presente in ogni WSL con glibc; se assente il comando resta quello di prima)
