from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .config import BASE_DIR, DATA_ROOT

PAGE_FILE_RE = re.compile(r"^(\d{3})\.md$")
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp")
RELEVANT_EXTS = (".md", ".png", ".jpg", ".jpeg", ".webp", ".pdf", ".json")


@dataclass
class RequirementSpec:
    tipo: str
    ref: str
    orden: int = 0


@dataclass
class ImageSlotSpec:
    slot: str
    rol: str
    prompt: str
    requisitos: list[RequirementSpec] = field(default_factory=list)
    orden: int = 0
    image_rel_path: str = ""


@dataclass
class StoryPage:
    numero: int
    file_rel: str
    contenido: str
    raw_frontmatter_json: str
    image_slots: list[ImageSlotSpec]
    warnings: list[str] = field(default_factory=list)


@dataclass
class StoryMeta:
    titulo: str
    slug: str
    prompt_portada: str
    prompt_contraportada: str
    estado: str
    notas: str
    raw_frontmatter_json: str


@dataclass
class StoryData:
    story_path_rel: str
    meta_file_rel: str
    meta: StoryMeta
    pages: list[StoryPage]
    warnings: list[str] = field(default_factory=list)


@dataclass
class NodeData:
    path_rel: str
    parent_path_rel: str | None
    nombre: str
    is_story_leaf: bool


@dataclass
class AssetInfo:
    rel_path: str
    kind: str
    size: int
    mtime_ns: int
    exists: bool


@dataclass
class LibrarySnapshot:
    nodes: list[NodeData]
    stories: list[StoryData]
    assets: list[AssetInfo]
    warnings: list[str]


def relevant_files(root: Path | None = None) -> list[Path]:
    root_dir = (root or DATA_ROOT).resolve()
    files: list[Path] = []
    for p in root_dir.rglob("*"):
        if p.is_file() and p.suffix.lower() in RELEVANT_EXTS:
            files.append(p)
    files.sort(key=lambda x: x.as_posix())
    return files


def _to_rel_from_data_root(path: Path) -> str:
    return path.resolve().relative_to(DATA_ROOT.resolve()).as_posix()


def _to_rel_from_base(path: Path) -> str:
    return path.resolve().relative_to(BASE_DIR.resolve()).as_posix()


def _slug_slot(slot: str) -> str:
    slug = re.sub(r"[^a-z0-9-]+", "-", slot.lower().strip()).strip("-")
    return slug or "slot"


def _normalize_role(raw: str) -> str:
    value = raw.strip().lower()
    if value in {"principal", "secundaria", "referencia"}:
        return value
    return "secundaria"


def _parse_kv(text: str) -> tuple[str, str] | None:
    if ":" not in text:
        return None
    key, value = text.split(":", 1)
    key = key.strip()
    if not key:
        return None
    return key, value.strip()


def _parse_scalar(value: str) -> str:
    raw = value.strip()
    if raw == "":
        return ""
    if raw.startswith('"') and raw.endswith('"') and len(raw) >= 2:
        return raw[1:-1].replace('\\"', '"')
    if raw.startswith("'") and raw.endswith("'") and len(raw) >= 2:
        return raw[1:-1].replace("\\'", "'")
    return raw


def _split_frontmatter(raw: str) -> tuple[list[str], str, list[str]]:
    warnings: list[str] = []
    lines = raw.splitlines()
    if not lines or lines[0].strip() != "---":
        return [], raw, warnings
    end_idx = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break
    if end_idx is None:
        warnings.append("Frontmatter sin cierre '---'.")
        return [], raw, warnings
    fm_lines = lines[1:end_idx]
    body = "\n".join(lines[end_idx + 1 :]).lstrip("\n")
    return fm_lines, body, warnings


def _parse_meta_frontmatter(fm_lines: list[str]) -> tuple[dict[str, Any], list[str]]:
    data: dict[str, Any] = {}
    warnings: list[str] = []
    for line in fm_lines:
        stripped = line.strip()
        if not stripped:
            continue
        parsed = _parse_kv(stripped)
        if not parsed:
            warnings.append(f"Linea invalida en frontmatter meta: {line}")
            continue
        key, value = parsed
        data[key] = _parse_scalar(value)
    return data, warnings


def _parse_page_frontmatter(fm_lines: list[str]) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    data: dict[str, Any] = {"pagina": None, "imagenes": []}
    idx = 0
    total = len(fm_lines)
    while idx < total:
        line = fm_lines[idx]
        stripped = line.strip()
        if not stripped:
            idx += 1
            continue
        parsed = _parse_kv(stripped)
        if not parsed:
            warnings.append(f"Linea invalida en frontmatter pagina: {line}")
            idx += 1
            continue
        key, value = parsed
        if key != "imagenes":
            data[key] = _parse_scalar(value)
            idx += 1
            continue

        if value and value != "[]":
            warnings.append("Campo imagenes debe usar bloque de lista o []")
        if value == "[]":
            idx += 1
            continue
        idx += 1
        slot_order = 0
        while idx < total and fm_lines[idx].startswith("  - "):
            slot_data: dict[str, Any] = {"slot": "", "rol": "secundaria", "prompt": "", "requisitos": []}
            first_item = fm_lines[idx][4:].strip()
            if first_item:
                item_kv = _parse_kv(first_item)
                if item_kv:
                    slot_data[item_kv[0]] = _parse_scalar(item_kv[1])
            idx += 1
            while idx < total and fm_lines[idx].startswith("    "):
                field = fm_lines[idx][4:].strip()
                if not field:
                    idx += 1
                    continue
                if field.startswith("requisitos:"):
                    req_value = field.split(":", 1)[1].strip()
                    if req_value == "[]":
                        idx += 1
                        continue
                    if req_value not in {"", "[]"}:
                        warnings.append(f"Formato de requisitos no soportado: {field}")
                        idx += 1
                        continue
                    idx += 1
                    req_order = 0
                    while idx < total and fm_lines[idx].startswith("      - "):
                        req_data = {"tipo": "", "ref": "", "orden": req_order}
                        first_req = fm_lines[idx][8:].strip()
                        if first_req:
                            req_kv = _parse_kv(first_req)
                            if req_kv:
                                req_data[req_kv[0]] = _parse_scalar(req_kv[1])
                        idx += 1
                        while idx < total and fm_lines[idx].startswith("        "):
                            sub_line = fm_lines[idx][8:].strip()
                            sub_kv = _parse_kv(sub_line) if sub_line else None
                            if sub_kv:
                                req_data[sub_kv[0]] = _parse_scalar(sub_kv[1])
                            idx += 1
                        if req_data.get("tipo") and req_data.get("ref"):
                            slot_data["requisitos"].append(req_data)
                            req_order += 1
                    continue
                field_kv = _parse_kv(field)
                if field_kv:
                    slot_data[field_kv[0]] = _parse_scalar(field_kv[1])
                else:
                    warnings.append(f"Campo de imagen invalido: {field}")
                idx += 1
            slot_name = str(slot_data.get("slot", "")).strip()
            if slot_name:
                slot_data["rol"] = _normalize_role(str(slot_data.get("rol", "")))
                slot_data["orden"] = slot_order
                data["imagenes"].append(slot_data)
                slot_order += 1
            else:
                warnings.append("Imagen sin slot en frontmatter de pagina.")
        continue
    return data, warnings


def _resolve_slot_image_rel(story_path_rel: str, page_num: int, slot: str) -> str:
    story_abs = DATA_ROOT / story_path_rel
    images_dir = story_abs / "assets" / "imagenes"
    base_name = f"pagina-{page_num:03d}-{_slug_slot(slot)}"
    for ext in IMAGE_EXTS:
        candidate = images_dir / f"{base_name}{ext}"
        if candidate.exists():
            return _to_rel_from_base(candidate)
    fallback = images_dir / f"{base_name}.png"
    return _to_rel_from_base(fallback)


def _story_is_leaf(story_dir: Path) -> bool:
    meta = story_dir / "meta.md"
    page_files = [p for p in story_dir.iterdir() if p.is_file() and PAGE_FILE_RE.fullmatch(p.name)]
    return meta.exists() and bool(page_files)


def load_story(story_path_rel: str) -> StoryData:
    story_abs = DATA_ROOT / story_path_rel
    story_warnings: list[str] = []

    raw_meta = (story_abs / "meta.md").read_text(encoding="utf-8", errors="replace")
    meta_fm_lines, meta_body, meta_split_warn = _split_frontmatter(raw_meta)
    story_warnings.extend(meta_split_warn)
    meta_fm, meta_parse_warn = _parse_meta_frontmatter(meta_fm_lines)
    story_warnings.extend(meta_parse_warn)

    meta = StoryMeta(
        titulo=str(meta_fm.get("titulo", story_abs.name)),
        slug=str(meta_fm.get("slug", story_abs.name)),
        prompt_portada=str(meta_fm.get("prompt_portada", "")),
        prompt_contraportada=str(meta_fm.get("prompt_contraportada", "")),
        estado=str(meta_fm.get("estado", "activo")),
        notas=meta_body.strip(),
        raw_frontmatter_json=json.dumps(meta_fm, ensure_ascii=False),
    )

    pages: list[StoryPage] = []
    for page_file in sorted(story_abs.iterdir(), key=lambda p: p.name):
        if not page_file.is_file():
            continue
        m = PAGE_FILE_RE.fullmatch(page_file.name)
        if not m:
            continue
        file_num = int(m.group(1))
        raw_page = page_file.read_text(encoding="utf-8", errors="replace")
        fm_lines, body, page_split_warn = _split_frontmatter(raw_page)
        page_frontmatter, page_parse_warn = _parse_page_frontmatter(fm_lines)
        page_warnings = list(page_split_warn) + list(page_parse_warn)
        page_num = file_num
        try:
            fm_num = int(str(page_frontmatter.get("pagina", "")).strip())
            if fm_num > 0 and fm_num != file_num:
                page_warnings.append(
                    f"Pagina declarada {fm_num} no coincide con archivo {file_num:03d}. Se usa {file_num:03d}."
                )
        except ValueError:
            pass

        slots: list[ImageSlotSpec] = []
        for item in page_frontmatter.get("imagenes", []):
            reqs = [
                RequirementSpec(
                    tipo=str(req.get("tipo", "")).strip(),
                    ref=str(req.get("ref", "")).strip(),
                    orden=int(req.get("orden", 0)),
                )
                for req in item.get("requisitos", [])
                if str(req.get("tipo", "")).strip() and str(req.get("ref", "")).strip()
            ]
            slot_name = str(item.get("slot", "")).strip()
            if not slot_name:
                continue
            slots.append(
                ImageSlotSpec(
                    slot=slot_name,
                    rol=_normalize_role(str(item.get("rol", ""))),
                    prompt=str(item.get("prompt", "")),
                    requisitos=reqs,
                    orden=int(item.get("orden", 0)),
                    image_rel_path=_resolve_slot_image_rel(story_path_rel, page_num, slot_name),
                )
            )

        pages.append(
            StoryPage(
                numero=page_num,
                file_rel=_to_rel_from_base(page_file),
                contenido=body.strip(),
                raw_frontmatter_json=json.dumps(page_frontmatter, ensure_ascii=False),
                image_slots=slots,
                warnings=page_warnings,
            )
        )

    return StoryData(
        story_path_rel=story_path_rel,
        meta_file_rel=_to_rel_from_base(story_abs / "meta.md"),
        meta=meta,
        pages=sorted(pages, key=lambda p: p.numero),
        warnings=story_warnings,
    )


def scan_library() -> LibrarySnapshot:
    root = DATA_ROOT.resolve()
    nodes: list[NodeData] = []
    stories: list[StoryData] = []
    warnings: list[str] = []

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        filenames.sort()
        path = Path(dirpath)
        rel = path.relative_to(root).as_posix()
        rel = "" if rel == "." else rel
        parent = Path(rel).parent.as_posix() if rel else None
        if parent == ".":
            parent = ""
        is_leaf = ("meta.md" in filenames) and any(PAGE_FILE_RE.fullmatch(name) for name in filenames)
        nodes.append(
            NodeData(
                path_rel=rel,
                parent_path_rel=parent,
                nombre=path.name if rel else "biblioteca",
                is_story_leaf=is_leaf,
            )
        )
        if is_leaf:
            story = load_story(rel)
            warnings.extend(f"[{rel}] {w}" for w in story.warnings)
            for page in story.pages:
                warnings.extend(f"[{rel}/{page.numero:03d}] {w}" for w in page.warnings)
            stories.append(story)

    assets: list[AssetInfo] = []
    for file_path in relevant_files(root):
        stat = file_path.stat()
        rel = _to_rel_from_base(file_path)
        ext = file_path.suffix.lower()
        kind = "other"
        if ext == ".md":
            kind = "md"
        elif ext == ".pdf":
            kind = "pdf"
        elif ext in IMAGE_EXTS:
            kind = "image"
        elif ext == ".json":
            kind = "json"
        assets.append(
            AssetInfo(
                rel_path=rel,
                kind=kind,
                size=stat.st_size,
                mtime_ns=stat.st_mtime_ns,
                exists=True,
            )
        )

    nodes.sort(key=lambda n: (n.path_rel.count("/"), n.path_rel))
    stories.sort(key=lambda s: s.story_path_rel)
    assets.sort(key=lambda a: a.rel_path)
    return LibrarySnapshot(nodes=nodes, stories=stories, assets=assets, warnings=warnings)


def resolve_requirement_paths(story_path_rel: str, ref_value: str) -> list[str]:
    ref = ref_value.strip().replace("\\", "/")
    if not ref:
        return []

    story_abs = (DATA_ROOT / story_path_rel).resolve()
    candidates: list[Path] = []

    p_ref = Path(ref)
    if p_ref.is_absolute():
        candidates.append(p_ref)
    else:
        candidates.append((story_abs / ref).resolve())
        candidates.append((DATA_ROOT / ref).resolve())
        candidates.append((BASE_DIR / ref).resolve())
        candidates.append((BASE_DIR / "biblioteca" / ref).resolve())

    root = BASE_DIR.resolve()
    resolved: list[str] = []
    for cand in candidates:
        if not cand.exists():
            continue
        if cand.is_file():
            if cand.suffix.lower() in IMAGE_EXTS and root in cand.parents:
                rel = cand.relative_to(root).as_posix()
                if rel not in resolved:
                    resolved.append(rel)
            continue
        if cand.is_dir():
            for item in sorted(cand.iterdir()):
                if item.is_file() and item.suffix.lower() in IMAGE_EXTS and root in item.parents:
                    rel = item.relative_to(root).as_posix()
                    if rel not in resolved:
                        resolved.append(rel)
    return resolved
