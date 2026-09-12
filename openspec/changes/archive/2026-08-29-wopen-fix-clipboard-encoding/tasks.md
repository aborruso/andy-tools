## 1. Script wopen

- [x] 1.1 Convertire il contenuto in UTF-16LE con `iconv` prima di `clip.exe`, scrivendo su file temporaneo
- [x] 1.2 Rimuovere un eventuale BOM UTF-8 dal sorgente prima della conversione
- [x] 1.3 Fallback ai byte grezzi con avviso su stderr se la conversione fallisce, exit code 0
- [x] 1.4 Saltare la conversione senza errore se `iconv` non è disponibile

## 2. Documentazione

- [x] 2.1 Aggiornare `tools/wopen/README.md` con il comportamento sulla codifica e il fallback

## 3. Verifica

- [x] 3.1 Testo italiano accentato → code point corretti negli appunti (`perché così è più` → 233, 236, 232, 249)
- [x] 3.2 File con BOM UTF-8 → nessun U+FEFF negli appunti
- [x] 3.3 File latin-1 → avviso su stderr, exit code 0
- [x] 3.4 File senza newline finale → nessuna newline aggiunta (`ciao è` → 99,105,97,111,32,232)
- [x] 3.5 Giapponese, emoji con coppia surrogata, stringhe ASCII brevi, file vuoto → corretti
