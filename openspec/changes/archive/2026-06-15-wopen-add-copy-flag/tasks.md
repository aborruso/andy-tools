## 1. Script wopen

- [x] 1.1 Aggiungere parsing del flag `-c` / `--copy` (esclusivo con `-s`)
- [x] 1.2 Validare che l'argomento non sia un URL né un percorso Windows né una directory, con messaggi di errore appropriati
- [x] 1.3 Verificare che il file esista (exit code 1 se mancante)
- [x] 1.4 Verificare che `clip.exe` sia disponibile (exit code 1 se assente)
- [x] 1.5 Leggere il file e inviarne il contenuto a `clip.exe` via stdin
- [x] 1.6 Aggiornare `usage()` con il nuovo flag e gli esempi

## 2. Documentazione

- [x] 2.1 Aggiornare `tools/wopen/README.md`: aggiungere `-c` alla sezione Usage, Behavior e Examples
