from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import BASE_DIR, DATA_ROOT, LIBRARY_CACHE_DB_PATH
from .library_fs import relevant_files, scan_library

_FINGERPRINT_TTL_SECONDS = 3.0
_FINGERPRINT_CACHE: dict[str, Any] = {
    "checked_at": 0.0,
    "fingerprint": "",
    "scanned_files": 0,
}
_FILE_BACKEND_AVAILABLE: bool | None = None
_MEMORY_CONN: sqlite3.Connection | None = None


def _memory_connect() -> sqlite3.Connection:
    global _MEMORY_CONN
    if _MEMORY_CONN is None:
        _MEMORY_CONN = sqlite3.connect(":memory:", check_same_thread=False)
        _MEMORY_CONN.row_factory = sqlite3.Row
        _MEMORY_CONN.execute("PRAGMA foreign_keys=ON")
    return _MEMORY_CONN


def cache_backend_label() -> str:
    if _FILE_BACKEND_AVAILABLE is False:
        return ":memory:"
    return str(LIBRARY_CACHE_DB_PATH.relative_to(BASE_DIR))


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _connect() -> sqlite3.Connection:
    global _FILE_BACKEND_AVAILABLE

    if _FILE_BACKEND_AVAILABLE is False:
        return _memory_connect()

    LIBRARY_CACHE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(LIBRARY_CACHE_DB_PATH)
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
        return _memory_connect()


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS cache_state (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            fingerprint_global TEXT NOT NULL,
            last_refresh_at TEXT NOT NULL,
            stale INTEGER NOT NULL DEFAULT 0,
            scanned_files INTEGER NOT NULL DEFAULT 0,
            warnings_json TEXT NOT NULL DEFAULT '[]'
        );

        CREATE TABLE IF NOT EXISTS node (
            path_rel TEXT PRIMARY KEY,
            parent_path_rel TEXT,
            nombre TEXT NOT NULL,
            is_story_leaf INTEGER NOT NULL DEFAULT 0
        );
        CREATE INDEX IF NOT EXISTS node_parent_path_rel_idx ON node(parent_path_rel);

        CREATE TABLE IF NOT EXISTS story (
            story_path_rel TEXT PRIMARY KEY,
            titulo TEXT NOT NULL,
            estado TEXT NOT NULL,
            meta_file TEXT NOT NULL,
            prompt_portada TEXT NOT NULL DEFAULT '',
            prompt_contraportada TEXT NOT NULL DEFAULT '',
            notas TEXT NOT NULL DEFAULT '',
            last_parsed_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS page (
            story_path_rel TEXT NOT NULL,
            numero INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            contenido TEXT NOT NULL,
            raw_frontmatter_json TEXT NOT NULL DEFAULT '{}',
            PRIMARY KEY (story_path_rel, numero),
            FOREIGN KEY (story_path_rel) REFERENCES story(story_path_rel)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS page_image_slot (
            story_path_rel TEXT NOT NULL,
            page_num INTEGER NOT NULL,
            slot TEXT NOT NULL,
            rol TEXT NOT NULL,
            prompt TEXT NOT NULL,
            orden INTEGER NOT NULL DEFAULT 0,
            image_rel_path TEXT NOT NULL DEFAULT '',
            PRIMARY KEY (story_path_rel, page_num, slot),
            FOREIGN KEY (story_path_rel, page_num)
                REFERENCES page(story_path_rel, numero)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS page_slot_requirement (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_path_rel TEXT NOT NULL,
            page_num INTEGER NOT NULL,
            slot TEXT NOT NULL,
            tipo TEXT NOT NULL,
            ref TEXT NOT NULL,
            orden INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (story_path_rel, page_num, slot)
                REFERENCES page_image_slot(story_path_rel, page_num, slot)
                ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS req_slot_idx ON page_slot_requirement(
            story_path_rel, page_num, slot, orden, id
        );

        CREATE TABLE IF NOT EXISTS asset_index (
            rel_path TEXT PRIMARY KEY,
            kind TEXT NOT NULL,
            size INTEGER NOT NULL,
            mtime_ns INTEGER NOT NULL,
            is_present INTEGER NOT NULL DEFAULT 1
        );
        """
    )


def _normalize_rel(path_rel: str) -> str:
    return path_rel.strip().replace("\\", "/").strip("/")


def _clear_snapshot_tables(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM page_slot_requirement")
    conn.execute("DELETE FROM page_image_slot")
    conn.execute("DELETE FROM page")
    conn.execute("DELETE FROM story")
    conn.execute("DELETE FROM node")
    conn.execute("DELETE FROM asset_index")


def _fingerprint_line(path: Path, root: Path) -> str:
    stat = path.stat()
    rel = path.resolve().relative_to(root.resolve()).as_posix()
    return f"{rel}|{stat.st_size}|{stat.st_mtime_ns}"


def compute_library_fingerprint(root: Path | None = None) -> tuple[str, int]:
    base_root = (root or DATA_ROOT).resolve()
    rows = [_fingerprint_line(path, base_root) for path in relevant_files(base_root)]
    payload = "\n".join(rows)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return digest, len(rows)


def get_live_fingerprint(ttl_seconds: float = _FINGERPRINT_TTL_SECONDS) -> tuple[str, int]:
    now_monotonic = time.monotonic()
    if (
        _FINGERPRINT_CACHE["fingerprint"]
        and (now_monotonic - float(_FINGERPRINT_CACHE["checked_at"])) <= ttl_seconds
    ):
        return str(_FINGERPRINT_CACHE["fingerprint"]), int(_FINGERPRINT_CACHE["scanned_files"])

    fingerprint, scanned_files = compute_library_fingerprint(DATA_ROOT)
    _FINGERPRINT_CACHE["checked_at"] = now_monotonic
    _FINGERPRINT_CACHE["fingerprint"] = fingerprint
    _FINGERPRINT_CACHE["scanned_files"] = scanned_files
    return fingerprint, scanned_files


def _row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {k: row[k] for k in row.keys()}


def get_cache_state() -> dict[str, Any]:
    with _connect() as conn:
        _ensure_schema(conn)
        row = conn.execute("SELECT * FROM cache_state WHERE id=1").fetchone()
    if row is None:
        return {
            "has_cache": False,
            "fingerprint_global": "",
            "last_refresh_at": "",
            "stale": True,
            "scanned_files": 0,
            "warnings": [],
            "cache_backend": cache_backend_label(),
        }
    warnings = []
    raw = str(row["warnings_json"] or "[]")
    try:
        decoded = json.loads(raw)
        if isinstance(decoded, list):
            warnings = [str(x) for x in decoded]
    except json.JSONDecodeError:
        warnings = []
    return {
        "has_cache": True,
        "fingerprint_global": str(row["fingerprint_global"]),
        "last_refresh_at": str(row["last_refresh_at"]),
        "stale": bool(row["stale"]),
        "scanned_files": int(row["scanned_files"]),
        "warnings": warnings,
        "cache_backend": cache_backend_label(),
    }


def refresh_stale_flag(ttl_seconds: float = _FINGERPRINT_TTL_SECONDS) -> dict[str, Any]:
    state = get_cache_state()
    live_fingerprint, live_scanned = get_live_fingerprint(ttl_seconds=ttl_seconds)
    cached_fingerprint = str(state.get("fingerprint_global", ""))
    stale = not state["has_cache"] or (live_fingerprint != cached_fingerprint)

    with _connect() as conn:
        _ensure_schema(conn)
        if state["has_cache"]:
            conn.execute(
                """
                UPDATE cache_state
                SET stale=?, scanned_files=?
                WHERE id=1
                """,
                (1 if stale else 0, live_scanned),
            )

    merged = get_cache_state()
    merged["live_fingerprint"] = live_fingerprint
    merged["live_scanned_files"] = live_scanned
    merged["stale"] = stale
    return merged


def accept_live_fingerprint(ttl_seconds: float = _FINGERPRINT_TTL_SECONDS) -> dict[str, Any]:
    state = get_cache_state()
    if not state["has_cache"]:
        return rebuild_cache()

    live_fingerprint, live_scanned = get_live_fingerprint(ttl_seconds=ttl_seconds)
    now = _now_iso()
    with _connect() as conn:
        _ensure_schema(conn)
        conn.execute(
            """
            UPDATE cache_state
            SET fingerprint_global=?, last_refresh_at=?, stale=0, scanned_files=?
            WHERE id=1
            """,
            (live_fingerprint, now, live_scanned),
        )
    merged = get_cache_state()
    merged["live_fingerprint"] = live_fingerprint
    merged["live_scanned_files"] = live_scanned
    merged["stale"] = False
    return merged


def ensure_cache_ready() -> dict[str, Any]:
    state = get_cache_state()
    if not state["has_cache"]:
        rebuild_cache()
    return refresh_stale_flag()


def rebuild_cache() -> dict[str, Any]:
    snapshot = scan_library()
    fingerprint, scanned_files = compute_library_fingerprint(DATA_ROOT)
    now = _now_iso()
    with _connect() as conn:
        _ensure_schema(conn)
        with conn:
            _clear_snapshot_tables(conn)

            for node in snapshot.nodes:
                conn.execute(
                    """
                    INSERT INTO node(path_rel, parent_path_rel, nombre, is_story_leaf)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        node.path_rel,
                        node.parent_path_rel,
                        node.nombre,
                        1 if node.is_story_leaf else 0,
                    ),
                )

            for story in snapshot.stories:
                conn.execute(
                    """
                    INSERT INTO story(
                        story_path_rel, titulo, estado, meta_file, prompt_portada,
                        prompt_contraportada, notas, last_parsed_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        story.story_path_rel,
                        story.meta.titulo,
                        story.meta.estado,
                        story.meta_file_rel,
                        story.meta.prompt_portada,
                        story.meta.prompt_contraportada,
                        story.meta.notas,
                        now,
                    ),
                )
                for page in story.pages:
                    conn.execute(
                        """
                        INSERT INTO page(
                            story_path_rel, numero, file_path, contenido,
                            raw_frontmatter_json
                        )
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            story.story_path_rel,
                            int(page.numero),
                            page.file_rel,
                            page.contenido,
                            page.raw_frontmatter_json,
                        ),
                    )
                    for slot in page.image_slots:
                        conn.execute(
                            """
                            INSERT INTO page_image_slot(
                                story_path_rel, page_num, slot, rol, prompt, orden,
                                image_rel_path
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                story.story_path_rel,
                                int(page.numero),
                                slot.slot,
                                slot.rol,
                                slot.prompt,
                                int(slot.orden),
                                slot.image_rel_path,
                            ),
                        )
                        for req in slot.requisitos:
                            conn.execute(
                                """
                                INSERT INTO page_slot_requirement(
                                    story_path_rel, page_num, slot, tipo, ref, orden
                                )
                                VALUES (?, ?, ?, ?, ?, ?)
                                """,
                                (
                                    story.story_path_rel,
                                    int(page.numero),
                                    slot.slot,
                                    req.tipo,
                                    req.ref,
                                    int(req.orden),
                                ),
                            )

            for asset in snapshot.assets:
                conn.execute(
                    """
                    INSERT INTO asset_index(rel_path, kind, size, mtime_ns, is_present)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        asset.rel_path,
                        asset.kind,
                        int(asset.size),
                        int(asset.mtime_ns),
                        1 if asset.exists else 0,
                    ),
                )

            conn.execute(
                """
                INSERT INTO cache_state(
                    id, fingerprint_global, last_refresh_at, stale, scanned_files,
                    warnings_json
                )
                VALUES (1, ?, ?, 0, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    fingerprint_global=excluded.fingerprint_global,
                    last_refresh_at=excluded.last_refresh_at,
                    stale=0,
                    scanned_files=excluded.scanned_files,
                    warnings_json=excluded.warnings_json
                """,
                (fingerprint, now, scanned_files, json.dumps(snapshot.warnings, ensure_ascii=False)),
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
        node_count = conn.execute("SELECT COUNT(*) FROM node").fetchone()[0]
        story_count = conn.execute("SELECT COUNT(*) FROM story").fetchone()[0]
        page_count = conn.execute("SELECT COUNT(*) FROM page").fetchone()[0]
        slot_count = conn.execute("SELECT COUNT(*) FROM page_image_slot").fetchone()[0]
        req_count = conn.execute("SELECT COUNT(*) FROM page_slot_requirement").fetchone()[0]
        asset_count = conn.execute("SELECT COUNT(*) FROM asset_index").fetchone()[0]
    return {
        "nodes": int(node_count),
        "stories": int(story_count),
        "pages": int(page_count),
        "slots": int(slot_count),
        "requirements": int(req_count),
        "assets": int(asset_count),
    }


def list_children(parent_path_rel: str) -> list[dict[str, Any]]:
    parent = _normalize_rel(parent_path_rel)
    with _connect() as conn:
        _ensure_schema(conn)
        rows = conn.execute(
            """
            SELECT path_rel, parent_path_rel, nombre, is_story_leaf
            FROM node
            WHERE parent_path_rel=?
            ORDER BY nombre COLLATE NOCASE ASC
            """,
            (parent,),
        ).fetchall()
    return [_row_to_dict(row) for row in rows if row is not None]


def get_node(path_rel: str) -> dict[str, Any] | None:
    target = _normalize_rel(path_rel)
    if not target:
        return {
            "path_rel": "",
            "parent_path_rel": None,
            "nombre": "biblioteca",
            "is_story_leaf": 0,
        }
    with _connect() as conn:
        _ensure_schema(conn)
        row = conn.execute(
            """
            SELECT path_rel, parent_path_rel, nombre, is_story_leaf
            FROM node
            WHERE path_rel=?
            """,
            (target,),
        ).fetchone()
    return _row_to_dict(row)


def get_story(story_path_rel: str) -> dict[str, Any] | None:
    target = _normalize_rel(story_path_rel)
    with _connect() as conn:
        _ensure_schema(conn)
        row = conn.execute(
            """
            SELECT story_path_rel, titulo, estado, meta_file, prompt_portada,
                   prompt_contraportada, notas, last_parsed_at
            FROM story
            WHERE story_path_rel=?
            """,
            (target,),
        ).fetchone()
    return _row_to_dict(row)


def list_story_pages(story_path_rel: str) -> list[dict[str, Any]]:
    target = _normalize_rel(story_path_rel)
    with _connect() as conn:
        _ensure_schema(conn)
        rows = conn.execute(
            """
            SELECT story_path_rel, numero, file_path, contenido, raw_frontmatter_json
            FROM page
            WHERE story_path_rel=?
            ORDER BY numero ASC
            """,
            (target,),
        ).fetchall()
    return [_row_to_dict(row) for row in rows if row is not None]


def get_story_page(story_path_rel: str, page_num: int) -> dict[str, Any] | None:
    target = _normalize_rel(story_path_rel)
    with _connect() as conn:
        _ensure_schema(conn)
        row = conn.execute(
            """
            SELECT story_path_rel, numero, file_path, contenido, raw_frontmatter_json
            FROM page
            WHERE story_path_rel=? AND numero=?
            """,
            (target, int(page_num)),
        ).fetchone()
    return _row_to_dict(row)


def list_page_slots(story_path_rel: str, page_num: int) -> list[dict[str, Any]]:
    target = _normalize_rel(story_path_rel)
    with _connect() as conn:
        _ensure_schema(conn)
        rows = conn.execute(
            """
            SELECT story_path_rel, page_num, slot, rol, prompt, orden, image_rel_path
            FROM page_image_slot
            WHERE story_path_rel=? AND page_num=?
            ORDER BY orden ASC, slot ASC
            """,
            (target, int(page_num)),
        ).fetchall()
    return [_row_to_dict(row) for row in rows if row is not None]


def get_page_slot(story_path_rel: str, page_num: int, slot_name: str) -> dict[str, Any] | None:
    target = _normalize_rel(story_path_rel)
    with _connect() as conn:
        _ensure_schema(conn)
        row = conn.execute(
            """
            SELECT story_path_rel, page_num, slot, rol, prompt, orden, image_rel_path
            FROM page_image_slot
            WHERE story_path_rel=? AND page_num=? AND slot=?
            """,
            (target, int(page_num), slot_name),
        ).fetchone()
    return _row_to_dict(row)


def list_slot_requirements(story_path_rel: str, page_num: int, slot_name: str) -> list[dict[str, Any]]:
    target = _normalize_rel(story_path_rel)
    with _connect() as conn:
        _ensure_schema(conn)
        rows = conn.execute(
            """
            SELECT id, story_path_rel, page_num, slot, tipo, ref, orden
            FROM page_slot_requirement
            WHERE story_path_rel=? AND page_num=? AND slot=?
            ORDER BY orden ASC, id ASC
            """,
            (target, int(page_num), slot_name),
        ).fetchall()
    return [_row_to_dict(row) for row in rows if row is not None]


def upsert_asset_index(rel_path: str) -> None:
    rel = rel_path.strip().replace("\\", "/")
    abs_path = (BASE_DIR / rel).resolve()
    if BASE_DIR.resolve() not in abs_path.parents:
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
            INSERT INTO asset_index(rel_path, kind, size, mtime_ns, is_present)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(rel_path) DO UPDATE SET
                kind=excluded.kind,
                size=excluded.size,
                mtime_ns=excluded.mtime_ns,
                is_present=excluded.is_present
            """,
            (rel, kind, size, mtime_ns, is_present),
        )
