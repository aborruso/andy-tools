# md-gist

`md-gist` publishes Markdown quickly to GitHub Gist.

It is designed for the fast path: take a Markdown file or piped input, create a gist, and return a shareable URL.

## Usage

```bash
md-gist [options] [FILE]
md-gist --help
```

Examples:

```bash
md-gist note.md
printf '# Hello\n' | md-gist
printf '# Hello\n' | md-gist --filename hello.md --copy
md-gist note.md --description 'Shared via terminal'
md-gist note.md --secret
md-gist note.md --raw
md-gist note.md --open
```

## Behavior

- Accepts input from a file path or stdin.
- If both `FILE` and stdin are present, `FILE` wins.
- Defaults to a public gist.
- Prints the gist page URL.
- With `--raw`, prints only the raw URL.

## Options

- `-d, --description <text>`: gist description. Default: `Shared via md-gist`
- `-f, --filename <name>`: filename inside the gist
- `-p, --public`: create a public gist
- `-s, --secret`: create a secret gist
- `-c, --copy`: copy the resulting URL to the clipboard when possible
- `-r, --raw`: print only the raw URL
- `-o, --open`: open the gist page in the browser
- `-h, --help`: show help

## Defaults

- file input: keep the file basename unless `--filename` is passed
- stdin input: use `note.md` unless `--filename` is passed
- description: `Shared via md-gist`

## Dependencies

Required:
- `gh`

Optional:
- `xclip`, `wl-copy`, or `clip.exe` for `--copy`
- `xdg-open`, `open`, or Windows interop for `--open`

You must be authenticated with GitHub CLI:

```bash
gh auth login
```

## Install

From the repository root:

```bash
make -C tools/md-gist install
```

By default, this installs:

```text
$HOME/bin/md-gist
```

Make sure `$HOME/bin` is in your `PATH`.

To install elsewhere:

```bash
make -C tools/md-gist install BINDIR=/usr/local/bin
```

## Check

```bash
make -C tools/md-gist check
```

## Uninstall

```bash
make -C tools/md-gist uninstall
```
