# howcli specification

## Purpose

`howcli` turns a natural-language request into a Linux shell command.

It is optimized for fast interactive use: print one command, copy it to the clipboard when possible, and avoid executing it unless explicitly requested.

## Components

```text
howcli              # Bash wrapper installed in ~/bin
shell-command.ts    # Pi extension installed in ~/.pi/agent/extensions
howcli-cache        # Python CLI installed with uv
cache.sqlite        # Local SQLite cache
```

## Requirements

### Command generation

- Accept a natural-language request as positional text.
- Call Pi in one-shot print mode.
- Activate the `shell-command` Pi extension.
- Disable tools, context files, skills, and prompt templates for predictable non-interactive output.
- Print only the generated command.
- Copy the generated command to the clipboard when a supported clipboard command is available, without a trailing newline: on WSL `clip.exe` is preferred (CTRL+V pastes from the Windows clipboard) and a trailing newline would become CRLF in the pasted command. `wl-copy`, `xclip`, and `pbcopy` remain fallbacks.
- `HOWCLI_MODEL` overrides the model passed to Pi (`--model`), default `openai-codex/gpt-5.5`.
- When the primary model fails (for example the ChatGPT usage limit is reached), retry automatically with the models in `HOWCLI_FALLBACK_MODELS` (space-separated; default `openrouter/deepseek/deepseek-v4-flash-0731 openrouter/qwen/qwen3.5-plus-20260420`), printing a notice on stderr. `HOWCLI_NO_FALLBACK=1` disables the retry; the eval runner sets it to keep per-model results honest.
- `HOWCLI_NO_CLIPBOARD=1` disables clipboard copy.

### Safety and execution

- Do not execute generated commands by default.
- With `--run`, print the generated command before prompting, ask for confirmation, and execute only after an affirmative answer.
- For commands matching known destructive patterns (`rm -rf` on root paths or `*`/`.`, `mkfs*`, `dd … of=/dev/*`, `shred` on root paths, fork bombs, direct writes to `/dev/sd*`), `--run` requires a second explicit confirmation with default `no`: only `y`, `yes`, `s`, `si`, or `sì` proceed. Anything else aborts without executing. The pattern check is a heuristic tripwire, not a security boundary.
- Use a safe prompt bias: prefer dry-run or non-destructive variants for destructive requests when available.

### Recursive path behavior

- For requests that search, find, list, inspect, read, or count files/content in a directory or path, generated commands should be recursive by default.
- Prefer appropriate tools and flags such as `find`, `grep -R`, `rg`, `ls -R`, or recursive shell globs.

### Error noise behavior

- For recursive path searches, directory scans, and reads that may hit unreadable files or directories, hide stderr by default with `2>/dev/null`.
- Do not hide stderr for commands where errors are important for safety or diagnosis, such as install, delete, move, write, network, archive extraction, or other state-changing commands.
- With `--debug`, ask Pi not to add `2>/dev/null`.

### Cache behavior

- Save each successfully generated command to a local SQLite cache.
- Use `howcli -c` / `howcli --cache` to search the cache without calling Pi.
- Cache search uses fuzzy matching through `rapidfuzz`.
- Cache search shows up to 5 matches.
- Cache search prints the full top-ranked command as the final `COMMAND:` line.
- Cache search copies the top-ranked command to the clipboard when possible.

### Evaluation

- A golden set of query→command pairs lives in `eval/cases.json`, one JSON object per case with `id`, `query`, `command`, optional `soft` and `note`.
- `eval/run-eval.sh` runs each case through the real `howcli` stack with an isolated cache (`XDG_CACHE_HOME` under a temp dir) and clipboard disabled.
- A generated command matching the expected one exactly is `PASS`. A generated command equal to the expected one after style normalization (`norm`: quote stripping; `2>/dev/null`, `./` prefixes ignored; whitespace collapsed; `cmd … < file` ≡ `cmd … file`; `sort … | uniq` ≡ `sort -u …`) is `PASS~` and counts as a pass. A `soft` case with any non-empty output is `SOFT-OK`. Anything else is `DIFF` (or `ERROR` when generation produced no output and stderr carries an error).
- `--model` sets `HOWCLI_MODEL`; `--filter` runs a subset; `--out` writes a markdown report; `--quiet` hides `PASS` lines.
- Exit code `0` only when there are no `DIFF`/`ERROR` cases.
- `soft` cases are judge-dependent: the score counts only exact matches, so a model biased toward dry-run variants on destructive requests is not penalized there.

### Versioning

- `howcli --version` prints the wrapper version.
- `howcli-cache --version` prints the Python cache CLI version.
- Current version: `0.3.2`.

## CLI surface

```bash
howcli "natural language request"
howcli --run "natural language request"
howcli --debug "natural language request"
howcli -c "cache search"
howcli --cache "cache search"
howcli --version
```

Cache helper:

```bash
howcli-cache save --query "..." --command "..."
howcli-cache search "..."
howcli-cache list
howcli-cache top "..."
howcli-cache clear
howcli-cache --version
```

## Cache location

Default path:

```text
${XDG_CACHE_HOME:-~/.cache}/howcli/cache.sqlite
```

## Cache schema

Current SQLite table:

```sql
CREATE TABLE IF NOT EXISTS cache (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  query_original TEXT NOT NULL,
  query_norm TEXT NOT NULL,
  command TEXT NOT NULL,
  debug INTEGER NOT NULL DEFAULT 0,
  used_count INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_used_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(query_norm, command)
);
```

Indexes:

```sql
CREATE INDEX IF NOT EXISTS idx_cache_query_norm ON cache(query_norm);
CREATE INDEX IF NOT EXISTS idx_cache_last_used ON cache(last_used_at);
```

### Field meanings

| Field | Meaning |
| --- | --- |
| `id` | Internal autoincrement row identifier. |
| `query_original` | Original natural-language request. |
| `query_norm` | Normalized request used for matching and uniqueness. |
| `command` | Generated shell command. |
| `debug` | `1` if generated with debug mode, otherwise `0`. |
| `used_count` | Number of times the same normalized query and command were saved. |
| `created_at` | First insertion timestamp, in SQLite `CURRENT_TIMESTAMP` format. |
| `last_used_at` | Last save timestamp, updated on conflict. |

Uniqueness is defined by:

```sql
UNIQUE(query_norm, command)
```

This allows the same normalized request to map to different commands over time, while repeated identical request-command pairs increment `used_count`.

## Cache ranking

For a query, `howcli-cache` scores recent cache rows using:

- exact normalized query match;
- normalized substring match in the saved query;
- normalized substring match in the command;
- `rapidfuzz.token_set_ratio` against the saved query;
- `rapidfuzz.partial_ratio` against the saved query;
- `rapidfuzz.partial_ratio` against the command;
- a small `used_count` bonus.

Rows below the minimum score are ignored. Default minimum score is `35`.

## Installation

`make install` installs:

```text
~/.pi/agent/extensions/shell-command.ts
~/bin/howcli
~/.local/bin/howcli-cache
```

`howcli-cache` is installed with:

```bash
uv tool install --force --refresh --reinstall ./howcli-cache
```

The refresh/reinstall flags avoid stale local builds when the package version does not change.

## Non-goals

- `howcli` is not a shell executor by default.
- Cache search does not call Pi or generate new commands.
- Cache search is not a vector database.
- The cache schema is local and may evolve before stronger compatibility guarantees are needed.
