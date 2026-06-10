# gread

Interactive Gmail triage TUI.

`gread` shows starred or unread primary Gmail messages from the last 7 days in a navigable list. Use keyboard shortcuts to archive, star/unstar, mark read/unread, and read emails.

All authentication is delegated to the `gws` / `gwsb` CLI — if that works, gread works.

## Usage

```bash
gread gws
gread gwsb
gread gws --exclude "pec,bic,cip"
gread --help
```

## Keyboard shortcuts

| Key | Action |
|-----|--------|
| `↑` / `k` | Move up |
| `↓` / `j` | Move down |
| `Space` | Toggle selection |
| `Enter` | Read full email |
| `a` | Archive selected (or cursor) |
| `s` | Toggle star ★ |
| `r` | Mark as read |
| `u` | Mark as unread |
| `x` | Read + archive |
| `q` / `Esc` | Quit |

## Exclude files

Sender exclusions live in:

```text
excludes/global.txt     # applies to all profiles
excludes/gws.txt        # gws only
excludes/gwsb.txt       # gwsb only
```

Each non-empty, non-comment line becomes `-from:<value>` in the Gmail query.

```text
# example global.txt
noreply
@substack.com
```

## Install

From the repo root:

```bash
make -C tools/gread install
```

Installs to `~/bin/gread` and `~/share/gread/`. Requires Node.js and `npx` in PATH.

## Dependencies

- [Ink](https://github.com/vadimdemedes/ink) (React for CLI)
- [gws](https://github.com/googleworkspace/cli) (Google Workspace CLI)
- Node.js 18+

## Check

```bash
make -C tools/gread check
```

## Uninstall

```bash
make -C tools/gread uninstall
```
