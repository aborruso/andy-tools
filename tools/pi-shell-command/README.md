# Pi Shell Command

Pi extension that turns natural-language requests into shell commands.

It is meant for non-interactive use: Pi prints the command to run, without executing it.

For requirements, architecture, and cache schema details, see [SPEC.md](SPEC.md).

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

## Using other models

`howcli` defaults to `openai-codex/gpt-5.5` (served through your logged-in ChatGPT session). To use a different model, set `HOWCLI_MODEL` — any model id Pi accepts works:

```bash
HOWCLI_MODEL=openrouter/deepseek/deepseek-v4-flash-0731 howcli "trova i file csv"
HOWCLI_MODEL=openrouter/qwen/qwen3.5-plus-20260420 howcli "conta le righe dei file python"
```

Several models behave equivalently on this task (see [Evaluating](#evaluating)); the OpenRouter ones are faster, pay-per-use, and do not depend on the ChatGPT session. To make one the default for the current shell:

```bash
export HOWCLI_MODEL=openrouter/deepseek/deepseek-v4-flash-0731
```

(add the same line to `~/.zshrc` for a persistent default).

To search the local cache without calling Pi:

```bash
howcli -c "trova csv"
howcli --cache
```

Expected interaction:

```bash
ls
Comando: ls
Eseguire? [Y/n]
```

With `--run`, `howcli` shows the command before asking. Press `Enter`, `y`, `yes`, `s`, `si`, or `sì` to execute the command. Type `n` or `no` to skip it. Press `Ctrl+C` to abort.

For commands matching known destructive patterns (`rm -rf` on root paths or `*`/`.`, `mkfs*`, `dd … of=/dev/*`, `shred` on root paths, fork bombs, direct writes to `/dev/sd*`), `howcli` asks a second, explicit confirmation with default `no` before the standard prompt:

```bash
rm -rf /tmp/ciao
Comando: rm -rf /tmp/ciao
Comando potenzialmente distruttivo: confermi davvero? [y/N]
```

Only `y`, `yes`, `s`, `si`, or `sì` proceed; anything else aborts without executing. The check is a heuristic tripwire, not a security boundary.

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

## Evaluating

A golden set of 20 query→command pairs lives in `eval/cases.json`, with `eval/run-eval.sh` to run it:

```bash
cd tools/pi-shell-command
./eval/run-eval.sh                                          # modello di default
./eval/run-eval.sh --model openrouter/deepseek/deepseek-v4-flash-0731
./eval/run-eval.sh --filter csv                             # solo i casi che contengono "csv"
./eval/run-eval.sh --out eval/result.md                     # report markdown
```

The runner calls the real `howcli` stack (isolated cache, clipboard disabled), compares each generated command with the expected one, and reports exact matches (`PASS`), style-normalized matches (`PASS~`), near-matches via difflib ratio, and diffs. The comparison is style-insensitive: quotes are stripped, `2>/dev/null`, `./` prefixes, and `cmd … < file` vs `cmd … file` are ignored, and `sort … | uniq` counts as `sort -u …`. `soft` cases are judge-dependent (e.g. destructive requests where the prompt bias prefers a dry-run variant, or ambiguous wording). Exit code is `0` only when there are no `DIFF`/`ERROR` cases.

## Notes

- `howcli` prints the generated command without executing it.
- `HOWCLI_MODEL` overrides the model passed to Pi (default `openai-codex/gpt-5.5`). Useful to compare models via `eval/run-eval.sh`.
- `HOWCLI_NO_CLIPBOARD=1` disables copying to the system clipboard. The eval runner sets it.
- `howcli` also copies the generated command to the system clipboard when `wl-copy`, `xclip`, `pbcopy`, or `clip.exe` is available.
- `howcli --run` shows the command, asks for confirmation, and requires a second explicit confirmation for commands matching known destructive patterns.
- `howcli --debug` asks Pi not to add `2>/dev/null` to generated commands.
- `howcli -c` / `howcli --cache` searches the local command cache using fuzzy matching and does not call Pi.
- Cache search shows up to 5 matches, prints the full top-ranked command as the final `COMMAND:` line, and copies that command to the clipboard when possible.
- `howcli --version` and `howcli-cache --version` print the installed versions.
- `howcli-cache` is installed as a Python CLI with `uv tool install --refresh --reinstall`.
- `make install` installs the Pi extension in `~/.pi/agent/extensions/` and the `howcli` command in `~/bin/`.
- Make sure `~/bin` is in your `PATH`.
- `--shell-command` activates the extension. Without it, the installed extension does nothing.
- `--no-tools` prevents Pi from executing shell commands or reading/writing files.
- `-p` / `--print` makes Pi run once and exit.
- `-e` / `--extension` loads this extension explicitly for local tests.
