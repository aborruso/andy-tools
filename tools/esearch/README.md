# esearch

`esearch` is a small command-line wrapper around the [Everything](https://www.voidtools.com/) search CLI (`es.exe`) for Linux/WSL environments.

It turns plain words into Everything glob patterns (`*word*`), so a natural query like:

```bash
esearch report 2024 xlsx
```

becomes the equivalent of:

```bash
es.exe *report* *2024* *xlsx*
```

It also re-encodes the output from the Windows OEM codepage (cp850) to UTF-8, so accented characters and paths display correctly in a Linux terminal.

The tool is designed to be useful both for humans working in a shell and for AI agents that need a simple, non-interactive way to search files on the Windows side via Everything.

## Why Everything

[Everything](https://www.voidtools.com/) is a Windows desktop search engine that maintains a real-time index of every file and folder on all NTFS drives. Because it indexes the filesystem at the MFT level rather than scanning directories, searches are near-instantaneous even across millions of files — results appear in milliseconds regardless of drive size.

The index is global and always up to date: there is no need to run a crawl or wait for a scheduled scan. This makes it a reliable foundation for any workflow that needs to locate files quickly, from the shell or from an AI agent, without knowing in advance where a file might be stored.

## Requirements

- [Everything](https://www.voidtools.com/) installed and running on Windows.
- The Everything command-line interface `es.exe`. Get it from the [ES CLI page](https://www.voidtools.com/support/everything/command_line_interface/), for example at `C:\Programmi\Everything\es.exe` (i.e. `/mnt/c/Programmi/Everything/es.exe` from WSL).
- `iconv` (usually provided by `glibc` / `libc-bin`).

## Usage

```bash
esearch [es-options] <query...>
esearch --help
```

### Query rewriting (default)

Each plain token is split on whitespace and every resulting word is wrapped as a glob (`*word*`). Tokens that look like flags (`-x`) or that contain `:` (paths like `C:\...`, or Everything search terms like `ext:pdf`) are passed through verbatim.

Examples:

```bash
esearch report 2024 xlsx
esearch *.csv path:C:\Users
esearch -r -n 20 invoice
esearch ext:pdf budget
```

### Options

| Option | Description |
| --- | --- |
| `--es-path <path>` | Path to `es.exe`. Default: `$ESEARCH_ES_PATH` or `/mnt/c/Programmi/Everything/es.exe`. |
| `--from-enc <enc>` | Source encoding. Default: `cp850` (env: `ESEARCH_FROM_ENC`). |
| `--to-enc <enc>` | Target encoding. Default: `utf-8` (env: `ESEARCH_TO_ENC`). |
| `--raw` | Disable query rewriting: pass all tokens verbatim to `es.exe`. |
| `--no-iconv` | Skip the `cp850` → `utf-8` conversion. |
| `-h, --help` | Show help. |

### Environment variables

| Variable | Description |
| --- | --- |
| `ESEARCH_ES_PATH` | Override the `es.exe` location. |
| `ESEARCH_FROM_ENC` | Override the source encoding (default `cp850`). |
| `ESEARCH_TO_ENC` | Override the target encoding (default `utf-8`). |

### Passing Everything flags

Everything `es.exe` flags (e.g. `-r` for regex, `-n <count>` to limit results, `-s` for whole-word, `-i` case-insensitive) are forwarded as-is because they start with `-`:

```bash
esearch -n 10 -i progetto
```

## Install

### Install from Git

Clone the repository, enter it, and run the installer:

```bash
git clone https://github.com/aborruso/andy-tools.git andy-tools
cd andy-tools
make -C tools/esearch install
```

If you already cloned the repository, run this from the repository root:

```bash
make -C tools/esearch install
```

By default, this copies the `esearch` executable to:

```text
$HOME/bin/esearch
```

Make sure `$HOME/bin` is in your `PATH`. If it is not, add it to the startup file used by your shell, for example `~/.bashrc`, `~/.zshrc`, or another shell-specific configuration file:

```sh
export PATH="$HOME/bin:$PATH"
```

Then restart or reload your shell and check that `esearch` is available:

```bash
esearch --help
```

To install to a different directory, pass `BINDIR` explicitly:

```bash
make -C tools/esearch install BINDIR=/usr/local/bin
```

### Check that it works

Run a simple search:

```bash
esearch readme
```

### Uninstall

From the repository root, run:

```bash
make -C tools/esearch uninstall
```

This removes:

```text
$HOME/bin/esearch
```

If you installed to a custom directory, pass the same `BINDIR` value:

```bash
make -C tools/esearch uninstall BINDIR=/usr/local/bin
```

## Notes

- Non-interactive: never prompts for input.
- If `es.exe` is not found at the expected location, set it via `--es-path` or `ESEARCH_ES_PATH`.
- The default `es.exe` output uses the OEM codepage (cp850); `esearch` pipes it through `iconv -f cp850 -t utf-8`. Use `--no-iconv` if your `es.exe` already outputs UTF-8 (Everything has a UTF-8 output option).
- Use `--raw` when you want to pass a complex Everything query without any rewriting.

## Usage in non-interactive environments (AI agents, CI)

`esearch` works reliably from non-interactive shells (e.g. Claude Code, Pi, scripts) with a plain call:

```bash
esearch invoice 2024 pdf
```
