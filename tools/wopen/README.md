# wopen

`wopen` is a small command-line tool for Linux environments running inside WSL.

It opens files, directories, and URLs from a WSL/Linux shell using Windows applications. Files and URLs are opened with the default Windows app, while directories are opened explicitly in Windows File Explorer.

The tool is designed to be useful both for humans working in a shell and for AI agents that need a simple, non-interactive way to open local files, folders, or web links on the Windows side.

## Usage

```bash
wopen <file|directory|url>
wopen --help
```

Examples:

```bash
wopen info.md
wopen /home/user/info.md
wopen .
wopen /mnt/c/Users/user/Desktop/trash
wopen 'C:\Users\user\Desktop\info.md'
wopen https://example.com
```

## Install

### Install from Git

Clone the repository, enter it, and run the installer:

```bash
git clone https://github.com/aborruso/andy-tools.git andy-tools
cd andy-tools
make -C tools/wopen install
```

If you already cloned the repository, run this from the repository root:

```bash
make -C tools/wopen install
```

By default, this copies the `wopen` executable to:

```text
$HOME/bin/wopen
```

Make sure `$HOME/bin` is in your `PATH`. If it is not, add it to the startup file used by your shell, for example `~/.bashrc`, `~/.zshrc`, or another shell-specific configuration file:

```sh
export PATH="$HOME/bin:$PATH"
```

Then restart or reload your shell and check that `wopen` is available:

```bash
wopen --help
```

To install to a different directory, pass `BINDIR` explicitly:

```bash
make -C tools/wopen install BINDIR=/usr/local/bin
```

### Check that it works

Run:

```bash
wopen .
```

This should open the current WSL/Linux directory in Windows File Explorer.

### Uninstall

From the repository root, run:

```bash
make -C tools/wopen uninstall
```

This removes:

```text
$HOME/bin/wopen
```

If you installed to a custom directory, pass the same `BINDIR` value:

```bash
make -C tools/wopen uninstall BINDIR=/usr/local/bin
```

## Notes

- Non-interactive: never prompts for input.
- Requires exactly one argument.
- Linux/WSL paths are converted with `wslpath -w`.
- Linux/WSL directories, including paths like `/mnt/c/Users/...`, are opened with `explorer.exe`.
- Windows paths are passed through unchanged.
- Files and URLs are delegated to PowerShell `Start-Process -FilePath`, so Windows chooses the default application.
- Error messages fail fast and suggest the next valid command.
