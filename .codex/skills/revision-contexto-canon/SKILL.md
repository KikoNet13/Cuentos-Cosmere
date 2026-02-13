---
name: revision-contexto-canon
description: Construir contexto jerárquico, glosario consolidado y canon PDF.
---

# Contexto Canon

Construye contexto y glosario del libro.

Comando:
python -c "from app.editorial_orquestador import run_contexto_canon as f; r=f(inbox_book_title='El imperio final', book_rel_path='cosmere/nacidos-de-la-bruma-era-1/el-imperio-final'); print(r['context_chain_rel']); print(r['glossary_merged_rel'])"
