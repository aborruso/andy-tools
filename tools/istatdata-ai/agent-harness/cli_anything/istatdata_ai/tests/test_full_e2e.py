"""Live tests against the real IstatData backend.

Skipped unless ISTATDATA_AI_LIVE=1. The node declares a budget of 10 requests
per 60 seconds, so the whole module stays well under a dozen calls and never
runs them in parallel.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

import pytest

from cli_anything.istatdata_ai.core import api, catalog as catalog_mod, enrich as enrich_mod

LIVE = os.environ.get("ISTATDATA_AI_LIVE") == "1"
pytestmark = pytest.mark.skipif(not LIVE, reason="set ISTATDATA_AI_LIVE=1 to run live tests")


def _resolve_cli(name="cli-anything-istatdata-ai"):
    """Locate the installed console script, no hardcoded paths, no CWD games."""
    found = shutil.which(name)
    if found:
        return [found]
    sibling = os.path.join(os.path.dirname(sys.executable), name)
    if os.path.exists(sibling):
        return [sibling]
    if os.environ.get("CLI_ANYTHING_FORCE_INSTALLED") == "1":
        pytest.fail(f"{name} is not installed but CLI_ANYTHING_FORCE_INSTALLED=1")
    return [sys.executable, "-m", "cli_anything.istatdata_ai"]


@pytest.fixture(scope="module")
def client():
    return api.Client(lang="it")


@pytest.fixture(scope="module")
def index(client):
    cat, _ = catalog_mod.load(client, refresh=True, use_cache=True)
    return catalog_mod.build_index(cat)


@pytest.fixture(scope="module")
def first_answer(client):
    return client.execute_search("quanti sono gli occupati in Sicilia", max_results=10)


def test_live_search_returns_usable_results(first_answer, index):
    payload = enrich_mod.enrich_answer(first_answer, index)
    assert payload["count"] > 0
    top = payload["results"][0]
    assert top["title"]
    assert top["url"] and top["url"].startswith("https://esploradati.istat.it/databrowser/#/it/dw/")
    assert top["sdmx_data_csv_url"]


def test_live_every_id_is_in_the_catalogue(first_answer, index):
    ids = [p["id"] for p in first_answer["chatContext"]["dataproducts"]]
    missing = [i for i in ids if i not in index]
    assert missing == [], f"ids returned by the AI but absent from the catalogue: {missing}"


def test_live_session_round_trip(client, first_answer):
    session_id = first_answer["session_id"]
    assert session_id
    second = client.execute_search("e per le donne?", session_id=session_id, max_results=5)
    assert second["session_id"] == session_id
    assert len(second["chatContext"]["conversation"]) == 4


class TestCLISubprocess:
    """Exercise the installed command from an unrelated working directory."""

    @staticmethod
    def _run(args, **kwargs):
        with tempfile.TemporaryDirectory() as cwd:
            return subprocess.run(_resolve_cli() + args, cwd=cwd, capture_output=True,
                                  text=True, timeout=180, **kwargs)

    def test_help(self):
        proc = self._run(["--help"])
        assert proc.returncode == 0
        assert "ask" in proc.stdout

    def test_version(self):
        proc = self._run(["--version"])
        assert proc.returncode == 0

    def test_ask_json(self):
        proc = self._run(["ask", "incidenti stradali", "--limit", "3", "--json"])
        assert proc.returncode == 0, proc.stderr
        payload = json.loads(proc.stdout)
        assert payload["count"] == 3
        assert all(item["title"] for item in payload["results"])
        assert all(item["url"] for item in payload["results"])

    def test_catalog_info_json(self):
        proc = self._run(["catalog", "info", "--json"])
        assert proc.returncode == 0, proc.stderr
        info = json.loads(proc.stdout)
        assert "path" in info and "exists" in info

    def test_dataset_json(self):
        proc = self._run(["dataset", "IT1,DF_BES_TERRIT_4,1.0", "--json"])
        assert proc.returncode == 0, proc.stderr
        item = json.loads(proc.stdout)
        assert item["id"] == "IT1,DF_BES_TERRIT_4,1.0"
        assert item["title"]
        assert item["url"]

    def test_unknown_dataset_exits_with_api_error(self):
        proc = self._run(["dataset", "IT1,NOPE_NOT_A_DATASET,1.0"])
        assert proc.returncode == 2
