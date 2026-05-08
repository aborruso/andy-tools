# gread

`gread` shows unread primary Gmail messages from the last 7 days for one of two configured Google Workspace CLIs: `gws` or `gwsb`.

It wraps this fixed command shape:

```bash
<profile> gmail +triage --max 50 --format table --query '<query>'
```

The base query is fixed:

```text
is:unread category:primary newer_than:7d
```

Sender exclusions are read from text files instead of being hardcoded in the command line.

## Usage

```bash
gread gws
gread gwsb
gread --help
```

## Exclude files

Exclude files are in:

```text
excludes/global.txt
excludes/gws.txt
excludes/gwsb.txt
```

`global.txt` applies to all profiles. The profile-specific file applies only to that profile.

Each non-empty, non-comment line becomes a Gmail query term:

```text
-from:<value>
```

Example:

```text
noreply
@substack.com
calendar-notification@google.com
```

becomes:

```text
-from:noreply -from:@substack.com -from:calendar-notification@google.com
```

Lines starting with `#` are ignored. Inline comments are also ignored.

## Install

From the repository root:

```bash
make -C tools/gread install
```

By default, this installs:

```text
$HOME/bin/gread
$HOME/share/gread/excludes/*.txt
```

Make sure `$HOME/bin` is in your `PATH`.

To install elsewhere:

```bash
make -C tools/gread install BINDIR=/usr/local/bin DATADIR=$HOME/.local/share/gread
```

## Configuration lookup

`gread` searches exclude files in this order:

1. `GREAD_EXCLUDES_DIR`, if set;
2. `excludes/` next to the script, useful when running from the repository;
3. `../share/gread/excludes` relative to the installed script, useful after `make install`;
4. `$HOME/share/gread/excludes`, the default install location.

## Check

```bash
make -C tools/gread check
```

## Uninstall

```bash
make -C tools/gread uninstall
```
