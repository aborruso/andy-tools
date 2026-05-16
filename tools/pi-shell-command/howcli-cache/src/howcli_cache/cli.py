from __future__ import annotations

import argparse
import os
import re
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path

from rapidfuzz import fuzz


VERSION = "0.1.0"


@dataclass
class CacheRow:
    query_original: str
    query_norm: str
    command: str
    debug: int
    used_count: int
    created_at: str
    last_used_at: str


def cache_db_path() -> Path:
    cache_home = os.environ.get("XDG_CACHE_HOME")
    if cache_home:
        return Path(cache_home) / "howcli" / "cache.sqlite"
    return Path.home() / ".cache" / "howcli" / "cache.sqlite"


def normalize(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9_./*-]+", text.lower()))


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or cache_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    init_db(conn)
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS cache (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          query_original TEXT NOT NULL,
          query_norm TEXT NOT NULL,
          command TEXT NOT NULL,
          debug INTEGER NOT NULL DEFAULT 0,
          used_count INTEGER NOT NULL DEFAULT 1,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
          last_used_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
          UNIQUE(query_norm, command)
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_cache_query_norm ON cache(query_norm)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_cache_last_used ON cache(last_used_at)")


def save(args: argparse.Namespace) -> int:
    conn = connect(args.db)
    conn.execute(
        """
        INSERT INTO cache (query_original, query_norm, command, debug)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(query_norm, command) DO UPDATE SET
          query_original=excluded.query_original,
          debug=excluded.debug,
          used_count=cache.used_count + 1,
          last_used_at=CURRENT_TIMESTAMP
        """,
        (args.query, normalize(args.query), args.command, 1 if args.debug else 0),
    )
    conn.commit()
    return 0


def fetch_rows(conn: sqlite3.Connection, limit: int = 500) -> list[CacheRow]:
    rows = conn.execute(
        """
        SELECT query_original, query_norm, command, debug, used_count, created_at, last_used_at
        FROM cache
        ORDER BY last_used_at DESC, id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [CacheRow(**dict(row)) for row in rows]


def score_row(query: str, row: CacheRow) -> int:
    qnorm = normalize(query)
    if not qnorm:
        return 0

    score = 0
    if qnorm == row.query_norm:
        score += 100
    if qnorm in row.query_norm:
        score += 20
    if qnorm in row.command.lower():
        score += 10

    score += int(fuzz.token_set_ratio(qnorm, row.query_norm) * 0.45)
    score += int(fuzz.partial_ratio(qnorm, row.query_norm) * 0.25)
    score += int(fuzz.partial_ratio(qnorm, row.command.lower()) * 0.15)
    score += min(row.used_count, 10)
    return score


def build_matches(args: argparse.Namespace) -> tuple[str, list[tuple[int, CacheRow]] | None]:
    conn = connect(args.db)
    rows = fetch_rows(conn, args.scan_limit)
    query = " ".join(args.query).strip()

    if not rows:
        return query, None

    if not query:
        matches = [(0, row) for row in rows[: args.limit]]
    else:
        matches = [(score_row(query, row), row) for row in rows]
        matches = [(score, row) for score, row in matches if score >= args.min_score]
        matches.sort(key=lambda item: (-item[0], -item[1].used_count, item[1].query_original))
        matches = matches[: args.limit]

    return query, matches


def search(args: argparse.Namespace) -> int:
    query, matches = build_matches(args)

    if matches is None:
        print("Cache vuota.", file=sys.stderr)
        return 2

    if not matches:
        print(f"Nessun match in cache per: {query}", file=sys.stderr)
        return 2

    if args.json:
        import json

        print(
            json.dumps(
                {
                    "matches": [
                        {
                            "score": score,
                            "query": row.query_original,
                            "command": row.command,
                            "debug": bool(row.debug),
                            "used_count": row.used_count,
                            "created_at": row.created_at,
                            "last_used_at": row.last_used_at,
                        }
                        for score, row in matches
                    ]
                },
                ensure_ascii=False,
            )
        )
        return 0

    print(f"{'SCORE':>5}  {'USED':>4}  {'QUERY':<40}  COMMAND")
    for score, row in matches:
        q = row.query_original.replace("\n", " ")
        c = row.command.replace("\n", " ")
        if len(q) > 40:
            q = q[:37] + "..."
        print(f"{score:>5}  {row.used_count:>4}  {q:<40}  {c}")
    print(f"COMMAND: {matches[0][1].command}")
    return 0


def top(args: argparse.Namespace) -> int:
    query, matches = build_matches(args)
    if matches is None:
        return 2
    if not matches:
        return 2
    print(matches[0][1].command)
    return 0


def clear(args: argparse.Namespace) -> int:
    path = args.db or cache_db_path()
    if not path.exists():
        return 0
    path.unlink()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="howcli-cache")
    parser.add_argument("--version", action="version", version=f"howcli-cache {VERSION}")
    parser.add_argument("--db", type=Path, default=None, help="SQLite cache path")
    subparsers = parser.add_subparsers(dest="command", required=True)

    save_parser = subparsers.add_parser("save", help="Save a generated command")
    save_parser.add_argument("--query", required=True)
    save_parser.add_argument("--command", required=True)
    save_parser.add_argument("--debug", action="store_true")
    save_parser.set_defaults(func=save)

    search_parser = subparsers.add_parser("search", help="Search cached commands")
    search_parser.add_argument("query", nargs="*")
    search_parser.add_argument("--limit", type=int, default=5)
    search_parser.add_argument("--scan-limit", type=int, default=500)
    search_parser.add_argument("--min-score", type=int, default=35)
    search_parser.add_argument("--json", action="store_true")
    search_parser.set_defaults(func=search)

    list_parser = subparsers.add_parser("list", help="List recent cached commands")
    list_parser.add_argument("--limit", type=int, default=5)
    list_parser.add_argument("--scan-limit", type=int, default=500)
    list_parser.add_argument("--min-score", type=int, default=35)
    list_parser.add_argument("--json", action="store_true")
    list_parser.set_defaults(func=lambda args: search(args))
    list_parser.set_defaults(query=[])

    top_parser = subparsers.add_parser("top", help="Print only the top cached command")
    top_parser.add_argument("query", nargs="*")
    top_parser.add_argument("--limit", type=int, default=1)
    top_parser.add_argument("--scan-limit", type=int, default=500)
    top_parser.add_argument("--min-score", type=int, default=35)
    top_parser.set_defaults(func=top)

    clear_parser = subparsers.add_parser("clear", help="Clear the cache")
    clear_parser.set_defaults(func=clear)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
