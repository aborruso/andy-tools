## ADDED Requirements

### Requirement: Copia contenuto file negli appunti di Windows
Il sistema SHALL copiare il contenuto di un file WSL/Linux negli appunti di Windows quando invocato con il flag `-c` o `--copy`.

#### Scenario: Copia file di testo esistente
- **WHEN** l'utente esegue `wopen -c <file>` con un file di testo esistente
- **THEN** il contenuto del file viene copiato negli appunti di Windows tramite `clip.exe` e il comando termina con exit code 0

#### Scenario: Flag lungo --copy equivalente a -c
- **WHEN** l'utente esegue `wopen --copy <file>`
- **THEN** il comportamento è identico a `wopen -c <file>`

### Requirement: Restrizione a soli file locali WSL
Il sistema SHALL rifiutare l'uso di `-c` con directory, URL o percorsi Windows.

#### Scenario: Tentativo con una directory
- **WHEN** l'utente esegue `wopen -c <directory>`
- **THEN** il sistema stampa un messaggio di errore su stderr e termina con exit code 2

#### Scenario: Tentativo con un URL
- **WHEN** l'utente esegue `wopen -c https://example.com`
- **THEN** il sistema stampa un messaggio di errore su stderr e termina con exit code 2

#### Scenario: Tentativo con un percorso Windows
- **WHEN** l'utente esegue `wopen -c 'C:\file.txt'`
- **THEN** il sistema stampa un messaggio di errore su stderr e termina con exit code 2

### Requirement: File non trovato
Il sistema SHALL restituire un errore chiaro se il file non esiste.

#### Scenario: File inesistente
- **WHEN** l'utente esegue `wopen -c /percorso/inesistente.txt`
- **THEN** il sistema stampa un messaggio di errore su stderr e termina con exit code 1

### Requirement: clip.exe non disponibile
Il sistema SHALL restituire un errore chiaro se `clip.exe` non è disponibile.

#### Scenario: clip.exe assente
- **WHEN** `clip.exe` non è nel PATH e l'utente esegue `wopen -c <file>`
- **THEN** il sistema stampa un messaggio di errore su stderr e termina con exit code 1

### Requirement: Incompatibilità con altri flag
Il sistema SHALL rifiutare la combinazione di `-c` con `-s`.

#### Scenario: Flag -c e -s usati insieme
- **WHEN** l'utente esegue `wopen -c -s <file>` o `wopen -s -c <file>`
- **THEN** il sistema stampa un messaggio di errore su stderr e termina con exit code 2
