# Andy Tools

A personal collection of small tools for practical tasks, automation, and everyday workflows.

## Tools

| Tool | Description | Documentation |
| --- | --- | --- |
| `wopen` | Open a file, directory, or URL from WSL/Linux with Windows. | [README](tools/wopen/README.md) |
| `pi-shell-command` | Pi extension and `howcli` command that turn natural-language requests into shell commands without executing them by default. Requires Pi Coding Agent. | [README](tools/pi-shell-command/README.md) |

## Quick install

### pi-shell-command

Prerequisite: install and configure Pi Coding Agent.

```bash
npm install -g @earendil-works/pi-coding-agent
```

Then install `howcli` and the Pi extension:

```bash
cd tools/pi-shell-command
make install
```

Usage:

```bash
howcli "lista i file della cartella corrente"
howcli --run "lista i file della cartella corrente"
```
