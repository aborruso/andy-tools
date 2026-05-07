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

To ask for confirmation and execute it:

```bash
howcli --run "lista i file della cartella corrente"
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
- `make install` installs the Pi extension in `~/.pi/agent/extensions/` and the `howcli` command in `~/bin/`.
- Make sure `~/bin` is in your `PATH`.
- `--shell-command` activates the extension. Without it, the installed extension does nothing.
- `--no-tools` prevents Pi from executing shell commands or reading/writing files.
- `-p` / `--print` makes Pi run once and exit.
- `-e` / `--extension` loads this extension explicitly for local tests.
