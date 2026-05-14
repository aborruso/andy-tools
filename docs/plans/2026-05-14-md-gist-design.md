# md-gist design

## Summary

Create a small standalone CLI tool named `md-gist` to publish Markdown quickly as a GitHub Gist, with a future path to Pi integration but no Pi-specific work now.

## Goal

Make a Markdown note immediately readable and shareable by publishing it as a gist with minimal friction.

## Scope

Initial scope is a Bash CLI in `tools/md-gist/`.

It should:
- accept Markdown from a file path or stdin;
- publish through `gh gist create`;
- default to a public gist;
- print the resulting URL;
- optionally copy the URL to the clipboard;
- optionally open the gist in the browser;
- optionally print the raw URL.

It should not yet:
- integrate with Pi;
- add rendering beyond what GitHub Gist already provides;
- introduce packaging beyond repo conventions.

## Recommended approach

Implement `md-gist` as a small Bash script wrapping `gh gist create`.

Why:
- closest to the original alias;
- minimal code and dependencies;
- consistent with the repository style of practical small tools;
- easy to evolve later into a Pi-facing command.

## Alternatives considered

### Pure wrapper alias

Very fast, but too limited as a reusable repo tool.

### Python CLI

More robust for growth, but heavier than needed for the initial use case.

## CLI shape

Command:
- `md-gist [FILE]`

Initial options:
- `-d, --description <text>`
- `-f, --filename <name>`
- `-p, --public`
- `-s, --secret`
- `-c, --copy`
- `-r, --raw`
- `-o, --open`
- `-h, --help`

## Defaults

- visibility: public
- input from file: use file basename as gist filename
- input from stdin: use `note.md` unless overridden
- description: simple default placeholder, to be finalized during implementation
- output: gist URL on stdout

## Input handling

Supported first-class flows:
- `md-gist file.md`
- `cat file.md | md-gist`

Behavior:
- if a file path is provided, publish that file content;
- if stdin is present, publish stdin content;
- if both are present, implementation must choose a clear precedence and document it;
- if neither is present, exit with a short usage error.

## Output behavior

Base behavior:
- print the gist page URL.

Optional behaviors:
- `--copy`: copy final URL to clipboard when supported;
- `--open`: open gist page in browser;
- `--raw`: print raw URL instead of page URL.

## Dependencies

Required:
- `gh`

Optional:
- clipboard tool such as `xclip`, `wl-copy`, or `clip.exe`
- browser opener available on the host environment

## Error handling

Handle clearly:
- missing `gh`;
- failed `gh` auth or gist creation;
- file not found;
- no input provided;
- clipboard requested but unavailable;
- raw URL requested but not derivable.

Preference:
- fail hard on publish errors;
- degrade gracefully on post-publish conveniences like clipboard/open.

## Testing

Initial manual checks:
- publish from file;
- publish from stdin;
- custom description;
- custom filename for stdin;
- public vs secret;
- copy URL;
- open URL;
- raw URL output;
- no-input error;
- missing-file error.

## Future path

Possible later work:
- integrate into Pi as a command or tool;
- add install helper/Makefile if useful;
- support richer output modes for scripts.

## Decision

Start with a small autonomous Bash CLI, designed cleanly enough to be reused later by Pi.

## Open questions

- exact default description text;
- precedence if both file argument and stdin are present;
- whether `--raw` should print only raw URL or support both outputs later.
