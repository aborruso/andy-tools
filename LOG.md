# LOG

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
