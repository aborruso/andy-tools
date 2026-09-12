"""Offline unit tests over saved fixtures. No network."""

import json
import os
from pathlib import Path

import pytest

from cli_anything.istatdata_ai.core import api, catalog as catalog_mod, enrich as enrich_mod

FIXTURES = Path(__file__).parent / "fixtures"
BAGHERIA = "IT1,30_1008_DF_MEF_REDDITIIRPEF_COM_2,1.0"
# Verified by hand in the browser: this exact URL opens the table.
BAGHERIA_URL = ("https://esploradati.istat.it/databrowser/#/it/dw/categories/"
                "IT1,HOU,1.0/MEF_REDDITIIRPEF_COM/"
                "IT1,30_1008_DF_MEF_REDDITIIRPEF_COM_2,1.0")


@pytest.fixture(scope="module")
def catalog():
    with open(FIXTURES / "catalog_small.json", encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def index(catalog):
    return catalog_mod.build_index(catalog)


@pytest.fixture(scope="module")
def answer():
    with open(FIXTURES / "execute_search_it.json", encoding="utf-8") as fh:
        return json.load(fh)


def test_index_titles_every_dataset(catalog, index):
    for dataset_id in catalog["datasetMap"]:
        assert index[dataset_id]["title"]


def test_index_path_starts_with_group_id(index):
    assert index[BAGHERIA]["category_ids"][0] == "IT1,HOU,1.0"
    assert index[BAGHERIA]["category_ids"][-1] == "MEF_REDDITIIRPEF_COM"


def test_index_labels_match_ids_depth(index):
    entry = index[BAGHERIA]
    assert len(entry["category_labels"]) == len(entry["category_ids"])


def test_split_id():
    assert enrich_mod.split_id(BAGHERIA) == ("IT1", "30_1008_DF_MEF_REDDITIIRPEF_COM_2", "1.0")


def test_split_id_malformed():
    assert enrich_mod.split_id("not-a-dataset-id") is None


def test_browser_url_matches_verified_link(index):
    url = enrich_mod.browser_url(BAGHERIA, index[BAGHERIA]["category_ids"], "it")
    assert url == BAGHERIA_URL


def test_browser_url_without_category_is_none():
    assert enrich_mod.browser_url(BAGHERIA, [], "it") is None


def test_sdmx_urls():
    urls = enrich_mod.sdmx_urls(BAGHERIA)
    assert urls["structure"] == (
        "https://esploradati.istat.it/SDMXWS/rest/dataflow/IT1/"
        "30_1008_DF_MEF_REDDITIIRPEF_COM_2/1.0?references=all")
    assert urls["data_csv"] == (
        "https://esploradati.istat.it/SDMXWS/rest/data/"
        "IT1,30_1008_DF_MEF_REDDITIIRPEF_COM_2,1.0/?format=csv")


def test_sdmx_urls_malformed_id():
    assert enrich_mod.sdmx_urls("nope") == {"structure": None, "data_csv": None}


EXPECTED_KEYS = {
    "id", "title", "ai_title", "category_path", "description", "similarity", "motivation",
    "preview_enabled", "url", "reference_metadata_url", "sdmx_structure_url",
    "sdmx_data_csv_url", "in_catalog",
}


def test_enrich_answer_shape(answer, index):
    payload = enrich_mod.enrich_answer(answer, index)
    assert payload["count"] == len(payload["results"]) == 5
    assert payload["session_id"]
    for item in payload["results"]:
        assert set(item) == EXPECTED_KEYS


def test_titles_come_from_the_catalogue_when_the_api_omits_them(answer, index):
    """With UserLang=en the backend returns empty titles; the join must cover."""
    blanked = json.loads(json.dumps(answer))
    for product in blanked["chatContext"]["dataproducts"]:
        product["title"] = ""
        product["ai_title"] = ""
    payload = enrich_mod.enrich_answer(blanked, index)
    assert all(item["title"] for item in payload["results"])
    assert all(item["ai_title"] == "" for item in payload["results"])


def test_ai_title_is_kept_when_present(answer, index):
    payload = enrich_mod.enrich_answer(answer, index)
    raw = answer["chatContext"]["dataproducts"]
    assert payload["results"][0]["ai_title"] == raw[0]["ai_title"]
    assert payload["results"][0]["ai_title"] != payload["results"][0]["title"]


def test_enrich_answer_first_result_is_the_verified_one(answer, index):
    payload = enrich_mod.enrich_answer(answer, index)
    first = payload["results"][0]
    assert first["id"] == BAGHERIA
    assert first["url"] == BAGHERIA_URL
    assert first["in_catalog"] is True


def test_motivation_passed_through_raw(answer, index):
    payload = enrich_mod.enrich_answer(answer, index)
    assert payload["results"][0]["motivation"] == answer["chatContext"]["dataproducts"][0]["motivation"]


class _FakeClient:
    """Stands in for api.Client; counts how often the network would be hit."""

    def __init__(self, catalog, node=1, lang="it"):
        self._catalog = catalog
        self.node = node
        self.lang = lang
        self.calls = 0

    def fetch_catalog(self):
        self.calls += 1
        return self._catalog


def test_cache_roundtrip(catalog, tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    client = _FakeClient(catalog)
    first, from_cache = catalog_mod.load(client)
    assert from_cache is False and client.calls == 1
    second, from_cache = catalog_mod.load(client)
    assert from_cache is True and client.calls == 1
    assert first["datasetMap"] == second["datasetMap"]


def test_cache_refresh_forces_fetch(catalog, tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    client = _FakeClient(catalog)
    catalog_mod.load(client)
    catalog_mod.load(client, refresh=True)
    assert client.calls == 2


def test_no_cache_leaves_no_file(catalog, tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    client = _FakeClient(catalog)
    catalog_mod.load(client, use_cache=False)
    assert not catalog_mod.cache_path(1, "it").exists()


def test_cache_info_when_missing(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    info = catalog_mod.cache_info(1, "it")
    assert info["exists"] is False and info["age_seconds"] is None


def test_error_payload_becomes_api_error(monkeypatch):
    class _Resp:
        status = 200

        def read(self):
            return json.dumps({"errorCode": "INTERNAL_ERROR_SERVER", "message": ""}).encode()

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **k: _Resp())
    with pytest.raises(api.ApiError) as excinfo:
        api.Client().execute_search("qualcosa")
    assert excinfo.value.code == "INTERNAL_ERROR_SERVER"


def test_rate_limit_payload_becomes_rate_limit_error(monkeypatch):
    class _Resp:
        status = 200

        def read(self):
            return json.dumps({"errorCode": "RATE_LIMIT_EXCEEDED", "message": "slow down"}).encode()

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **k: _Resp())
    with pytest.raises(api.RateLimitError):
        api.Client().execute_search("qualcosa")


def test_rate_limiting_block_is_always_sent(monkeypatch):
    captured = {}

    class _Resp:
        status = 200

        def read(self):
            return json.dumps({"session_id": "x", "request": "q", "response": "",
                               "chatContext": {"conversation": [], "dataproducts": []}}).encode()

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def _urlopen(req, timeout=None):
        captured["body"] = json.loads(req.data.decode("utf-8"))
        captured["headers"] = dict(req.headers)
        return _Resp()

    monkeypatch.setattr("urllib.request.urlopen", _urlopen)
    api.Client(lang="it").execute_search("domanda", max_results=7)
    assert captured["body"]["aiRateLimiting"] == api.RATE_LIMITING
    assert captured["body"]["aiSearchMaxResults"] == 7
    assert captured["body"]["action"] == {"type": "query"}
    # urllib title-cases header names
    assert captured["headers"]["Userlang"] == "it"


def test_ask_still_answers_when_the_catalogue_is_unreachable(answer, tmp_path, monkeypatch):
    """A catalogue outage must cost the links, not the answer."""
    from click.testing import CliRunner

    from cli_anything.istatdata_ai import istatdata_ai_cli as cli_mod

    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    monkeypatch.setattr(api.Client, "fetch_catalog",
                        lambda self: (_ for _ in ()).throw(api.ApiError("catalogue down")))
    monkeypatch.setattr(api.Client, "execute_search",
                        lambda self, request, session_id=None, max_results=20: answer)

    result = CliRunner().invoke(cli_mod.cli, ["ask", "reddito", "--json"], obj={})
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["count"] == 5
    assert all(item["url"] is None for item in payload["results"])
    assert all(item["in_catalog"] is False for item in payload["results"])
    # With UserLang=it the backend fills `title` itself, so it survives.
    assert all(item["title"] for item in payload["results"])
