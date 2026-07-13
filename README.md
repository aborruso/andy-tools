# Andy Tools

A personal collection of small tools for practical tasks, automation, and everyday workflows.

## Tools

| Tool | Description | Documentation |
| --- | --- | --- |
| `wopen` | Open a file, directory, or URL from WSL/Linux with Windows. Copy file content to the Windows clipboard with `-c`. | [README](tools/wopen/README.md) |
| `pi-shell-command` | Pi extension and `howcli` command that turn natural-language requests into shell commands without executing them by default. Requires Pi Coding Agent. | [README](tools/pi-shell-command/README.md) |
| `gread` | Show unread primary Gmail messages from the last 7 days for `gws` or `gwsb`, with sender exclusions loaded from files. | [README](tools/gread/README.md) |
| `projump` | Jump to one of the most recently created git project folders under home via `projump-path` + shell `cd` function. | [README](tools/projump/README.md) |
| `md-gist` | Publish Markdown quickly to GitHub Gist from a file or stdin, with optional copy/open/raw output helpers. | [README](tools/md-gist/README.md) |
| `bookmarklets` | Browser bookmarklets for GitHub and other productivity tasks. | [README](tools/bookmarklets/README.md) |
| `linux-cleanup` | Safely clean cache and temp files on Linux/WSL2 (`~/.cache`, `/tmp`, apt). Supports `--dry-run` and `--no-sudo`. | [script](tools/linux-cleanup/linux-cleanup.sh) |
| `stale-repos` | List abandoned, bulky git repos (no recent commit/edit, over a size threshold; dirty repos excluded) as candidates to move/archive. List-only. | [README](tools/stale-repos/README.md) |
| `esearch` | Wrapper around the Everything search CLI (`es.exe`) for WSL: plain words become glob patterns (`*word*`), output re-encoded from cp850 to UTF-8. | [README](tools/esearch/README.md) |
