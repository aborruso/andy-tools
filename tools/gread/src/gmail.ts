import { execFile, execFileSync } from "node:child_process";
import { readFileSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);

export interface Message {
  id: string;
  from: string;
  subject: string;
  date: string;
  labels: string[];
}

export function isStarred(msg: Message): boolean {
  return msg.labels.includes("STARRED");
}

export function isUnread(msg: Message): boolean {
  return msg.labels.includes("UNREAD");
}

export function isInInbox(msg: Message): boolean {
  return msg.labels.includes("INBOX");
}

/**
 * Build the Gmail query string, reading exclude files.
 */
export function buildQuery(
  profile: string,
  extraExcludes: string[],
  excludesDir?: string
): string {
  const parts: string[] = [
    "(is:starred OR is:unread)",
    "in:inbox",
    "category:primary",
    "newer_than:7d",
  ];

  const dir = excludesDir ?? findExcludesDir();

  const addExcludes = (file: string) => {
    if (!existsSync(file)) return;
    const content = readFileSync(file, "utf-8");
    for (const raw of content.split("\n")) {
      const line = raw.split("#")[0].trim();
      if (line) parts.push(`-from:${line}`);
    }
  };

  addExcludes(join(dir, "global.txt"));
  addExcludes(join(dir, `${profile}.txt`));

  for (const pattern of extraExcludes) {
    if (pattern) parts.push(`-from:*${pattern}*`);
  }

  return parts.join(" ");
}

function findExcludesDir(): string {
  const env = process.env.GREAD_EXCLUDES_DIR;
  if (env && existsSync(env)) return env;

  const scriptDir = dirname(process.argv[1] ?? __dirname);
  const candidates = [
    join(scriptDir, "excludes"),
    join(scriptDir, "..", "share", "gread", "excludes"),
    join(process.env.HOME ?? "", "share", "gread", "excludes"),
  ];

  for (const c of candidates) {
    if (existsSync(c)) return c;
  }

  throw new Error(
    "gread: excludes directory not found. Set GREAD_EXCLUDES_DIR or install with 'make -C tools/gread install'"
  );
}

/**
 * Fetch messages via `gws gmail +triage --format json --labels`.
 * Synchronous — used only for initial load.
 */
export function fetchMessages(
  profile: string,
  query: string
): Message[] {
  const cmd = `${profile} gmail +triage --max 50 --format json --labels --query '${query.replace(/'/g, "'\\''")}'`;
  const raw = execFileSync("bash", ["-c", cmd], { encoding: "utf-8" });
  const data = JSON.parse(raw);
  return (data.messages ?? []).map((m: any) => ({
    id: m.id ?? "",
    from: m.from ?? "?",
    subject: m.subject ?? "",
    date: m.date ?? "",
    labels: m.labels ?? [],
  }));
}

/**
 * Fetch messages async — used for reloads after actions.
 */
export async function fetchMessagesAsync(
  profile: string,
  query: string
): Promise<Message[]> {
  const q = query.replace(/'/g, "'\\''");
  const { stdout } = await execFileAsync("bash", [
    "-c",
    `${profile} gmail +triage --max 50 --format json --labels --query '${q}'`,
  ]);
  const data = JSON.parse(stdout);
  return (data.messages ?? []).map((m: any) => ({
    id: m.id ?? "",
    from: m.from ?? "?",
    subject: m.subject ?? "",
    date: m.date ?? "",
    labels: m.labels ?? [],
  }));
}

async function msgModify(id: string, profile: string, body: object): Promise<void> {
  const json = JSON.stringify(body);
  await execFileAsync("bash", [
    "-c",
    `${profile} gmail users messages modify --params '{"userId":"me","id":"${id}"}' --json '${json.replace(/'/g, "'\\''")}' --format json`,
  ]);
}

export async function archive(id: string, profile: string): Promise<void> {
  await msgModify(id, profile, { removeLabelIds: ["INBOX"] });
}

export async function toggleStar(msg: Message, profile: string): Promise<void> {
  if (isStarred(msg)) {
    await msgModify(msg.id, profile, { removeLabelIds: ["STARRED"] });
  } else {
    await msgModify(msg.id, profile, { addLabelIds: ["STARRED"] });
  }
}

export async function markRead(id: string, profile: string): Promise<void> {
  await msgModify(id, profile, { removeLabelIds: ["UNREAD"] });
}

export async function markUnread(id: string, profile: string): Promise<void> {
  await msgModify(id, profile, { addLabelIds: ["UNREAD"] });
}

/**
 * Read a full email and return the text output.
 */
export function readEmail(id: string, profile: string): string {
  const raw = execFileSync("bash", [
    "-c",
    `${profile} gmail +read --id ${id} --headers --format text`,
  ], { encoding: "utf-8" });
  return raw;
}
