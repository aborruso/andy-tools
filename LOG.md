# LOG

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
