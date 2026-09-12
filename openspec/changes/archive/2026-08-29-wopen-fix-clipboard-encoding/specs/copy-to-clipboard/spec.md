## ADDED Requirements

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
