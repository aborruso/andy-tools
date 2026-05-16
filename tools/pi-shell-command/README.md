# Pi Shell Command

Pi extension that turns natural-language requests into shell commands.

It is meant for non-interactive use: Pi prints the command to run, without executing it.

## Prerequisites

Pi Coding Agent must be installed and configured before using this tool.

```bash
npm install -g @earendil-works/pi-coding-agent
```

Pi must also have access to a configured model/provider, for example via `/login` or an API key.

## Install

```bash
cd tools/pi-shell-command
make install
```

This installs the extension to Pi's default global extension directory:

```text
~/.pi/agent/extensions/shell-command.ts
```

## Usage after install

```bash
howcli "lista i file della cartella corrente"
```

Expected output:

```bash
ls
```

By default, `howcli` prints the generated command and copies it to the system clipboard when a clipboard command is available.

For commands that search, list, read, or count files inside a path, `howcli` asks Pi to prefer recursive commands by default, including subdirectories.

For recursive path searches and directory scans, generated commands hide noisy stderr output with `2>/dev/null` when appropriate. Use `--debug` to keep stderr visible.

Generated commands are saved in a local SQLite cache under `${XDG_CACHE_HOME:-~/.cache}/howcli/cache.sqlite`. The cache is managed by the `howcli-cache` Python CLI, installed with `uv` and using `rapidfuzz` for fuzzy search. Use `-c` or `--cache` to search previous suggestions without calling Pi.

To ask for confirmation and execute it:

```bash
howcli --run "lista i file della cartella corrente"
```

To keep stderr visible in generated commands:

```bash
howcli --debug "trova tutti i file csv sotto la cartella corrente"
```

To search the local cache without calling Pi:

```bash
howcli -c "trova csv"
howcli --cache
```

Expected interaction:

```bash
ls
Eseguire? [Y/n]
```

With `--run`, press `Enter`, `y`, `yes`, `s`, `si`, or `sì` to execute the command. Type `n` or `no` to skip it. Press `Ctrl+C` to abort.

Equivalent Pi command:

```bash
pi -p \
  --shell-command \
  --no-session \
  --no-tools \
  --no-context-files \
  --no-skills \
  --no-prompt-templates \
  "lista i file della cartella corrente"
```

Examples:

```bash
howcli "trova tutti i file csv sotto la cartella corrente"
howcli "scompatta archivio.zip in una cartella output"
howcli "conta le righe dei file python"
howcli --debug "cerca errore sotto la cartella corrente"
howcli -c "cerca csv"
howcli --run "lista i file della cartella corrente"
```

## Uninstall

```bash
cd tools/pi-shell-command
make uninstall
```

## Local test without installing

```bash
pi -p \
  --no-session \
  --no-tools \
  --no-context-files \
  --no-skills \
  --no-prompt-templates \
  --no-extensions \
  -e ./tools/pi-shell-command/shell-command.ts \
  --shell-command \
  "lista i file della cartella corrente"
```

## Notes

- `howcli` prints the generated command without executing it.
- `howcli` also copies the generated command to the system clipboard when `wl-copy`, `xclip`, `pbcopy`, or `clip.exe` is available.
- `howcli --run` asks before executing the generated command.
- `howcli --debug` asks Pi not to add `2>/dev/null` to generated commands.
- `howcli -c` / `howcli --cache` searches the local command cache using fuzzy matching and does not call Pi.
- Cache search shows up to 5 matches, prints the full top-ranked command as the final `COMMAND:` line, and copies that command to the clipboard when possible.
- `howcli-cache` is installed as a Python CLI with `uv tool install`.
- `make install` installs the Pi extension in `~/.pi/agent/extensions/` and the `howcli` command in `~/bin/`.
- Make sure `~/bin` is in your `PATH`.
- `--shell-command` activates the extension. Without it, the installed extension does nothing.
- `--no-tools` prevents Pi from executing shell commands or reading/writing files.
- `-p` / `--print` makes Pi run once and exit.
- `-e` / `--extension` loads this extension explicitly for local tests.
