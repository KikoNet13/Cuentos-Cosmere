from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import CACHE_DB_PATH, LIBRARY_ROOT, ROOT_DIR
from .library_fs import list_relevant_files, scan_library

_FINGERPRINT_TTL_SECONDS = 3.0
_FINGERPRINT_CACHE: dict[str, Any] = {
    "checked_at": 0.0,
    "fingerprint": "",
    "scanned_files": 0,
}

_FILE_BACKEND_AVAILABLE: bool | None = None
_MEMORY_CONNECTION: sqlite3.Connection | None = None


def _get_memory_connection() -> sqlite3.Connection:
    global _MEMORY_CONNECTION
    if _MEMORY_CONNECTION is None:
        _MEMORY_CONNECTION = sqlite3.connect(":memory:", check_same_thread=False)
        _MEMORY_CONNECTION.row_factory = sqlite3.Row
        _MEMORY_CONNECTION.execute("PRAGMA foreign_keys=ON")
    return _MEMORY_CONNECTION


def cache_backend_label() -> str:
    if _FILE_BACKEND_AVAILABLE is False:
        return ":memory:"
    return str(CACHE_DB_PATH.relative_to(ROOT_DIR))


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _connect() -> sqlite3.Connection:
    global _FILE_BACKEND_AVAILABLE

    if _FILE_BACKEND_AVAILABLE is False:
        return _get_memory_connection()

    CACHE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(CACHE_DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        conn.execute("PRAGMA foreign_keys=ON")
        if _FILE_BACKEND_AVAILABLE is None:
            conn.execute("CREATE TABLE IF NOT EXISTS __cache_probe__(id INTEGER)")
            conn.execute("INSERT INTO __cache_probe__(id) VALUES (1)")
            conn.execute("DELETE FROM __cache_probe__")
            conn.commit()
            _FILE_BACKEND_AVAILABLE = True
        return conn
    except sqlite3.OperationalError:
        _FILE_BACKEND_AVAILABLE = False
        try:
            conn.close()
        except sqlite3.Error:
            pass
        return _get_memory_connection()


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS cache_state (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            library_fingerprint TEXT NOT NULL,
            last_refresh_at TEXT NOT NULL,
            is_stale INTEGER NOT NULL DEFAULT 0,
            scanned_files INTEGER NOT NULL DEFAULT 0,
            warnings_json TEXT NOT NULL DEFAULT '[]'
        );

        CREATE TABLE IF NOT EXISTS cache_node (
            path_rel TEXT PRIMARY KEY,
            parent_path_rel TEXT,
            name TEXT NOT NULL,
            is_story_leaf INTEGER NOT NULL DEFAULT 0,
            is_book_node INTEGER NOT NULL DEFAULT 0
        );
        CREATE INDEX IF NOT EXISTS cache_node_parent_idx
        ON cache_node(parent_path_rel);

        CREATE TABLE IF NOT EXISTS cache_story (
            story_rel_path TEXT PRIMARY KEY,
            story_id TEXT NOT NULL DEFAULT '',
            story_file_rel_path TEXT NOT NULL DEFAULT '',
            title TEXT NOT NULL,
            status TEXT NOT NULL,
            meta_rel_path TEXT NOT NULL,
            cover_prompt TEXT NOT NULL DEFAULT '',
            back_cover_prompt TEXT NOT NULL DEFAULT '',
            notes TEXT NOT NULL DEFAULT '',
            last_parsed_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS cache_page (
            story_rel_path TEXT NOT NULL,
            page_number INTEGER NOT NULL,
            file_rel_path TEXT NOT NULL,
            content TEXT NOT NULL,
            raw_frontmatter_json TEXT NOT NULL DEFAULT '{}',
            PRIMARY KEY (story_rel_path, page_number),
            FOREIGN KEY (story_rel_path) REFERENCES cache_story(story_rel_path)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS cache_page_slot (
            story_rel_path TEXT NOT NULL,
            page_number INTEGER NOT NULL,
            slot_name TEXT NOT NULL,
            role TEXT NOT NULL,
            prompt_text TEXT NOT NULL,
            display_order INTEGER NOT NULL DEFAULT 0,
            image_rel_path TEXT NOT NULL DEFAULT '',
            PRIMARY KEY (story_rel_path, page_number, slot_name),
            FOREIGN KEY (story_rel_path, page_number)
                REFERENCES cache_page(story_rel_path, page_number)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS cache_slot_requirement (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_rel_path TEXT NOT NULL,
            page_number INTEGER NOT NULL,
            slot_name TEXT NOT NULL,
            requirement_kind TEXT NOT NULL,
            ref_value TEXT NOT NULL,
            display_order INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (story_rel_path, page_number, slot_name)
                REFERENCES cache_page_slot(story_rel_path, page_number, slot_name)
                ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS cache_slot_requirement_idx
        ON cache_slot_requirement(story_rel_path, page_number, slot_name, display_order, id);

        CREATE TABLE IF NOT EXISTS cache_asset (
            rel_path TEXT PRIMARY KEY,
            kind TEXT NOT NULL,
            size INTEGER NOT NULL,
            mtime_ns INTEGER NOT NULL,
            is_present INTEGER NOT NULL DEFAULT 1
        );
        """
    )
    _ensure_optional_columns(conn)


def _table_columns(conn: sqlite3.Connection, table_name: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {str(row[1]) for row in rows}


def _ensure_optional_columns(conn: sqlite3.Connection) -> None:
    node_columns = _table_columns(conn, "cache_node")
    if "is_book_node" not in node_columns:
        conn.execute("ALTER TABLE cache_node ADD COLUMN is_book_node INTEGER NOT NULL DEFAULT 0")

    story_columns = _table_columns(conn, "cache_story")
    if "story_id" not in story_columns:
        conn.execute("ALTER TABLE cache_story ADD COLUMN story_id TEXT NOT NULL DEFAULT ''")
    if "story_file_rel_path" not in story_columns:
        conn.execute("ALTER TABLE cache_story ADD COLUMN story_file_rel_path TEXT NOT NULL DEFAULT ''")


def _normalize_rel_path(path_rel: str) -> str:
    return path_rel.strip().replace("\\", "/").strip("/")


def _clear_snapshot_tables(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM cache_slot_requirement")
    conn.execute("DELETE FROM cache_page_slot")
    conn.execute("DELETE FROM cache_page")
    conn.execute("DELETE FROM cache_story")
    conn.execute("DELETE FROM cache_node")
    conn.execute("DELETE FROM cache_asset")


def _fingerprint_line(path: Path, root: Path) -> str:
    stat = path.stat()
    rel_path = path.resolve().relative_to(root.resolve()).as_posix()
    return f"{rel_path}|{stat.st_size}|{stat.st_mtime_ns}"


def compute_library_fingerprint(root: Path | None = None) -> tuple[str, int]:
    base_root = (root or LIBRARY_ROOT).resolve()
    lines = [_fingerprint_line(path, base_root) for path in list_relevant_files(base_root)]
    payload = "\n".join(lines)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return digest, len(lines)


def get_live_fingerprint(ttl_seconds: float = _FINGERPRINT_TTL_SECONDS) -> tuple[str, int]:
    now_monotonic = time.monotonic()
    if (
        _FINGERPRINT_CACHE["fingerprint"]
        and (now_monotonic - float(_FINGERPRINT_CACHE["checked_at"])) <= ttl_seconds
    ):
        return (
            str(_FINGERPRINT_CACHE["fingerprint"]),
            int(_FINGERPRINT_CACHE["scanned_files"]),
        )

    fingerprint, scanned_files = compute_library_fingerprint(LIBRARY_ROOT)
    _FINGERPRINT_CACHE["checked_at"] = now_monotonic
    _FINGERPRINT_CACHE["fingerprint"] = fingerprint
    _FINGERPRINT_CACHE["scanned_files"] = scanned_files
    return fingerprint, scanned_files


def _row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {key: row[key] for key in row.keys()}


def get_cache_state() -> dict[str, Any]:
    with _connect() as conn:
        _ensure_schema(conn)
        row = conn.execute("SELECT * FROM cache_state WHERE id=1").fetchone()

    if row is None:
        return {
            "has_cache": False,
            "fingerprint": "",
            "last_refresh_at": "",
            "stale": True,
            "scanned_files": 0,
            "warnings": [],
            "cache_backend": cache_backend_label(),
        }

    warnings: list[str] = []
    raw_warnings = str(row["warnings_json"] or "[]")
    try:
        parsed = json.loads(raw_warnings)
        if isinstance(parsed, list):
            warnings = [str(item) for item in parsed]
    except json.JSONDecodeError:
        warnings = []

    return {
        "has_cache": True,
        "fingerprint": str(row["library_fingerprint"]),
        "last_refresh_at": str(row["last_refresh_at"]),
        "stale": bool(row["is_stale"]),
        "scanned_files": int(row["scanned_files"]),
        "warnings": warnings,
        "cache_backend": cache_backend_label(),
    }


def refresh_stale_flag(ttl_seconds: float = _FINGERPRINT_TTL_SECONDS) -> dict[str, Any]:
    state = get_cache_state()
    live_fingerprint, live_scanned_files = get_live_fingerprint(ttl_seconds=ttl_seconds)
    stale = not state["has_cache"] or (live_fingerprint != str(state.get("fingerprint", "")))

    with _connect() as conn:
        _ensure_schema(conn)
        if state["has_cache"]:
            conn.execute(
                """
                UPDATE cache_state
                SET is_stale=?, scanned_files=?
                WHERE id=1
                """,
                (1 if stale else 0, live_scanned_files),
            )

    merged = get_cache_state()
    merged["live_fingerprint"] = live_fingerprint
    merged["live_scanned_files"] = live_scanned_files
    merged["stale"] = stale
    return merged


def accept_live_fingerprint(ttl_seconds: float = _FINGERPRINT_TTL_SECONDS) -> dict[str, Any]:
    state = get_cache_state()
    if not state["has_cache"]:
        return rebuild_cache()

    live_fingerprint, live_scanned_files = get_live_fingerprint(ttl_seconds=ttl_seconds)
    now_iso = _utc_now_iso()
    with _connect() as conn:
        _ensure_schema(conn)
        conn.execute(
            """
            UPDATE cache_state
            SET library_fingerprint=?, last_refresh_at=?, is_stale=0, scanned_files=?
            WHERE id=1
            """,
            (live_fingerprint, now_iso, live_scanned_files),
        )

    merged = get_cache_state()
    merged["live_fingerprint"] = live_fingerprint
    merged["live_scanned_files"] = live_scanned_files
    merged["stale"] = False
    return merged


def ensure_cache_ready() -> dict[str, Any]:
    state = get_cache_state()
    if not state["has_cache"]:
        rebuild_cache()
    return refresh_stale_flag()


def rebuild_cache() -> dict[str, Any]:
    snapshot = scan_library()
    fingerprint, scanned_files = compute_library_fingerprint(LIBRARY_ROOT)
    now_iso = _utc_now_iso()

    with _connect() as conn:
        _ensure_schema(conn)
        with conn:
            _clear_snapshot_tables(conn)

            for node in snapshot.nodes:
                conn.execute(
                    """
                    INSERT INTO cache_node(path_rel, parent_path_rel, name, is_story_leaf, is_book_node)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        node.path_rel,
                        node.parent_path_rel,
                        node.name,
                        1 if node.is_story_leaf else 0,
                        1 if node.is_book_node else 0,
                    ),
                )

            for story in snapshot.stories:
                conn.execute(
                    """
                    INSERT INTO cache_story(
                        story_rel_path, story_id, story_file_rel_path, title, status, meta_rel_path,
                        cover_prompt, back_cover_prompt, notes, last_parsed_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        story.story_rel_path,
                        story.story_id,
                        story.story_file_rel_path,
                        story.meta.title,
                        story.meta.status,
                        story.meta_rel_path,
                        story.meta.cover_prompt,
                        story.meta.back_cover_prompt,
                        story.meta.notes,
                        now_iso,
                    ),
                )

                for page in story.pages:
                    conn.execute(
                        """
                        INSERT INTO cache_page(
                            story_rel_path, page_number, file_rel_path,
                            content, raw_frontmatter_json
                        )
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            story.story_rel_path,
                            int(page.page_number),
                            page.file_rel_path,
                            page.content,
                            page.raw_frontmatter_json,
                        ),
                    )

                    for slot in page.image_slots:
                        conn.execute(
                            """
                            INSERT INTO cache_page_slot(
                                story_rel_path, page_number, slot_name, role,
                                prompt_text, display_order, image_rel_path
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                story.story_rel_path,
                                int(page.page_number),
                                slot.slot_name,
                                slot.role,
                                slot.prompt_text,
                                int(slot.display_order),
                                slot.image_rel_path,
                            ),
                        )

                        for requirement in slot.requirements:
                            conn.execute(
                                """
                                INSERT INTO cache_slot_requirement(
                                    story_rel_path, page_number, slot_name,
                                    requirement_kind, ref_value, display_order
                                )
                                VALUES (?, ?, ?, ?, ?, ?)
                                """,
                                (
                                    story.story_rel_path,
                                    int(page.page_number),
                                    slot.slot_name,
                                    requirement.kind,
                                    requirement.ref,
                                    int(requirement.order),
                                ),
                            )

            for asset in snapshot.assets:
                conn.execute(
                    """
                    INSERT INTO cache_asset(rel_path, kind, size, mtime_ns, is_present)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        asset.rel_path,
                        asset.kind,
                        int(asset.size),
                        int(asset.mtime_ns),
                        1 if asset.is_present else 0,
                    ),
                )

            conn.execute(
                """
                INSERT INTO cache_state(
                    id, library_fingerprint, last_refresh_at, is_stale,
                    scanned_files, warnings_json
                )
                VALUES (1, ?, ?, 0, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    library_fingerprint=excluded.library_fingerprint,
                    last_refresh_at=excluded.last_refresh_at,
                    is_stale=0,
                    scanned_files=excluded.scanned_files,
                    warnings_json=excluded.warnings_json
                """,
                (
                    fingerprint,
                    now_iso,
                    scanned_files,
                    json.dumps(snapshot.warnings, ensure_ascii=False),
                ),
            )

    _FINGERPRINT_CACHE["checked_at"] = time.monotonic()
    _FINGERPRINT_CACHE["fingerprint"] = fingerprint
    _FINGERPRINT_CACHE["scanned_files"] = scanned_files

    return {
        "nodes": len(snapshot.nodes),
        "stories": len(snapshot.stories),
        "pages": sum(len(story.pages) for story in snapshot.stories),
        "slots": sum(len(page.image_slots) for story in snapshot.stories for page in story.pages),
        "assets": len(snapshot.assets),
        "warnings": list(snapshot.warnings),
        "fingerprint": fingerprint,
        "scanned_files": scanned_files,
        "cache_db": cache_backend_label(),
    }


def cache_counts() -> dict[str, int]:
    with _connect() as conn:
        _ensure_schema(conn)
        node_count = conn.execute("SELECT COUNT(*) FROM cache_node").fetchone()[0]
        story_count = conn.execute("SELECT COUNT(*) FROM cache_story").fetchone()[0]
        page_count = conn.execute("SELECT COUNT(*) FROM cache_page").fetchone()[0]
        slot_count = conn.execute("SELECT COUNT(*) FROM cache_page_slot").fetchone()[0]
        requirement_count = conn.execute("SELECT COUNT(*) FROM cache_slot_requirement").fetchone()[0]
        asset_count = conn.execute("SELECT COUNT(*) FROM cache_asset").fetchone()[0]

    return {
        "nodes": int(node_count),
        "stories": int(story_count),
        "pages": int(page_count),
        "slots": int(slot_count),
        "requirements": int(requirement_count),
        "assets": int(asset_count),
    }


def list_children(parent_path_rel: str) -> list[dict[str, Any]]:
    parent_rel = _normalize_rel_path(parent_path_rel)
    with _connect() as conn:
        _ensure_schema(conn)
        rows = conn.execute(
            """
            SELECT path_rel, parent_path_rel, name, is_story_leaf, is_book_node
            FROM cache_node
            WHERE parent_path_rel=?
            ORDER BY name COLLATE NOCASE ASC
            """,
            (parent_rel,),
        ).fetchall()
    return [_row_to_dict(row) for row in rows if row is not None]


def get_node(path_rel: str) -> dict[str, Any] | None:
    normalized = _normalize_rel_path(path_rel)
    if not normalized:
        return {
            "path_rel": "",
            "parent_path_rel": None,
            "name": "biblioteca",
            "is_story_leaf": 0,
            "is_book_node": 0,
        }

    with _connect() as conn:
        _ensure_schema(conn)
        row = conn.execute(
            """
            SELECT path_rel, parent_path_rel, name, is_story_leaf, is_book_node
            FROM cache_node
            WHERE path_rel=?
            """,
            (normalized,),
        ).fetchone()
    return _row_to_dict(row)


def get_story(story_rel_path: str) -> dict[str, Any] | None:
    normalized = _normalize_rel_path(story_rel_path)
    with _connect() as conn:
        _ensure_schema(conn)
        row = conn.execute(
            """
            SELECT story_rel_path, story_id, story_file_rel_path, title, status, meta_rel_path,
                   cover_prompt, back_cover_prompt, notes, last_parsed_at
            FROM cache_story
            WHERE story_rel_path=?
            """,
            (normalized,),
        ).fetchone()
    return _row_to_dict(row)


def list_story_pages(story_rel_path: str) -> list[dict[str, Any]]:
    normalized = _normalize_rel_path(story_rel_path)
    with _connect() as conn:
        _ensure_schema(conn)
        rows = conn.execute(
            """
            SELECT story_rel_path, page_number, file_rel_path, content, raw_frontmatter_json
            FROM cache_page
            WHERE story_rel_path=?
            ORDER BY page_number ASC
            """,
            (normalized,),
        ).fetchall()
    return [_row_to_dict(row) for row in rows if row is not None]


def get_story_page(story_rel_path: str, page_number: int) -> dict[str, Any] | None:
    normalized = _normalize_rel_path(story_rel_path)
    with _connect() as conn:
        _ensure_schema(conn)
        row = conn.execute(
            """
            SELECT story_rel_path, page_number, file_rel_path, content, raw_frontmatter_json
            FROM cache_page
            WHERE story_rel_path=? AND page_number=?
            """,
            (normalized, int(page_number)),
        ).fetchone()
    return _row_to_dict(row)


def list_page_slots(story_rel_path: str, page_number: int) -> list[dict[str, Any]]:
    normalized = _normalize_rel_path(story_rel_path)
    with _connect() as conn:
        _ensure_schema(conn)
        rows = conn.execute(
            """
            SELECT story_rel_path, page_number, slot_name, role,
                   prompt_text, display_order, image_rel_path
            FROM cache_page_slot
            WHERE story_rel_path=? AND page_number=?
            ORDER BY display_order ASC, slot_name ASC
            """,
            (normalized, int(page_number)),
        ).fetchall()
    return [_row_to_dict(row) for row in rows if row is not None]


def get_page_slot(story_rel_path: str, page_number: int, slot_name: str) -> dict[str, Any] | None:
    normalized = _normalize_rel_path(story_rel_path)
    with _connect() as conn:
        _ensure_schema(conn)
        row = conn.execute(
            """
            SELECT story_rel_path, page_number, slot_name, role,
                   prompt_text, display_order, image_rel_path
            FROM cache_page_slot
            WHERE story_rel_path=? AND page_number=? AND slot_name=?
            """,
            (normalized, int(page_number), slot_name),
        ).fetchone()
    return _row_to_dict(row)


def list_slot_requirements(story_rel_path: str, page_number: int, slot_name: str) -> list[dict[str, Any]]:
    normalized = _normalize_rel_path(story_rel_path)
    with _connect() as conn:
        _ensure_schema(conn)
        rows = conn.execute(
            """
            SELECT id, story_rel_path, page_number, slot_name,
                   requirement_kind, ref_value, display_order
            FROM cache_slot_requirement
            WHERE story_rel_path=? AND page_number=? AND slot_name=?
            ORDER BY display_order ASC, id ASC
            """,
            (normalized, int(page_number), slot_name),
        ).fetchall()
    return [_row_to_dict(row) for row in rows if row is not None]


def upsert_asset_index(rel_path: str) -> None:
    normalized_rel = rel_path.strip().replace("\\", "/")
    abs_path = (ROOT_DIR / normalized_rel).resolve()
    if ROOT_DIR.resolve() not in abs_path.parents:
        return

    if abs_path.exists() and abs_path.is_file():
        stat = abs_path.stat()
        ext = abs_path.suffix.lower()
        if ext in {".png", ".jpg", ".jpeg", ".webp"}:
            kind = "image"
        elif ext == ".md":
            kind = "md"
        elif ext == ".pdf":
            kind = "pdf"
        elif ext == ".json":
            kind = "json"
        else:
            kind = "other"
        size = int(stat.st_size)
        mtime_ns = int(stat.st_mtime_ns)
        is_present = 1
    else:
        kind = "missing"
        size = 0
        mtime_ns = 0
        is_present = 0

    with _connect() as conn:
        _ensure_schema(conn)
        conn.execute(
            """
            INSERT INTO cache_asset(rel_path, kind, size, mtime_ns, is_present)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(rel_path) DO UPDATE SET
                kind=excluded.kind,
                size=excluded.size,
                mtime_ns=excluded.mtime_ns,
                is_present=excluded.is_present
            """,
            (normalized_rel, kind, size, mtime_ns, is_present),
        )
