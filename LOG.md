# LOG

## 2026-08-19

- `tools/pi-shell-command` 0.3.2: fallback automatico del modello. Quando il primario fallisce (es. `Codex error: The usage limit has been reached` su gpt-5.5) howcli riprova con `HOWCLI_FALLBACK_MODELS` (default: deepseek-v4-flash e qwen3.5-plus via OpenRouter), avviso su stderr e stdout pulito; `HOWCLI_NO_FALLBACK=1` disattiva (lo imposta `eval/run-eval.sh` per mantenere onesti i risultati per-modello). Verificato dal vivo con la quota Codex esaurita: fallback → `rg -l "jiku" ~ --glob '*.sh' 2>/dev/null` exit 0, clipboard 40 char esatti senza CRLF; senza fallback → exit 1 pulito.

- `tools/pi-shell-command` 0.3.1: fix clipboard per CTRL+V. Il ramo `clip.exe` inviava un `\n` finale che diventa CRLF nella clipboard Windows (incollando, il comando si portava dietro un ritorno a capo); inoltre su questo WSL `wl-copy` e `xclip` falliscono entrambi (exit 1), quindi `clip.exe` era già il percorso effettivo ma arrivava per ultimo. Ora `copy_to_clipboard` prova prima `clip.exe` con `printf '%s'` (niente newline): verificato con run reali conteggiando i caratteri in memoria — `date` = 4 char (100,97,116,101), `ls` = 2 (108,115), zero CRLF. Nota: il "non funziona più" di oggi era anche il usage limit di `openai-codex/gpt-5.5` (howcli esce 1 senza copiare nulla); testato ok con `HOWCLI_MODEL=openrouter/deepseek/deepseek-v4-flash-0731`.
- `tools/pi-shell-command`: cache verificata end-to-end con il wrapper installato e un `XDG_CACHE_HOME` isolato: dopo `howcli "mostra il nome del kernel Linux"` la stessa query via `howcli --cache` restituisce `COMMAND: uname -s`. Il wrapper installato è identico al sorgente; nessuna modifica al tool.

## 2026-08-14

- `tools/projump`: ranking del filtro rifatto. Il match era greedy sui singoli caratteri (nessun backtracking) e senza bonus per sottostringa: cercando `tasca`, `~/git/idee/la-tasca` prendeva 12.8 (la `t` veniva consumata da `git`, la `a` da `la`) mentre `~/lavagna/tmp/analisi_cambiamenti_cusras` arrivava a 35.6 accumulando i +10 di inizio-parola su un path lungo. Ora `fuzzyScore()` è a strati: sottostringa nel basename (+bonus word-boundary e copertura del nome) → sottostringa nel path → sottosequenza come prima; la penalità per lunghezza passa da `0.01` a `0.15` per carattere e si applica solo agli ultimi due strati, così tra i match sul nome il tie-break resta l'attività recente. `tasca` → `la-tasca` 165 contro 30 del secondo.

## 2026-08-11

- `tools/projump`: la lista non sfora più l'altezza del terminale. Prima venivano stampate tutte le voci fino a `--limit`: su finestre piccole il terminale scrollava, l'intestazione spariva e si vedevano solo le ultime righe (anche il repaint via `\x1b[<n>F` risultava corrotto, perché le righe scrollate via non sono più raggiungibili). Ora `listSlots()`/`viewWindow()` calcolano a ogni render una finestra che sta in `rows - 1`, si parte sempre dalla prima voce, `↑`/`↓` scrollano seguendo la selezione e una riga `1-6 of 40` indica la posizione.

## 2026-08-09

- `tools/pi-shell-command` eval normalizzato (rerun sui 3 migliori, gpt-5.4 scartato): gpt-5.5 80% (16 PASS, di cui 1 normalizzato), deepseek-v4-flash 80% (16, di cui 1 norm), qwen3.5-plus 75% (15 esatti). L'unico DIFF residuo per tutti e 3 è il caso 17 (`du -sh ./*` vs `du -sh */`, stile). Completezza: tutti 3 coprono 20/20 casi (PASS+PASS~+SOFT-OK) senza ERROR né comandi sbagliati.
- `tools/pi-shell-command` README: nuova sezione "Using other models" — default invariato `openai-codex/gpt-5.5`, esempi `HOWCLI_MODEL=openrouter/deepseek/deepseek-v4-flash-0731` e `.../qwen/qwen3.5-plus-20260420`, export persistente in `~/.zshrc`.
- `tools/pi-shell-command` eval: confronto ora normalizzato (`norm()` in run-eval.sh): toglie apici, ignora `2>/dev/null`, collassa spazi, folda `./`, `cmd … < file` ≡ `cmd … file`, `sort … | uniq` ≡ `sort -u …`. I match normalizzati contano come PASS e sono marcati `PASS~` nel log (es. `wc -l < "file.csv"` ≡ `wc -l file.csv`). Caso 15 marcato `soft`: "conta quante volte" è ambiguo tra righe (`grep -c`) e occorrenze (`grep -o | wc -l`) — entrambe valide (emerso dall'eval: gpt-5.5/5.4 e dsv4f generavano la variante occorrenze).
- Fix `eval/run-eval.sh`: `pi` reale legge stdin e divorava il feed del `while read` (con lo stub bash non emergeva). Ora `jq` scrive un TSV su file e ogni chiamata gira con `</dev/null`. Gira correttamente col `pi` vero (20/20 casi).
- `tools/pi-shell-command` 0.3.0: nuovo `eval/` — golden set di 20 coppie query→comando (`cases.json`) e runner `run-eval.sh` che esegue lo stack reale di howcli (cache isolata, clipboard disattivata) e confronta l'output con l'atteso: `PASS` esatto, `SOFT-OK` per casi judge-dipendenti, `DIFF` con ratio difflib. Flag `--model`, `--filter`, `--out`, `--quiet`, `HOWCLI_BIN`. Exit 0 solo senza DIFF/ERROR. Aggiunto a `make check`.

- `tools/pi-shell-command` 0.3.0: nuovo `eval/` — golden set di 20 coppie query→comando (`cases.json`) e runner `run-eval.sh` che esegue lo stack reale di howcli (cache isolata, clipboard disattivata) e confronta l'output con l'atteso: `PASS` esatto, `SOFT-OK` per casi judge-dipendenti, `DIFF` con ratio difflib. Flag `--model`, `--filter`, `--out`, `--quiet`, `HOWCLI_BIN`. Exit 0 solo senza DIFF/ERROR. Aggiunto a `make check`.
- `tools/pi-shell-command` 0.3.0: `HOWCLI_MODEL` (override del modello passato a Pi, default `openai-codex/gpt-5.5`) e `HOWCLI_NO_CLIPBOARD=1` (disabilita la clipboard, usato dall'eval).
- `tools/pi-shell-command` 0.2.0: `howcli --run` ora stampa il comando prima della conferma (`Comando: …`) e richiede una doppia conferma esplicita (`[y/N]`, default no) per i comandi che matchano pattern distruttivi noti: `rm -rf` su path root o `*`/`.`, `mkfs*`, `dd … of=/dev/*`, `shred` su path root, fork bomb, scritture dirette su `/dev/sd*`. Check euristico (tripwire), non una boundary di sicurezza. Documentato in README e SPEC.

## 2026-07-28

- `tools/projump` 0.3.0: fuzzy search nel selettore — digitando si filtra su **tutti** i repo in cache (sottosequenza case-insensitive, bonus per caratteri consecutivi e inizio segmento), migliore match in cima accanto al cursore, tie-break per attività recente. Riga query nell'header, `Esc` svuota la query poi annulla, `Ctrl+C` annulla sempre; rimossi `j`/`k`/`q` (confliggono con la digitazione). Default `--limit` da 20 a 40.

## 2026-07-27

- `tools/projump`: cache su file in `${XDG_CACHE_HOME:-~/.cache}/projump/`, una per combinazione `--root` + `--all`. Si salva la lista completa ordinata, lo slice a `--limit` avviene in lettura. Scrittura atomica (tmp + rename), TTL 24 h, path spariti filtrati alla lettura.
- `tools/projump`: nuovo `--live`/`-l` (ignora la cache, riscansiona e riscrive) e `--refresh-only` (aggiorna la cache senza selettore). Se la cache ha più di 10 minuti, la lista si mostra subito da cache e un processo staccato (`detached` + `stdio: ignore` + `unref`) rigenera per il lancio successivo.
- `tools/projump`: le due chiamate `git` per repo ora sono concorrenti (`execFile` + pool di 16) invece che seriali. Erano 784 `spawnSync` su 392 repo, ~5 s dei 6,2 s totali.
- Misure su `~` (440 `.git`, 392 visibili): funzione shell `projump` da 6,2 s a 0,06 s con cache calda; scansione live da 6,2 s a 2,7 s.

## 2026-07-26

- `tools/projump`: sort key ora `max(birthtime cartella, reflog HEAD, committerdate refs)` invece della sola data di creazione. I progetti attivi (es. `la-tasca`, creato a aprile ma committato ieri) non sparivano più dal top-20.
- `tools/wopen`: il pre-check `powershell.exe` bloccava anche i casi che non lo usano (directory via `explorer.exe`, file via `cmd.exe`). Spostato in una funzione `require_powershell` richiamata solo dai rami URL e Windows path.
- `tools/wopen`: dedupe dei rami URL e Windows path, identici tranne l'azione; estratta `open_via_powershell <action> <target>`.

## 2026-07-13

- Added `tools/projump/`: Citty-based `projump-path` CLI that discovers git repositories under home with `fd` (fallback `find`), sorts them by project folder creation time, shows the newest 20 in an interactive selector, and prints the selected path for a shell `projump` cd wrapper. Default results now hide tool/cache repositories under hidden paths (for example `~/.gemini/...`) and dot-prefixed project folders; `--all` includes them.
- Added `wopen -c <file>` to copy local WSL file content to the Windows clipboard via `clip.exe`, with README and root index updates.

## 2026-06-15

- Added `tools/esearch/`: wrapper bash per Everything `es.exe` (WSL). Le parole plain diventano glob `*word*`; flag e token con `:` passano invariati; output riconvertito da cp850 a UTF-8. Opzioni `--es-path`, `--from-enc`/`--to-enc`, `--raw`, `--no-iconv` + varianti env. Le opzioni `es.exe` che prendono un valore (`-n`, `-path`, ...) sono passate verbatim con il loro argomento (no wrapping).
- `esearch`: bugfix — i valori dei flag `es.exe` (es. `3` in `-n 3`) venivano erroneamente trasformati in `*3*`. Introdotto statemachine con lista `VALUE_OPTS` di opzioni che consumano l'argomento successivo.

## 2026-06-10

- `gread`: fix sovrapposizione stelline/pallini — flag ora spaziati (`★ ●`), larghezza invariata.
- `gread`: archiviare rimuove subito il messaggio dalla vista — aggiunto `in:inbox` alla query e rimozione ottimistica per `a`/`x`. Rimossi flag `arch` e import `isInInbox` (vestigiali con `in:inbox`).

## 2026-05-24

- Added `tools/linux-cleanup/linux-cleanup.sh`: script per svuotare in sicurezza cache e /tmp su Linux/WSL2. Supporta `--dry-run` e `--no-sudo`. Usa comandi ufficiali (uv, go, pip, pnpm) dove disponibili. Include nota Optimize-VHD per compattare il VHDX su Windows.

## 2026-05-17

- Added `tools/bookmarklets/` section with a single README listing bookmarklets and readable sources in `src/`.
- Added bookmarklet **Get GitHub RSS Feed**: shows the Atom feed URL for any GitHub file page.
- Added bookmarklet **View in DeepWiki**: opens the current GitHub repo on deepwiki.com in a new tab.
- Fixed **Get GitHub RSS Feed**: close button was broken (`innerHTML +=` wiped DOM listeners); added Copy button with "Copied!" feedback.
- Fixed **View in DeepWiki**: regex now excludes `?` and `#` from repo name capture to avoid broken URLs on query-string GitHub pages.

## 2026-05-16

- Added `tools/pi-shell-command/SPEC.md` with `howcli` requirements, architecture, cache schema, ranking, and installation notes.
- Added `howcli --version` and `howcli-cache --version` at version `0.1.0`, and made `make install` refresh/reinstall the Python cache CLI to avoid stale local builds.
- Made `howcli` cache search show 5 fuzzy matches, print the full top command, and copy that command to the clipboard.
- Refactored `howcli` cache logic into a dedicated `howcli-cache` Python CLI managed with `uv` and `rapidfuzz`.
- Added a local SQLite cache to `howcli`, with `-c` / `--cache` to search previous generated commands without calling Pi.
- Updated `howcli` to prefer recursive path searches and hide noisy stderr with `2>/dev/null` when appropriate, with `--debug` to keep errors visible.

## 2026-05-14

- Added `md-gist`, a small Bash CLI to publish Markdown to GitHub Gist from a file or stdin, with optional copy, open, and raw URL output.
- Added the `md-gist` design note in `docs/plans/2026-05-14-md-gist-design.md`.
- Added `docs/future-ideas.md` with follow-up ideas for gist-based sharing, including rendered-host URLs inspired by `gisthost.github.io`.

## 2026-05-12

- Changed the `gread` query to `(is:starred OR is:unread) category:primary newer_than:7d`: surfaces both unread and starred primary messages from the last 7 days.
- Dropped `is:unread` from the `gread` query: now lists all primary Gmail messages from the last 7 days, read or unread.

## 2026-05-08

- Added `gread` to show unread primary Gmail messages for `gws` or `gwsb` with sender exclusions loaded from files.
- Made `wopen` with no arguments open the current directory, equivalent to `wopen .`.

## 2026-05-07

- Made `howcli` copy generated commands to the system clipboard by default when possible, preferring non-blocking Linux clipboard tools before `clip.exe`.
- Documented Pi Coding Agent as a prerequisite for `pi-shell-command`.
- Clarified the `pi-shell-command` system prompt for Linux CLI requests.
- Made `howcli` execution opt-in via `--run`.
- Made `howcli` ask before executing the generated shell command.
- Added the `howcli` command installed by the `pi-shell-command` Makefile.
- Added a Makefile installer for the `pi-shell-command` extension.
- Added the `pi-shell-command` extension to print shell commands from natural-language requests.

## 2026-05-05

- Made the `wopen` PATH setup instructions shell-agnostic.
- Made the `wopen` installer user-independent by defaulting to `$HOME/bin`.
- Updated the `wopen` install guide with the public GitHub clone URL.
- Clarified the `wopen` install guide with clone-and-install steps.
- Expanded the `wopen` README with purpose, WSL context, AI-agent usage, and installation steps.
- Added the main README with the current tool list.
- Translated repository documentation to English.
- Improved `wopen` help with examples, behavior, agent-friendly notes, and exit codes.
- Updated `wopen` to open WSL/Linux directories with File Explorer.
- Added Makefile installer to install `wopen` in the user's `bin` directory.
- Added the `wopen` tool to open files, directories, and URLs from WSL with the default Windows app.
- Added the initial PRD draft for the `andy-tools` repository.
