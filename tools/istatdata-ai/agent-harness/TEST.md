# TEST — istatdata-ai

## What is under test

The harness wraps a public read-only backend. There is no state to mutate, so
the whole surface is: build a request, parse an answer, join it with the node
catalogue, build links, print.

Two suites:

- `tests/test_core.py` — offline, over saved fixtures. Always runs.
- `tests/test_full_e2e.py` — live, against the real ISTAT backend. Skipped
  unless `ISTATDATA_AI_LIVE=1` is set, because the node declares a budget of 10
  requests per 60 seconds and the suite must not be hostage to the network.

## Fixtures

- `tests/fixtures/execute_search_it.json` — a real `ExecuteSearch` answer
  (`UserLang: it`, question "qual è il reddito medio del comune di Bagheria",
  5 results). With `UserLang: en` the same call comes back with `title` and
  `ai_title` empty, which is what makes the catalogue join load-bearing.
- `tests/fixtures/catalog_small.json` — the node catalogue pruned to the five
  dataset ids of that answer, keeping the real category tree above them.

## Unit test plan (`test_core.py`)

1. `build_index` maps every dataset id in `datasetMap` to a title.
2. `build_index` puts the category group id first in `category_ids` — this is
   what makes the deep link resolve.
3. `split_id` splits `agency,id,version` and returns `None` on a malformed id.
4. `browser_url` reproduces, character by character, the URL verified by hand in
   the browser for `IT1,30_1008_DF_MEF_REDDITIIRPEF_COM_2,1.0`.
5. `browser_url` returns `None` when the category path is unknown, instead of
   emitting a link that lands on "page not available".
6. `sdmx_urls` builds the structure and CSV-data URLs in the verified shape.
7. `enrich_answer` fills every documented key for every result, with no
   missing-versus-null wobble.
8. Blanking `title`/`ai_title` in the fixture — the shape `UserLang: en`
   returns — still yields a readable title for every result, from the catalogue.
9. `ai_title` is kept when the backend provides it, and differs from `title`.
10. `enrich` keeps `motivation` as the raw single letter.
11. The catalogue cache writes atomically, is reread within the TTL without
    touching the network, and is bypassed by `use_cache=False`.
12. `cache_info` reports a missing cache without raising.
13. An `errorCode` payload becomes an `ApiError`, not a traceback; a rate-limit
    code becomes a `RateLimitError`.
14. Every outgoing request carries `aiRateLimiting`, the requested
    `aiSearchMaxResults`, `action: {type: query}` and the `UserLang` header.
15. `ask` still answers when the catalogue is unreachable: exit 0, results with
    `url: null` and `in_catalog: false`, and the warning on stderr so it never
    lands inside a `--json` payload.

## E2E test plan (`test_full_e2e.py`, live)

1. A real `ask` returns at least one result, with a resolved title and a
   non-null table URL.
2. The `session_id` round trip: a second question sent with the id of the first
   comes back with the same id and a four-turn conversation.
3. Every id returned by a live query is present in the live catalogue (the join
   is the whole deliverable; a miss would mean silently untitled results).
4. `TestCLISubprocess`: the installed command resolved through `_resolve_cli()`
   answers `--help`, `--version`, `ask --json`, `catalog info --json` and
   `dataset --json` with exit code 0 and parseable JSON, from a working
   directory unrelated to the source tree.

## Results

Run on 2026-08-24, Python 3.13.9, from `tools/istatdata-ai/agent-harness`.

Offline suite:

```
$ .venv/bin/python -m pytest cli_anything/istatdata_ai/tests/test_core.py -q --tb=no
22 passed in 0.05s
```

Live suite (`ISTATDATA_AI_LIVE=1`, real backend, installed command):

```
$ PATH="$PWD/.venv/bin:$PATH" CLI_ANYTHING_FORCE_INSTALLED=1 ISTATDATA_AI_LIVE=1 \
    .venv/bin/python -m pytest cli_anything/istatdata_ai/tests -q --tb=no
31 passed in 15.15s
```

## Coverage gaps

- `POST nodes/{node}/AI/GeneratePreview` is not wrapped: its payload was not
  reverse engineered, so nothing about the data preview is tested.
- The `motivation` letter is passed through untested for meaning, because its
  meaning is not documented anywhere in the application bundle.
- `suggested_questions` is deliberately dropped: the backend returns unresolved
  i18n keys (`["ISTAT1","ISTAT2","ISTAT3"]`), not questions.
- Rate limiting is honoured only by not fanning out; a real 429 has never been
  observed, so the `RateLimitError` branch is exercised on a synthetic payload
  only.
