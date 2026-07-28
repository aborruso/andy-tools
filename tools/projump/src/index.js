#!/usr/bin/env node
import { execFile, spawn, spawnSync } from "node:child_process";
import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import readline from "node:readline";
import { fileURLToPath } from "node:url";
import { promisify } from "node:util";
import { defineCommand, runMain } from "citty";

const VERSION = "0.3.0";
const CACHE_VERSION = 1;
const CACHE_TTL_MS = 24 * 60 * 60 * 1000;
const CACHE_REFRESH_AFTER_MS = 10 * 60 * 1000;
const GIT_CONCURRENCY = 16;

const execFileAsync = promisify(execFile);
const SELF = fileURLToPath(import.meta.url);

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
      default: "40",
      description: "Maximum number of repositories to show.",
    },
    all: {
      type: "boolean",
      alias: "a",
      default: false,
      description: "Include hidden/tool-managed repositories.",
    },
    live: {
      type: "boolean",
      alias: "l",
      default: false,
      description: "Ignore the cache, rescan now and refresh the cache.",
    },
    "refresh-only": {
      type: "boolean",
      default: false,
      description: "Rescan and update the cache without showing the selector.",
    },
  },
  async run({ args }) {
    const root = expandHome(String(args.root ?? "~"));
    const limit = parsePositiveInt(args.limit, "--limit");
    const includeAll = Boolean(args.all);
    const live = Boolean(args.live);
    const refreshOnly = Boolean(args["refresh-only"]);

    if (!fs.existsSync(root) || !fs.statSync(root).isDirectory()) {
      console.error(`projump-path: root is not a directory: ${root}`);
      process.exitCode = 2;
      return;
    }

    const cacheFile = cachePath(root, includeAll);

    if (refreshOnly) {
      writeCache(cacheFile, root, includeAll, await scanRepos(root, includeAll));
      return;
    }

    let repos = live ? null : readCache(cacheFile, root, includeAll);
    const fromCache = repos !== null;

    if (!fromCache) {
      console.error(`Scanning ${prettyPath(root)} for git repositories...`);
      repos = await scanRepos(root, includeAll);
      writeCache(cacheFile, root, includeAll, repos);
    }

    if (repos.length === 0) {
      console.error(`projump-path: no git repositories found under ${root}`);
      process.exitCode = 1;
      return;
    }

    const selected = await selectRepo(repos, root, fromCache, limit);
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

function cacheDir() {
  const base = process.env.XDG_CACHE_HOME || path.join(os.homedir(), ".cache");
  return path.join(base, "projump");
}

function cachePath(root, includeAll) {
  const key = crypto.createHash("sha1").update(`${root}\0${includeAll}`).digest("hex").slice(0, 16);
  return path.join(cacheDir(), `${key}.json`);
}

function readCache(cacheFile, root, includeAll) {
  let record;
  try {
    record = JSON.parse(fs.readFileSync(cacheFile, "utf8"));
  } catch {
    return null;
  }

  if (record?.version !== CACHE_VERSION) return null;
  if (record.root !== root || record.all !== includeAll) return null;
  if (!Array.isArray(record.repos)) return null;

  const age = Date.now() - Number(record.generatedAt ?? 0);
  if (!(age >= 0) || age > CACHE_TTL_MS) return null;

  const repos = record.repos.filter((repo) => repo?.path && fs.existsSync(repo.path));
  if (repos.length === 0) return null;

  if (age > CACHE_REFRESH_AFTER_MS) refreshInBackground(root, includeAll);

  return repos;
}

function writeCache(cacheFile, root, includeAll, repos) {
  if (repos.length === 0) return;

  const record = {
    version: CACHE_VERSION,
    generatedAt: Date.now(),
    root,
    all: includeAll,
    repos,
  };

  const tmpFile = `${cacheFile}.${process.pid}.tmp`;
  try {
    fs.mkdirSync(path.dirname(cacheFile), { recursive: true });
    fs.writeFileSync(tmpFile, `${JSON.stringify(record)}\n`);
    fs.renameSync(tmpFile, cacheFile);
  } catch (error) {
    try {
      fs.rmSync(tmpFile, { force: true });
    } catch {}
    console.error(`projump-path: could not write cache (${error.message})`);
  }
}

function refreshInBackground(root, includeAll) {
  try {
    const child = spawn(
      process.execPath,
      [SELF, "--refresh-only", "--root", root, ...(includeAll ? ["--all"] : [])],
      { detached: true, stdio: "ignore" },
    );
    child.unref();
  } catch {}
}

async function scanRepos(root, includeAll) {
  const repoPaths = findGitRepos(root)
    .map((gitDir) => path.dirname(gitDir))
    .filter((repoPath) => includeAll || isVisibleProject(repoPath));

  const repos = await mapLimit(repoPaths, GIT_CONCURRENCY, toRepo);

  return repos.filter(Boolean).sort((a, b) => b.sortMs - a.sortMs);
}

async function mapLimit(items, limit, worker) {
  const results = new Array(items.length);
  let next = 0;

  const runners = Array.from({ length: Math.min(limit, items.length) }, async () => {
    while (true) {
      const index = next++;
      if (index >= items.length) return;
      results[index] = await worker(items[index]);
    }
  });

  await Promise.all(runners);
  return results;
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

async function toRepo(repoPath) {
  let stat;
  try {
    stat = fs.statSync(repoPath);
  } catch {
    return null;
  }

  const birthMs = stat.birthtimeMs > 0 ? stat.birthtimeMs : stat.mtimeMs;
  const sortMs = Math.max(birthMs, await gitActivityMs(repoPath));
  return { path: repoPath, sortMs };
}

async function gitActivityMs(repoPath) {
  const [reflog, commit] = await Promise.all([
    runGit(repoPath, ["reflog", "-n1", "--format=%ct"]),
    runGit(repoPath, [
      "for-each-ref",
      "--sort=-committerdate",
      "--count=1",
      "--format=%(committerdate:unix)",
      "refs/heads",
      "refs/remotes",
    ]),
  ]);

  return Math.max(parseUnixSeconds(reflog), parseUnixSeconds(commit));
}

async function runGit(repoPath, gitArgs) {
  try {
    const { stdout } = await execFileAsync("git", ["-C", repoPath, ...gitArgs], {
      encoding: "utf8",
      timeout: 2000,
    });
    return (stdout || "").trim();
  } catch {
    return "";
  }
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

function fuzzyScore(query, text) {
  const haystack = text.toLowerCase();
  let score = 0;
  let searchFrom = 0;
  let previousMatch = -2;

  for (const char of query.toLowerCase()) {
    const found = haystack.indexOf(char, searchFrom);
    if (found === -1) return null;

    if (found === previousMatch + 1) score += 5;
    else if (found === 0 || "/-_. ".includes(haystack[found - 1])) score += 10;
    else score += 1;

    previousMatch = found;
    searchFrom = found + 1;
  }

  return score - haystack.length * 0.01;
}

async function selectRepo(repos, root, fromCache, limit) {
  if (!process.stdin.isTTY) {
    console.error("projump-path: interactive selection requires a TTY");
    return null;
  }

  const input = process.stdin;
  const output = process.stderr;
  let query = "";
  let filtered = repos.slice(0, limit);
  let index = 0;
  let renderedLines = 0;

  const applyFilter = () => {
    if (query === "") {
      filtered = repos.slice(0, limit);
    } else {
      filtered = repos
        .map((repo) => ({ repo, score: fuzzyScore(query, prettyPath(repo.path, root)) }))
        .filter((entry) => entry.score !== null)
        .sort((a, b) => b.score - a.score || b.repo.sortMs - a.repo.sortMs)
        .slice(0, limit)
        .map((entry) => entry.repo);
    }
    index = 0;
  };

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

      const rows = buildRows(filtered, index, root, fromCache, query, repos.length);
      renderedLines = rows.length;
      output.write(rows.join("\n"));
      output.write("\n");
    };

    const onKeypress = (str, key) => {
      if (key?.ctrl && key?.name === "c") {
        cleanup(null);
        return;
      }

      if (key?.name === "return" || key?.name === "enter") {
        if (filtered.length > 0) cleanup(filtered[index]);
        return;
      }

      if (key?.name === "escape") {
        if (query === "") {
          cleanup(null);
          return;
        }
        query = "";
        applyFilter();
        render();
        return;
      }

      if (key?.name === "up") {
        if (filtered.length > 0) index = (index - 1 + filtered.length) % filtered.length;
        render();
        return;
      }

      if (key?.name === "down") {
        if (filtered.length > 0) index = (index + 1) % filtered.length;
        render();
        return;
      }

      if (key?.name === "backspace") {
        query = query.slice(0, -1);
        applyFilter();
        render();
        return;
      }

      if (str && str.length === 1 && str >= " " && str !== "\x7f" && !key?.ctrl && !key?.meta) {
        query += str;
        applyFilter();
        render();
      }
    };

    input.on("keypress", onKeypress);
    render();
  });
}

function buildRows(filtered, selectedIndex, root, fromCache, query, total) {
  const source = fromCache ? "cached, -l to rescan" : "fresh scan";
  const status = query === "" ? `${filtered.length} newest by activity` : `${filtered.length}/${total} match`;
  const rows = [
    `Select a project (${status} · ${source})`,
    "type to filter · ↑/↓ move · Enter select · Esc clear/cancel",
    `\x1b[36m>\x1b[0m ${query}\x1b[7m \x1b[0m`,
    "",
  ];

  if (filtered.length === 0) {
    rows.push("  \x1b[2mno match\x1b[0m");
    return rows;
  }

  for (let i = 0; i < filtered.length; i++) {
    const repo = filtered[i];
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
