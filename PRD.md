# PRD — Andy Tools

## Status

Initial idea draft. The repository has not yet been initialized as an operational project.

## Idea

Create a personal repository to collect small tools developed over time to solve practical problems, automate repetitive tasks, or speed up everyday workflows.

The repo is intended as a simple, flexible, personal container: not as a structured public product, but as an organized space to save, document, and reuse useful tools.

## Problem

Daily work often creates small, recurring needs: conversions, checks, support scripts, data extraction, normalization, automation, or specific utilities.

Without a single place to store them, these solutions risk staying scattered and becoming hard to find or reuse.

## Goal

Have one repository to:

- collect small personal tools;
- make them easy to find;
- quickly document what they do and how to use them;
- reuse solutions that already exist;
- let the repo grow organically, without a structure that is too rigid at the beginning.

## Target audience

Primary user: the repository author.

Possible secondary users in the future:

- colleagues;
- collaborators;
- people with similar needs;
- anyone who finds a specific published tool useful.

## Initial scope

The repository may contain, for example:

- command-line scripts;
- small tools for data and files;
- utilities for conversions or data cleaning;
- personal automations;
- reusable snippets;
- independent mini-projects.

Each tool should ideally have a minimal description: what it does, when to use it, dependencies, and a usage example.

## Out of scope for now

At this stage, these are not priorities:

- formal packaging;
- publication on package managers;
- graphical interfaces;
- extensive documentation;
- complex architecture;
- guaranteed compatibility for external users.

## Guiding principles

- Simplicity first.
- Every tool must solve a concrete problem.
- Better to add little, but useful.
- Minimal documentation is part of the tool.
- The repo structure can evolve with real use.

## Possible future structure

Indicative, non-binding example:

```text
andy-tools/
├── README.md
├── PRD.md
├── tools/
│   ├── tool-name-1/
│   └── tool-name-2/
├── scripts/
└── docs/
```

## Success criteria

The repository will be useful if it:

- makes it possible to quickly find a tool that was already created;
- reduces repetitive work;
- makes it easier to turn a recurring need into a reusable script;
- remains simple to maintain;
- grows only when there is a real need.

## Open questions

- Will the tools mainly use Python, shell, Node.js, or mixed languages?
- Will each tool live in its own folder, or will some be simple standalone scripts?
- Will the repo remain personal, or could it become public and documented for others?
- Is a minimal convention needed for names, READMEs, and dependencies?
