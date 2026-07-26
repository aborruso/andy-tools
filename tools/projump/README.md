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
```

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
