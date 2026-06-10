#!/usr/bin/env node
import React from "react";
import { render } from "ink";
import { App } from "./ui.js";
import { buildQuery } from "./gmail.js";

const args = process.argv.slice(2);

if (args.includes("--help") || args.includes("-h")) {
  console.log(`Usage:
  gread <profile> [--exclude "pec,bic,cip"]
  gread --help

Profiles: gws, gwsb

Keyboard shortcuts (inside the TUI):
  ↑/k  Navigate up
  ↓/j  Navigate down
  Space  Toggle selection
  Enter  Read email
  a    Archive selected (or cursor)
  s    Toggle star ★ on selected (or cursor)
  r    Mark selected as read (or cursor)
  u    Mark selected as unread (or cursor)
  x    Mark as read + archive selected (or cursor)
  q    Quit

Options:
  -x, --exclude CSV   Additional comma-separated exclude patterns.
`);
  process.exit(0);
}

let profile = "";
let extraExcludes: string[] = [];

for (let i = 0; i < args.length; i++) {
  if (args[i] === "-x" || args[i] === "--exclude") {
    const csv = args[++i] ?? "";
    extraExcludes = csv.split(",").map((s) => s.trim()).filter(Boolean);
  } else if (args[i] === "gws" || args[i] === "gwsb") {
    profile = args[i];
  } else {
    console.error(`gread: unknown argument '${args[i]}'`);
    process.exit(2);
  }
}

if (!profile) {
  console.error("gread: specify a profile (gws or gwsb)");
  process.exit(2);
}

const query = buildQuery(profile, extraExcludes);
render(React.createElement(App, { profile, query }));
