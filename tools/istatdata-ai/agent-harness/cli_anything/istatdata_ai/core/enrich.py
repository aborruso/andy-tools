"""Turn a raw AI dataproduct into something a human or an agent can act on.

The AI endpoint answers with dataset ids only. Titles and category paths come
from the node catalogue; the links are built from the id.
"""

from urllib.parse import quote

DEFAULT_BROWSER_BASE = "https://esploradati.istat.it/databrowser/"
DEFAULT_SDMX_BASE = "https://esploradati.istat.it/SDMXWS/rest/"
DEFAULT_NODE_CODE = "dw"


def split_id(dataset_id):
    """`IT1,30_1008_DF_MEF_REDDITIIRPEF_COM_2,1.0` -> (agency, id, version)."""
    parts = dataset_id.split(",")
    if len(parts) != 3:
        return None
    return parts[0], parts[1], parts[2]


def browser_url(dataset_id, category_ids, lang="it",
                base=DEFAULT_BROWSER_BASE, node_code=DEFAULT_NODE_CODE):
    """Deep link to the table inside the Data Browser.

    The category path is required: without it the app answers "the requested
    page is not available".
    """
    if not category_ids:
        return None
    path = "/".join(category_ids + [dataset_id])
    return f"{base}#/{lang}/{node_code}/categories/{path}"


def sdmx_urls(dataset_id, base=DEFAULT_SDMX_BASE):
    """Structure and data URLs on the ISTAT SDMX web service."""
    ref = split_id(dataset_id)
    if not ref:
        return {"structure": None, "data_csv": None}
    agency, flow, version = ref
    return {
        "structure": f"{base}dataflow/{quote(agency)}/{quote(flow)}/{quote(version)}?references=all",
        "data_csv": f"{base}data/{quote(dataset_id, safe=',')}/?format=csv",
    }


def enrich(dataproduct, index, lang="it", browser_base=DEFAULT_BROWSER_BASE,
           sdmx_base=DEFAULT_SDMX_BASE, node_code=DEFAULT_NODE_CODE):
    dataset_id = dataproduct.get("id") or ""
    meta = index.get(dataset_id, {})
    category_ids = meta.get("category_ids") or []
    links = sdmx_urls(dataset_id, sdmx_base)
    return {
        "id": dataset_id,
        "title": meta.get("title") or dataproduct.get("title") or "",
        # AI-written descriptive title. The backend fills it (and `title`) only
        # when UserLang is `it`; with `en` both come back empty, which is why
        # the readable title is taken from the catalogue instead.
        "ai_title": dataproduct.get("ai_title") or "",
        "category_path": meta.get("category_labels") or [],
        "description": (dataproduct.get("description") or "").strip(),
        "similarity": dataproduct.get("similarity"),
        # Single-letter code (I/S/T/A) returned by the backend; its meaning is
        # not documented anywhere in the app, so it is passed through as-is.
        "motivation": dataproduct.get("motivation"),
        "preview_enabled": bool(dataproduct.get("enablePreview")),
        "url": browser_url(dataset_id, category_ids, lang, browser_base, node_code),
        "reference_metadata_url": meta.get("reference_metadata") or None,
        "sdmx_structure_url": links["structure"],
        "sdmx_data_csv_url": links["data_csv"],
        "in_catalog": dataset_id in index,
    }


def enrich_answer(answer, index, lang="it", browser_base=DEFAULT_BROWSER_BASE,
                  sdmx_base=DEFAULT_SDMX_BASE, node_code=DEFAULT_NODE_CODE):
    context = answer.get("chatContext") or {}
    products = context.get("dataproducts") or []
    return {
        "session_id": answer.get("session_id"),
        "request": answer.get("request"),
        "answer": answer.get("response"),
        "count": len(products),
        "results": [enrich(p, index, lang, browser_base, sdmx_base, node_code)
                    for p in products],
        "conversation": context.get("conversation") or [],
    }
