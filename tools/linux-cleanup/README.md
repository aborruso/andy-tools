# linux-cleanup

Safely clean cache and temporary files on Linux/WSL2.

## Usage

```bash
bash linux-cleanup.sh [--dry-run] [--no-sudo] [--tmp-days N]
```

| Flag | Description |
|---|---|
| `--dry-run` | Show what would be removed without making any changes |
| `--no-sudo` | Skip the system section (apt, journal) that requires sudo |
| `--tmp-days N` | Delete files in `/tmp` older than N days (default: 7) |

## What it cleans

### User cache (`~/.cache`) — no sudo required

| Path | Command |
|---|---|
| `~/.cache/uv` | `uv cache clean` |
| `~/.cache/go-build` | `go clean -cache` |
| `~/.cache/printing-press` | `rm -rf` |
| `~/.cache/pip` | `pip cache purge` |
| `~/.cache/pnpm` | `pnpm store prune` |
| `~/.cache/ort.pyke.io` | `rm -rf` |
| `~/.cache/node-gyp` | `rm -rf` |
| `~/.cache/pyright-python` | `rm -rf` |
| `~/.cache/opencode` | `rm -rf` |
| `~/.cache/typescript` | `rm -rf` |
| `~/.cache/deno` | `rm -rf` |

### `/tmp` — files older than N days (default 7)

Removes files and directories in `/tmp` older than the configured threshold. Linux automatically cleans `/tmp` via `systemd-tmpfiles` at 10 days, so values between 7 and 10 avoid redundant work. Skips:
- `claude-*` — active Claude Code session
- `dbus-*`, `*.sock` — system sockets
- `.org.chromium*` — Chromium lock files

Permission-denied entries are skipped silently.

### System — requires sudo

| Action | Command |
|---|---|
| APT package cache | `apt-get clean` |
| Journal logs older than 7 days | `journalctl --vacuum-time=7d` |

## WSL2 note

Freeing space inside WSL does **not** compact the `ext4.vhdx` file on Windows. To reclaim disk space on the host:

```powershell
# 1. Shut down WSL
wsl --shutdown

# 2. Find the vhdx path
Get-ChildItem "$env:LOCALAPPDATA\Packages" -Recurse -Filter ext4.vhdx | Select FullName

# 3. Compact it (PowerShell as Administrator)
Optimize-VHD -Path <path> -Mode Full
```
