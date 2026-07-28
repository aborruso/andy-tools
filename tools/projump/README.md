# projump

Jump to one of the most recently created git project folders under your home directory.

`projump-path` is the installable CLI. It scans for git repositories, shows the 20 most recently active, and prints only the selected path.

A shell function named `projump` can then use that path to `cd` in the current shell.

## Usage

```bash
projump-path
projump-path --limit 20
projump-path --root ~/git
projump-path --all
projump-path --live
```

| Option | Description |
| --- | --- |
| `-r`, `--root` | Root directory to scan (default `~`) |
| `-n`, `--limit` | Number of repositories to show (default 20) |
| `-a`, `--all` | Include hidden/tool-managed repositories |
| `-l`, `--live` | Ignore the cache, rescan now and refresh the cache |
| `--refresh-only` | Rescan and update the cache without showing the selector |

Keyboard shortcuts:

| Key | Action |
| --- | --- |
| `↑` / `k` | Move up |
| `↓` / `j` | Move down |
| `Enter` | Print selected path |
| `q` / `Esc` | Cancel |

## Shell function

Add this to your shell configuration:

```bash
projump() {
  if [[ "${1:-}" == "-h" || "${1:-}" == "--help" || "${1:-}" == "--version" || "${1:-}" == "-v" ]]; then
    projump-path "$@"
    return
  fi

  local tmp dir rc
  tmp="$(mktemp)" || return
  projump-path "$@" > "$tmp"
  rc=$?
  dir="$(cat "$tmp")"
  rm -f "$tmp"

  [[ $rc -eq 0 ]] || return $rc
  [[ -n "$dir" ]] && cd "$dir"
}
```

Then run:

```bash
projump
```

## Discovery

- Uses `fd` when available (`fd` or `fdfind`).
- Falls back to `find`.
- Searches for `.git` directories under `~` by default.
- By default, hides tool/cache repositories under hidden paths such as `~/.gemini/...` and project folders whose name starts with `.`.
- Use `--all` to include hidden/tool-managed repositories.
- Sorts repositories by the most recent of: folder creation time, latest `git reflog` entry, and latest commit timestamp across local and remote branches. This keeps actively-worked projects on top even when their folder was created long ago.
- Runs the `git` probes concurrently (16 repositories at a time), so a full scan of ~400 repositories takes a couple of seconds instead of six.

## Cache

The scan result is cached, so a normal run starts in a few milliseconds instead of seconds.

- Location: `${XDG_CACHE_HOME:-~/.cache}/projump/<key>.json`, one file per `--root` + `--all` combination.
- The full sorted list is cached; `--limit` is applied when reading, so changing `-n` never needs a rescan.
- Repositories that no longer exist on disk are dropped when the cache is read.
- TTL: 24 hours. Past that, the next run rescans.
- If the cache is older than 10 minutes, the list is still shown immediately from cache and a detached background process refreshes it for the next run.
- To force a rescan: `projump --live` (or `-l`). Deleting the cache directory works too.
- `projump-path --refresh-only` updates the cache without opening the selector — useful to warm it up from a shell startup file or a cron job.

## Install

From the repo root:

```bash
make -C tools/projump install
```

Installs `projump-path` to `~/bin/projump-path` and runtime files to `~/share/projump/`.

## Dependencies

- Node.js 18+
- [`citty`](https://github.com/unjs/citty)
- Optional: [`fd`](https://github.com/sharkdp/fd) for faster discovery

## Check

```bash
make -C tools/projump check
```

## Uninstall

```bash
make -C tools/projump uninstall
```
