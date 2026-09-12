"""istat-ask — command line access to the IstatData AI assistant.

Same job as the web form at
https://esploradati.istat.it/databrowser/#/it/dw/search?ai=true : a question in
plain language, a ranked list of ISTAT datasets in return.
"""

import json
import sys

import click

from cli_anything.istatdata_ai.core import api, catalog as catalog_mod, enrich as enrich_mod
from cli_anything.istatdata_ai.utils.repl_skin import ReplSkin

__version__ = "1.0.0"

EXIT_OK = 0
EXIT_API_ERROR = 2
EXIT_RATE_LIMIT = 3


def _skin():
    """ReplSkin, unmodified, with the install line pointing at this repository."""
    skin = ReplSkin("istatdata_ai", version=__version__)
    skin.skill_install_cmd = "pip install -e tools/istatdata-ai/agent-harness"
    if skin.skill_path:
        skin.global_skill_path = skin.skill_path
    return skin


def _client(ctx):
    return api.Client(base_url=ctx.obj["base_url"], node=ctx.obj["node"],
                      lang=ctx.obj["lang"], timeout=ctx.obj["timeout"])


def _index(ctx, client, refresh=False):
    cat, _ = catalog_mod.load(client, refresh=refresh, use_cache=ctx.obj["use_cache"])
    return catalog_mod.build_index(cat)


def _index_or_empty(ctx, client, refresh=False):
    """Same, but a catalogue failure must not cost the user the answer.

    Without the catalogue the results lose the title fallback, the category
    path and the table link, but the search itself still works.
    """
    try:
        return _index(ctx, client, refresh=refresh)
    except api.ApiError as exc:
        # stderr, so it never lands inside a --json payload
        click.echo(f"warning: catalogue unavailable ({exc}): "
                   "results will have no title or link", err=True)
        return {}


def _fail(skin, exc):
    if isinstance(exc, api.RateLimitError):
        skin.error(f"rate limit: {exc}")
        return EXIT_RATE_LIMIT
    skin.error(str(exc))
    return EXIT_API_ERROR


def _print_results(skin, payload, show_description, show_links):
    if not payload["results"]:
        skin.warning("no dataset returned for this question")
        return
    skin.info(payload["answer"] or "")
    skin.section(f"{payload['count']} dataset")
    for pos, item in enumerate(payload["results"], 1):
        title = item["title"] or item["id"]
        click.echo(f"\n{pos:>2}. {title}")
        if item["ai_title"] and item["ai_title"] != title:
            click.echo(f"    {item['ai_title']}")
        if item["category_path"]:
            click.echo(f"    {' > '.join(item['category_path'])}")
        click.echo(f"    id: {item['id']}")
        if show_description and item["description"]:
            for line in item["description"].splitlines():
                if line.strip():
                    click.echo(f"    {line.strip()}")
        if show_links:
            if item["url"]:
                click.echo(f"    tavola:  {item['url']}")
            if item["sdmx_data_csv_url"]:
                click.echo(f"    dati:    {item['sdmx_data_csv_url']}")


@click.group(invoke_without_command=True)
@click.option("--lang", default=api.DEFAULT_LANG, show_default=True,
              type=click.Choice(["it", "en"]),
              help="Language of titles and descriptions (UserLang header).")
@click.option("--node", default=api.DEFAULT_NODE, show_default=True, type=int,
              help="Data Browser node id.")
@click.option("--node-code", default=enrich_mod.DEFAULT_NODE_CODE, show_default=True,
              help="Node code used in the browser deep links.")
@click.option("--base-url", default=api.DEFAULT_BASE_URL, show_default=True,
              help="Data Browser hub API base URL.")
@click.option("--timeout", default=60, show_default=True, type=int,
              help="HTTP timeout in seconds.")
@click.option("--no-cache", is_flag=True, help="Never read or write the catalogue cache.")
@click.version_option(__version__, prog_name="istat-ask")
@click.pass_context
def cli(ctx, lang, node, node_code, base_url, timeout, no_cache):
    """Ask IstatData in plain language and get the matching datasets."""
    ctx.ensure_object(dict)
    ctx.obj.update(lang=lang, node=node, node_code=node_code, base_url=base_url,
                   timeout=timeout, use_cache=not no_cache)
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


@cli.command()
@click.argument("question", nargs=-1, required=True)
@click.option("--limit", default=api.DEFAULT_MAX_RESULTS, show_default=True, type=int,
              help="Maximum number of datasets to ask for.")
@click.option("--session-id", default=None,
              help="Session id of a previous answer, to keep the conversation context.")
@click.option("--json", "as_json", is_flag=True, help="Machine-readable output.")
@click.option("--no-description", is_flag=True, help="Hide the dataset descriptions.")
@click.option("--no-links", is_flag=True, help="Hide the table and data links.")
@click.option("--refresh-catalog", is_flag=True, help="Refetch the catalogue before answering.")
@click.pass_context
def ask(ctx, question, limit, session_id, as_json, no_description, no_links, refresh_catalog):
    """Ask a QUESTION and list the datasets the assistant proposes."""
    skin = _skin()
    text = " ".join(question).strip()
    client = _client(ctx)
    index = _index_or_empty(ctx, client, refresh=refresh_catalog)
    try:
        answer = client.execute_search(text, session_id=session_id, max_results=limit)
    except api.ApiError as exc:
        sys.exit(_fail(skin, exc))

    payload = enrich_mod.enrich_answer(
        answer, index, lang=ctx.obj["lang"],
        sdmx_base=enrich_mod.DEFAULT_SDMX_BASE, node_code=ctx.obj["node_code"])
    if as_json:
        click.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_results(skin, payload, not no_description, not no_links)
    sys.exit(EXIT_OK)


@cli.command()
@click.argument("dataset_id")
@click.option("--json", "as_json", is_flag=True, help="Machine-readable output.")
@click.pass_context
def dataset(ctx, dataset_id, as_json):
    """Show what the catalogue knows about DATASET_ID."""
    skin = _skin()
    client = _client(ctx)
    try:
        index = _index(ctx, client)
    except api.ApiError as exc:
        sys.exit(_fail(skin, exc))

    if dataset_id not in index:
        skin.error(f"{dataset_id} is not in the catalogue of node {ctx.obj['node']}")
        sys.exit(EXIT_API_ERROR)
    item = enrich_mod.enrich({"id": dataset_id}, index, lang=ctx.obj["lang"],
                             node_code=ctx.obj["node_code"])
    if as_json:
        click.echo(json.dumps(item, ensure_ascii=False, indent=2))
    else:
        skin.section(item["title"] or dataset_id)
        block = {"id": item["id"], "categorie": " > ".join(item["category_path"])}
        if item["url"]:
            block["tavola"] = item["url"]
        if item["reference_metadata_url"]:
            block["metadati"] = item["reference_metadata_url"]
        block["sdmx struttura"] = item["sdmx_structure_url"] or ""
        block["sdmx dati csv"] = item["sdmx_data_csv_url"] or ""
        skin.status_block(block)
    sys.exit(EXIT_OK)


@cli.group()
def catalog():
    """Inspect or refresh the cached node catalogue."""


@catalog.command("info")
@click.option("--json", "as_json", is_flag=True, help="Machine-readable output.")
@click.pass_context
def catalog_info(ctx, as_json):
    """Show the state of the catalogue cache."""
    skin = _skin()
    info = catalog_mod.cache_info(ctx.obj["node"], ctx.obj["lang"])
    if as_json:
        click.echo(json.dumps(info, ensure_ascii=False, indent=2))
    else:
        skin.status_block({k: str(v) for k, v in info.items()})
    sys.exit(EXIT_OK)


@catalog.command("refresh")
@click.pass_context
def catalog_refresh(ctx):
    """Refetch the catalogue and rewrite the cache."""
    skin = _skin()
    client = _client(ctx)
    try:
        cat, _ = catalog_mod.load(client, refresh=True, use_cache=True)
    except api.ApiError as exc:
        sys.exit(_fail(skin, exc))
    skin.success(f"{len(cat.get('datasetMap') or {})} dataset in cache "
                 f"({catalog_mod.cache_path(ctx.obj['node'], ctx.obj['lang'])})")
    sys.exit(EXIT_OK)


@cli.command()
@click.option("--limit", default=api.DEFAULT_MAX_RESULTS, show_default=True, type=int,
              help="Maximum number of datasets per question.")
@click.pass_context
def repl(ctx, limit=api.DEFAULT_MAX_RESULTS):
    """Conversational mode: follow-up questions keep the session context."""
    skin = _skin()
    skin.print_banner()
    skin.hint("Ask a question. `new` starts a new conversation, `quit` exits.")
    client = _client(ctx)
    index = _index_or_empty(ctx, client)

    session_id = None
    while True:
        try:
            line = input(skin.prompt(project_name=session_id or "new")).strip()
        except (EOFError, KeyboardInterrupt):
            click.echo()
            break
        if not line:
            continue
        if line in {"quit", "exit", ":q"}:
            break
        if line == "new":
            session_id = None
            skin.info("new conversation")
            continue
        try:
            answer = client.execute_search(line, session_id=session_id, max_results=limit)
        except api.ApiError as exc:
            _fail(skin, exc)
            continue
        session_id = answer.get("session_id") or session_id
        payload = enrich_mod.enrich_answer(answer, index, lang=ctx.obj["lang"],
                                           node_code=ctx.obj["node_code"])
        _print_results(skin, payload, True, True)
    skin.print_goodbye()
    sys.exit(EXIT_OK)


def main():
    cli(obj={})


if __name__ == "__main__":
    main()
