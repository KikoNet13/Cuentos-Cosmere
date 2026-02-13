from __future__ import annotations


class RemovedModuleError(RuntimeError):
    pass


def __getattr__(name: str):
    raise RemovedModuleError(
        "app.notebooklm_ingest fue retirado en TAREA-008. El flujo oficial vive en la skill revision-orquestador-editorial."
    )

