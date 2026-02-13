---
name: revision-orquestador-editorial
description: Orquestar el flujo completo por libro con cascada por severidad y gates.
---

# Orquestador Editorial

Comando:
python -c "from app.editorial_orquestador import run_orquestador_editorial as f; r=f(inbox_book_title='El imperio final', book_rel_path='cosmere/nacidos-de-la-bruma-era-1/el-imperio-final'); print(r['phase']); print(r['pipeline_state_rel'])"
