## Context

`wopen` è uno script Bash per WSL che apre file, directory e URL con le applicazioni Windows. Il flag `-s` già implementa una variante comportamentale (apre un terminale). La nuova funzionalità `-c` segue lo stesso pattern: un flag esclusivo che cambia il comportamento principale.

In WSL, `clip.exe` è il comando nativo Windows per scrivere sugli appunti di sistema: accetta dati da stdin. È già disponibile in ogni installazione WSL con interop abilitato.

## Goals / Non-Goals

**Goals:**
- Aggiungere `-c <file>` che legge il file e lo invia a `clip.exe`
- Supportare solo file locali WSL/Linux (stessa restrizione di `-s`)
- Errore chiaro se usato con directory, URL o percorsi Windows
- Errore chiaro se `clip.exe` non è disponibile

**Non-Goals:**
- Supporto per directory (il contenuto sarebbe ambiguo)
- Supporto per URL (non ha senso copiare il contenuto di una URL senza fetch)
- Supporto per percorsi Windows (complessità aggiuntiva senza beneficio pratico)
- Combinazione `-c` con `-s` (flag semanticamente incompatibili)

## Decisions

**D1: Usare `clip.exe` invece di `xclip`/`xsel`**
`clip.exe` è già presente in WSL senza installare nulla. `xclip` richiede un display X11 che in WSL puro non è disponibile. Scelta ovvia.

**D2: Flag breve `-c` e lungo `--copy`**
Coerente con lo stile del tool (`-s` per shell). Il lungo rende il codice leggibile negli script.

**D3: Solo file locali WSL**
Le restrizioni di `-s` (no URL, no Windows path) si applicano anche qui per semplicità e coerenza. I percorsi Windows non sono supportati perché richiederebbero una conversione inversa non necessaria.

**D4: Nessun output su stdout in caso di successo**
Comportamento silenzioso coerente con il resto del tool. Solo errori su stderr.

## Risks / Trade-offs

- [Risk] `clip.exe` potrebbe non essere disponibile su WSL con interop disabilitato → Mitigation: controllo esplicito con `command -v clip.exe` e messaggio di errore chiaro
- [Risk] File binari potrebbero corrompere la clipboard → Non mitigato: l'utente è responsabile di usare `-c` solo su file di testo; non è diverso da qualsiasi altro strumento di clipboard
