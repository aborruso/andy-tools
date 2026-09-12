"""Node catalogue: fetch, cache on disk, index by dataset id.

The AI endpoint returns dataset ids with an empty `title`, so every readable
label comes from here. Titles are language-dependent, hence the cache key.
"""

import json
import os
import time
from pathlib import Path

CACHE_TTL_SECONDS = 24 * 60 * 60


def cache_dir():
    base = os.environ.get("XDG_CACHE_HOME") or os.path.join(Path.home(), ".cache")
    return Path(base) / "istatdata-ai"


def cache_path(node, lang):
    return cache_dir() / f"catalog_node{node}_{lang}.json"


def _write_atomic(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".tmp{os.getpid()}")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False)
    os.replace(tmp, path)


def load(client, refresh=False, use_cache=True):
    """Return (catalog_dict, from_cache: bool)."""
    path = cache_path(client.node, client.lang)
    if use_cache and not refresh and path.exists():
        age = time.time() - path.stat().st_mtime
        if age < CACHE_TTL_SECONDS:
            try:
                with open(path, encoding="utf-8") as fh:
                    return json.load(fh), True
            except ValueError:
                pass
    catalog = client.fetch_catalog()
    if use_cache:
        _write_atomic(path, catalog)
    return catalog, False


def cache_info(node, lang):
    path = cache_path(node, lang)
    if not path.exists():
        return {"path": str(path), "exists": False, "age_seconds": None,
                "size_bytes": None, "stale": None}
    stat = path.stat()
    age = time.time() - stat.st_mtime
    return {"path": str(path), "exists": True, "age_seconds": int(age),
            "size_bytes": stat.st_size, "stale": age >= CACHE_TTL_SECONDS}


def build_index(catalog):
    """Map dataset id -> {title, category_ids, category_labels, ...}.

    `category_ids` is the path used by the browser deep link: the category
    group id first, then the chain of category ids down to the leaf.
    """
    index = {}
    dataset_map = catalog.get("datasetMap") or {}

    def walk(categories, id_path, label_path):
        for cat in categories:
            ids = id_path + [cat["id"]]
            labels = label_path + [cat.get("label") or cat["id"]]
            for dataset_id in cat.get("datasetIdentifiers") or []:
                index.setdefault(dataset_id, {"category_ids": ids, "category_labels": labels})
            walk(cat.get("childrenCategories") or [], ids, labels)

    for group in catalog.get("categoryGroups") or []:
        walk(group.get("categories") or [],
             [group["id"]],
             [group.get("label") or group["id"]])

    for dataset_id, meta in dataset_map.items():
        entry = index.setdefault(dataset_id, {"category_ids": [], "category_labels": []})
        entry["title"] = meta.get("title") or ""
        entry["reference_metadata"] = meta.get("referenceMetadata") or ""
        entry["dataset_type"] = meta.get("datasetType") or ""
    return index
