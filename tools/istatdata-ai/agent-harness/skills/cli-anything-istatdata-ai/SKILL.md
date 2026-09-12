---
name: cli-anything-istatdata-ai
description: >-
  Ask the ISTAT IstatData AI assistant a question in plain language and get back
  the matching statistical datasets, with resolved titles, category path, a deep
  link to the table and the SDMX download URLs. Use whenever someone asks where
  to find Italian official statistics on a topic — income, population,
  employment, road accidents, tourism, prices, health — or names a municipality,
  province or region and wants ISTAT data about it.
---

# cli-anything-istatdata-ai

Command line access to the AI search of the ISTAT Data Browser, the same form
served at `https://esploradati.istat.it/databrowser/#/it/dw/search?ai=true`.

The backend is public and needs no authentication. It answers with dataset ids
only: this harness joins them with the node catalogue so every result carries a
title, a breadcrumb, a working link to the table and the SDMX URLs.

## Installation

```bash
pip install -e tools/istatdata-ai/agent-harness
```

Two entry points are installed: `cli-anything-istatdata-ai` and the shorter
`istat-ask`. Python 3.9+, `click` is the only dependency.

## Usage

```bash
# One question, human-readable answer
istat-ask ask "qual è il reddito medio del comune di Bagheria"

# Machine-readable, for pipelines
istat-ask ask "incidenti stradali in Sicilia" --limit 5 --json | jq '.results[].url'

# Follow-up on the same conversation
istat-ask ask "e per le donne?" --session-id LafBBWBjvc7kz-7E-_ljU

# What the catalogue knows about one dataset
istat-ask dataset "IT1,DF_BES_TERRIT_4,1.0"

# Catalogue cache
istat-ask catalog info
istat-ask catalog refresh

# Conversational mode (also the default with no subcommand)
istat-ask repl
```

## Options that matter

- `--lang it|en` — sets the `UserLang` header. With `en` the backend leaves
  `title` and `ai_title` empty, so the readable title comes from the catalogue;
  the cache is keyed by language.
- `--limit N` — how many datasets to ask for. The node's own default is 20.
- `--session-id` — pass back the `session_id` of a previous answer to keep the
  conversation context.
- `--no-cache`, `--refresh-catalog` — control the 24 h catalogue cache in
  `${XDG_CACHE_HOME:-~/.cache}/istatdata-ai/`.

## JSON contract

`ask --json` prints `session_id`, `request`, `answer`, `count`, `conversation`
and `results`. Every result carries the same fixed keys:

`id`, `title`, `ai_title`, `category_path`, `description`, `similarity`,
`motivation`, `preview_enabled`, `url`, `reference_metadata_url`,
`sdmx_structure_url`, `sdmx_data_csv_url`, `in_catalog`.

`dataset --json` prints one such object.

## Exit codes

- `0` — answered, including when the answer is an empty result list
- `2` — backend error, or unknown dataset id
- `3` — rate limit

## Notes for agents

- The node declares a budget of 10 requests per 60 seconds. Ask serially, never
  fan out.
- `sdmx_data_csv_url` downloads the whole dataflow: for large tables that is
  slow and heavy. Narrow it with an SDMX key or `startPeriod`/`endPeriod`
  before fetching.
- `motivation` is a single letter (`I`, `S`, `T`, `A`) whose meaning is not
  documented anywhere in the application. Pass it through, do not interpret it.
- `suggested_questions` from the backend is dropped: it returns unresolved i18n
  keys, not questions.
- If the catalogue is unreachable, `ask` still answers: the warning goes to
  stderr, and the results come back with `url: null` and `in_catalog: false`.
