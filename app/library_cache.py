from __future__ import annotations


class RemovedModuleError(RuntimeError):
    pass


def __getattr__(name: str):
    raise RemovedModuleError(
        "app.library_cache fue retirado en TAREA-008. Usa catalog_provider y story_store."
    )
