# cli_anything.istatdata_ai

CLI-Anything harness around the AI search of the ISTAT Data Browser.

## Layout

- `core/api.py` — the HTTP client: `ExecuteSearch` and the node catalogue.
- `core/catalog.py` — catalogue cache on disk and the id → title/category index.
- `core/enrich.py` — joins an AI answer with the catalogue and builds the links.
- `istatdata_ai_cli.py` — the Click CLI (`ask`, `dataset`, `catalog`, `repl`).
- `utils/repl_skin.py` — the shared CLI-Anything terminal skin, unmodified.
- `../../ISTATDATA_AI.md` — what the backend does and how it was verified.
- `../../TEST.md` — test plan and results.

## Deviation from the CLI-Anything harness specification

The specification prescribes a session state model with undo/redo, auto-saved
one-shot mutations, `--dry-run` and locked session-file writes. This target is a
read-only public search: there is no mutable state, nothing to undo and nothing
to lock, so none of that machinery is implemented. What is kept: Click
subcommands, REPL as the default mode, `--json` output, the
`cli-anything-istatdata-ai` console script, `TEST.md` written before the tests,
and the packaged `skills/SKILL.md`.

Second deviation: the harness lives under `tools/istatdata-ai/` instead of a
top-level `<software>/agent-harness/`, so it fits the tools table of this
repository.
