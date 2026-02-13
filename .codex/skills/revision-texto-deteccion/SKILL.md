---
name: revision-texto-deteccion
description: Detectar hallazgos de texto por severidad y pasada.
---

# Texto Detección

Comando:
python -c "from app.editorial_orquestador import run_text_detection as f; r=f(inbox_book_title='El imperio final', book_rel_path='cosmere/nacidos-de-la-bruma-era-1/el-imperio-final', story_id='01', severity_band='critical', pass_index=1); print(r['findings_json_rel']); print(r['alerts_open'])"
