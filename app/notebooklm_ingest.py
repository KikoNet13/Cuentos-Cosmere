from __future__ import annotations


class RemovedModuleError(RuntimeError):
    pass


def __getattr__(name: str):
    raise RemovedModuleError(
        "app.notebooklm_ingest fue retirado. La adaptacion editorial oficial vive en las skills adaptacion-* fuera de app/."
    )

