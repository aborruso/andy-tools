# copy-to-clipboard

## Purpose

Copiare il contenuto di un file WSL/Linux negli appunti di Windows con `wopen -c`.
## Requirements
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

### Requirement: Codifica del contenuto copiato
Il sistema SHALL consegnare il contenuto a `clip.exe` in UTF-16LE senza BOM, in modo che i caratteri non ASCII arrivino integri negli appunti di Windows.

#### Scenario: File UTF-8 con caratteri accentati
- **WHEN** l'utente esegue `wopen -c <file>` su un file UTF-8 contenente `perché così è più`
- **THEN** gli appunti di Windows contengono lo stesso testo con i caratteri accentati integri

#### Scenario: File UTF-8 con BOM
- **WHEN** l'utente esegue `wopen -c <file>` su un file che inizia con un BOM UTF-8
- **THEN** il BOM non compare negli appunti come carattere U+FEFF

#### Scenario: File senza newline finale
- **WHEN** l'utente esegue `wopen -c <file>` su un file che non termina con newline
- **THEN** il contenuto negli appunti non ha una newline aggiunta

### Requirement: Fallback su contenuto non UTF-8
Il sistema SHALL copiare i byte grezzi, avvisando su stderr, quando il contenuto non è UTF-8 valido.

#### Scenario: File in codifica latin-1
- **WHEN** l'utente esegue `wopen -c <file>` su un file non UTF-8 valido
- **THEN** il sistema stampa un avviso su stderr, copia i byte grezzi come prima e termina con exit code 0

#### Scenario: iconv non disponibile
- **WHEN** `iconv` non è nel PATH e l'utente esegue `wopen -c <file>`
- **THEN** il contenuto viene copiato come byte grezzi e il comando termina con exit code 0

