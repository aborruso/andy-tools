import React, { useState, useEffect, useCallback, useRef } from "react";
import { Box, Text, useInput, useApp, useStdout } from "ink";
import {
  type Message,
  isStarred,
  isUnread,
  fetchMessages,
  fetchMessagesAsync,
  archive,
  toggleStar,
  markRead,
  markUnread,
  readEmail,
} from "./gmail.js";

interface AppProps {
  profile: string;
  query: string;
}

type Status = { text: string; color: string } | null;

export function App({ profile, query }: AppProps) {
  const { exit } = useApp();
  const { stdout } = useStdout();
  const [messages, setMessages] = useState<Message[]>([]);
  const [cursor, setCursor] = useState(0);
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState<Status>(null);
  const [reading, setReading] = useState<string | null>(null);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [pending, setPending] = useState(0);
  const busyRef = useRef(false);

  const termCols = stdout?.columns ?? 80;
  const termRows = stdout?.rows ?? 24;

  const HEADER_FOOTER = 5;
  const pageSize = Math.max(termRows - HEADER_FOOTER, 5);

  const reloadSync = useCallback(() => {
    setLoading(true);
    setStatus(null);
    setSelected(new Set());
    try {
      const msgs = fetchMessages(profile, query);
      setMessages(msgs);
      setCursor((prev) => Math.min(prev, Math.max(msgs.length - 1, 0)));
    } catch (e: any) {
      setStatus({ text: `Error: ${e.message}`, color: "red" });
    } finally {
      setLoading(false);
    }
  }, [profile, query]);

  const reloadAsync = useCallback(async () => {
    try {
      const msgs = await fetchMessagesAsync(profile, query);
      setMessages(msgs);
      setCursor((prev) => Math.min(prev, Math.max(msgs.length - 1, 0)));
      setSelected(new Set());
    } catch (e: any) {
      setStatus({ text: `Reload error: ${e.message}`, color: "red" });
    } finally {
      setPending((prev) => {
        const next = prev - 1;
        return next <= 0 ? 0 : next;
      });
    }
  }, [profile, query]);

  useEffect(() => {
    reloadSync();
  }, [reloadSync]);

  // Auto-reload when pending operations finish
  useEffect(() => {
    if (pending === 0 && busyRef.current) {
      busyRef.current = false;
      reloadAsync();
    }
  }, [pending, reloadAsync]);

  useEffect(() => {
    if (!status) return;
    const timer = setTimeout(() => setStatus(null), 3000);
    return () => clearTimeout(timer);
  }, [status]);

  const maxOffset = Math.max(messages.length - pageSize, 0);
  const clampedOffset = Math.min(offset, maxOffset);
  const visible = messages.slice(clampedOffset, clampedOffset + pageSize);

  const getTargets = (): Message[] => {
    if (selected.size > 0) {
      return messages.filter((m) => selected.has(m.id));
    }
    const msg = messages[cursor];
    return msg ? [msg] : [];
  };

  const runAction = (
    label: string,
    fn: (m: Message) => Promise<void>,
    removeFromView = false
  ) => {
    const targets = getTargets();
    if (targets.length === 0) return;
    const n = targets.length;

    // Remove acted-upon messages from view immediately (archive/read+archive)
    if (removeFromView) {
      const ids = new Set(targets.map((m) => m.id));
      setMessages((prev) => prev.filter((m) => !ids.has(m.id)));
      setCursor((c) => Math.min(c, Math.max(messages.length - n - 1, 0)));
    }

    setStatus({ text: `⏳ ${label} ${n} message${n > 1 ? "s" : ""}…`, color: "yellow" });
    setPending((prev) => prev + 1);
    busyRef.current = true;
    setSelected(new Set());

    // Run API calls in background
    (async () => {
      try {
        await Promise.all(targets.map((m) => fn(m)));
        setStatus({ text: `✓ ${label} ${n} message${n > 1 ? "s" : ""}`, color: "green" });
      } catch (e: any) {
        setStatus({ text: `Error: ${e.message}`, color: "red" });
      }
      setPending((prev) => {
        const next = prev - 1;
        if (next <= 0) {
          return 0;
        }
        return next;
      });
    })();
  };

  useInput((input, key) => {
    if (reading) {
      setReading(null);
      return;
    }

    // Ignore actions while operations are pending
    if (pending > 0 && !key.upArrow && !key.downArrow && input !== "k" && input !== "j" && input !== "q" && !key.escape && input !== " ") {
      setStatus({ text: `⏳ Wait for ${pending} pending operation${pending > 1 ? "s" : ""}…`, color: "yellow" });
      return;
    }

    if (key.upArrow || input === "k") {
      if (cursor > 0) {
        const newCursor = cursor - 1;
        setCursor(newCursor);
        if (newCursor < clampedOffset) {
          setOffset(clampedOffset - 1);
        }
      }
    } else if (key.downArrow || input === "j") {
      if (cursor < messages.length - 1) {
        const newCursor = cursor + 1;
        setCursor(newCursor);
        if (newCursor >= clampedOffset + pageSize) {
          setOffset(clampedOffset + 1);
        }
      }
    } else if (input === " ") {
      const msg = messages[cursor];
      if (msg) {
        setSelected((prev) => {
          const next = new Set(prev);
          if (next.has(msg.id)) {
            next.delete(msg.id);
          } else {
            next.add(msg.id);
          }
          return next;
        });
      }
    } else if (input === "a") {
      runAction("Archived", (m) => archive(m.id, profile), true);
    } else if (input === "x") {
      runAction(
        "Read & Archived",
        async (m) => {
          await markRead(m.id, profile);
          await archive(m.id, profile);
        },
        true
      );
    } else if (input === "s") {
      runAction("Toggled ★ on", (m) => toggleStar(m, profile));
    } else if (input === "r") {
      runAction("Marked as read", (m) => markRead(m.id, profile));
    } else if (input === "u") {
      runAction("Marked as unread", (m) => markUnread(m.id, profile));
    } else if (key.return) {
      const msg = messages[cursor];
      if (msg) {
        try {
          const body = readEmail(msg.id, profile);
          setReading(body);
        } catch (e: any) {
          setStatus({ text: `Error: ${e.message}`, color: "red" });
        }
      }
    } else if (input === "q" || key.escape) {
      exit();
    }
  });

  if (loading) {
    return <Text color="cyan">Loading messages…</Text>;
  }

  // Reading mode
  if (reading) {
    const lines = reading.split("\n").slice(0, termRows - 4);
    return (
      <Box flexDirection="column">
        <Box borderStyle="single" borderColor="gray" paddingX={1}>
          <Text dimColor>Press any key to go back</Text>
        </Box>
        {lines.map((line, i) => (
          <Text key={i}>{line}</Text>
        ))}
      </Box>
    );
  }

  // Column widths
  const CHECK_W = 1;
  const FLAGS_W = 3;
  const SEP = " │ ";
  const FROM_W = 28;
  const DATE_W = 11;
  const fixed = CHECK_W + 1 + FLAGS_W + SEP.length + FROM_W + SEP.length + DATE_W + SEP.length;
  const SUBJ_W = Math.max(termCols - fixed, 20);

  const pad = (s: string, w: number) => {
    const v = stripAnsi(s);
    if (v.length >= w) return s.slice(0, w - 1) + "…";
    return s + " ".repeat(w - v.length);
  };

  const selCount = selected.size;

  return (
    <Box flexDirection="column">
      {/* Header */}
      <Box>
        <Text bold color="cyan">{"gread " + profile}</Text>
        <Text color="gray">{" — "}</Text>
        <Text dimColor>
          {messages.length} message{messages.length !== 1 ? "s" : ""}
        </Text>
        <Text color="gray">{"  "}</Text>
        <Text dimColor>
          {cursor + 1}/{messages.length}
        </Text>
        {selCount > 0 && (
          <>
            <Text color="gray">{"  "}</Text>
            <Text color="yellow">{selCount} selected</Text>
          </>
        )}
        {pending > 0 && (
          <>
            <Text color="gray">{"  "}</Text>
            <Text color="yellow">⏳ {pending} pending</Text>
          </>
        )}
      </Box>

      {/* Message list */}
      <Box flexDirection="column">
        {visible.map((msg, i) => {
          const realIndex = clampedOffset + i;
          const isCursorHere = realIndex === cursor;
          const isChecked = selected.has(msg.id);
          const star = isStarred(msg) ? "★" : " ";
          const read = isUnread(msg) ? "●" : "○";
          const check = isChecked ? "☑" : " ";

          const flags = `${star} ${read}`;
          const from = truncate(stripAnsi(msg.from), FROM_W);
          const date = formatDate(msg.date);
          const subj = truncate(msg.subject, SUBJ_W);

          const line = `${check} ${flags}${SEP}${pad(from, FROM_W)}${SEP}${pad(date, DATE_W)}${SEP}${subj}`;

          if (isCursorHere) {
            const padded = padToWidth(line, termCols);
            return (
              <Text key={msg.id} backgroundColor="gray" color="white" bold>
                {padded}
              </Text>
            );
          }

          if (isChecked) {
            return (
              <Text key={msg.id} backgroundColor="#333" color="yellow">
                {line}
              </Text>
            );
          }

          return (
            <Text key={msg.id}>
              {line}
            </Text>
          );
        })}
        {/* Fill remaining rows */}
        {Array.from({ length: Math.max(pageSize - visible.length, 0) }).map((_, i) => (
          <Text key={`empty-${i}`}>{" ".repeat(termCols)}</Text>
        ))}
      </Box>

      {/* Footer */}
      <Box borderStyle="single" borderColor="gray" paddingX={1}>
        {status ? (
          <Text color={status.color}>{status.text}</Text>
        ) : (
          <Text dimColor>
            ↑/k ↓/j • Space=select • Enter=read • a=archive • x=read+archive • s=★ • r=read • u=unread • q=quit
          </Text>
        )}
      </Box>
    </Box>
  );
}

function truncate(s: string, max: number): string {
  if (s.length <= max) return s;
  return s.slice(0, max - 1) + "…";
}

function formatDate(s: string): string {
  const m = s.match(/\d{1,2}\s+[A-Za-z]+\s+\d{4}\s+(\d{1,2}):(\d{2})/);
  if (!m) return s.slice(0, 11);
  const dayMonth = s.match(/(\d{1,2}\s+[A-Za-z]+)/);
  return `${dayMonth?.[1] ?? ""} ${m[1]}:${m[2]}`;
}

function stripAnsi(s: string): string {
  return s.replace(/\x1b\[[0-9;]*m/g, "");
}

function padToWidth(s: string, w: number): string {
  const visible = stripAnsi(s);
  const diff = w - visible.length;
  if (diff <= 0) return s;
  return s + " ".repeat(diff);
}
