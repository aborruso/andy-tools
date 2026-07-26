#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import readline from "node:readline";
import { defineCommand, runMain } from "citty";

const VERSION = "0.1.0";

const command = defineCommand({
  meta: {
    name: "projump-path",
    version: VERSION,
    description: "Select a recently created git project folder and print its path.",
  },
  args: {
    root: {
      type: "string",
      alias: "r",
      default: "~",
      description: "Root directory to scan.",
    },
    limit: {
      type: "string",
      alias: "n",
      default: "20",
      description: "Number of recent repositories to show.",
    },
    all: {
      type: "boolean",
      alias: "a",
      default: false,
      description: "Include hidden/tool-managed repositories.",
    },
  },
  async run({ args }) {
    const root = expandHome(String(args.root ?? "~"));
    const limit = parsePositiveInt(args.limit, "--limit");
    const includeAll = Boolean(args.all);

    if (!fs.existsSync(root) || !fs.statSync(root).isDirectory()) {
      console.error(`projump-path: root is not a directory: ${root}`);
      process.exitCode = 2;
      return;
    }

    console.error(`Scanning ${prettyPath(root)} for git repositories...`);
    const repos = findGitRepos(root)
      .map((repoPath) => toRepo(repoPath))
      .filter(Boolean)
      .filter((repo) => includeAll || isVisibleProject(repo.path))
      .sort((a, b) => b.sortMs - a.sortMs)
      .slice(0, limit);

    if (repos.length === 0) {
      console.error(`projump-path: no git repositories found under ${root}`);
      process.exitCode = 1;
      return;
    }

    const selected = await selectRepo(repos, root);
    if (!selected) {
      process.exitCode = 130;
      return;
    }

    process.stdout.write(`${selected.path}\n`);
  },
});

runMain(command);

function expandHome(value) {
  if (value === "~") return os.homedir();
  if (value.startsWith("~/")) return path.join(os.homedir(), value.slice(2));
  return path.resolve(value);
}

function parsePositiveInt(value, name) {
  const parsed = Number.parseInt(String(value), 10);
  if (!Number.isFinite(parsed) || parsed < 1) {
    console.error(`projump-path: ${name} must be a positive integer`);
    process.exit(2);
  }
  return parsed;
}

function findGitRepos(root) {
  const fd = firstCommand(["fd", "fdfind"]);
  if (fd) {
    const result = spawnSync(fd, ["-H", "-t", "d", "^\\.git$", root], {
      encoding: "utf8",
      maxBuffer: 1024 * 1024 * 64,
    });

    if (result.status === 0 || result.status === 1) {
      return lines(result.stdout);
    }

    console.error(`projump-path: fd failed, falling back to find (${result.stderr.trim()})`);
  }

  const result = spawnSync("find", [root, "-xdev", "-type", "d", "-name", ".git", "-print", "-prune"], {
    encoding: "utf8",
    maxBuffer: 1024 * 1024 * 64,
  });

  if (result.status !== 0) {
    console.error(result.stderr.trim() || "projump-path: find failed");
    process.exit(1);
  }

  return lines(result.stdout);
}

function firstCommand(commands) {
  for (const commandName of commands) {
    const result = spawnSync("sh", ["-c", `command -v ${commandName} >/dev/null 2>&1`], {
      stdio: "ignore",
    });
    if (result.status === 0) return commandName;
  }
  return null;
}

function lines(text) {
  return text.split("\n").map((line) => line.trim()).filter(Boolean);
}

function toRepo(gitDir) {
  const repoPath = path.dirname(gitDir);
  try {
    const stat = fs.statSync(repoPath);
    const birthMs = stat.birthtimeMs > 0 ? stat.birthtimeMs : stat.mtimeMs;
    const sortMs = Math.max(birthMs, gitActivityMs(repoPath));
    return { path: repoPath, sortMs };
  } catch {
    return null;
  }
}

function gitActivityMs(repoPath) {
  let best = 0;

  const reflog = runGit(repoPath, ["reflog", "-n1", "--format=%ct"]);
  best = Math.max(best, parseUnixSeconds(reflog));

  const commit = runGit(repoPath, [
    "for-each-ref",
    "--sort=-committerdate",
    "--count=1",
    "--format=%(committerdate:unix)",
    "refs/heads",
    "refs/remotes",
  ]);
  best = Math.max(best, parseUnixSeconds(commit));

  return best;
}

function runGit(repoPath, gitArgs) {
  const result = spawnSync("git", ["-C", repoPath, ...gitArgs], {
    encoding: "utf8",
    timeout: 2000,
  });
  if (result.status !== 0) return "";
  return (result.stdout || "").trim();
}

function parseUnixSeconds(text) {
  if (!text) return 0;
  const seconds = Number.parseInt(text, 10);
  if (!Number.isFinite(seconds) || seconds <= 0) return 0;
  return seconds * 1000;
}

function isVisibleProject(repoPath) {
  const relative = path.relative(os.homedir(), repoPath);
  if (relative.startsWith("..") || path.isAbsolute(relative)) {
    return !path.basename(repoPath).startsWith(".");
  }

  return relative
    .split(path.sep)
    .filter(Boolean)
    .every((part) => !part.startsWith("."));
}

async function selectRepo(repos, root) {
  if (!process.stdin.isTTY) {
    console.error("projump-path: interactive selection requires a TTY");
    return null;
  }

  const input = process.stdin;
  const output = process.stderr;
  let index = 0;
  let renderedLines = 0;

  readline.emitKeypressEvents(input);
  input.setRawMode(true);
  output.write("\x1b[?25l");

  return new Promise((resolve) => {
    const cleanup = (value) => {
      input.setRawMode(false);
      input.off("keypress", onKeypress);
      input.pause();
      output.write("\x1b[?25h");
      output.write("\n");
      resolve(value);
    };

    const render = () => {
      if (renderedLines > 0) {
        output.write(`\x1b[${renderedLines}F`);
        output.write("\x1b[J");
      }

      const rows = buildRows(repos, index, root);
      renderedLines = rows.length;
      output.write(rows.join("\n"));
      output.write("\n");
    };

    const onKeypress = (_str, key) => {
      if (key?.name === "up" || key?.name === "k") {
        index = (index - 1 + repos.length) % repos.length;
        render();
        return;
      }

      if (key?.name === "down" || key?.name === "j") {
        index = (index + 1) % repos.length;
        render();
        return;
      }

      if (key?.name === "return" || key?.name === "enter") {
        cleanup(repos[index]);
        return;
      }

      if (key?.name === "escape" || key?.name === "q" || (key?.ctrl && key?.name === "c")) {
        cleanup(null);
      }
    };

    input.on("keypress", onKeypress);
    render();
  });
}

function buildRows(repos, selectedIndex, root) {
  const rows = [
    `Select a project (${repos.length} newest by activity)`,
    "↑/k ↓/j move · Enter select · q/Esc cancel",
    "",
  ];

  for (let i = 0; i < repos.length; i++) {
    const repo = repos[i];
    const marker = i === selectedIndex ? "›" : " ";
    const date = new Date(repo.sortMs).toISOString().slice(0, 10);
    const label = `${date}  ${prettyPath(repo.path, root)}`;
    rows.push(i === selectedIndex ? `${marker} \x1b[1m${label}\x1b[0m` : `${marker} ${label}`);
  }

  return rows;
}

function prettyPath(value, root = os.homedir()) {
  const home = os.homedir();
  if (value === home) return "~";
  if (value.startsWith(`${home}${path.sep}`)) return `~/${path.relative(home, value)}`;
  if (value.startsWith(`${root}${path.sep}`)) return path.relative(root, value);
  return value;
}
