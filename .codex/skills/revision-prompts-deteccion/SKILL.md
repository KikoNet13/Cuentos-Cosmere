---
name: revision-prompts-deteccion
description: Detectar hallazgos de prompts por severidad y pasada.
---

# Prompts Detección

Comando:
python -c "from app.editorial_orquestador import run_prompt_detection as f; r=f(inbox_book_title='El imperio final', book_rel_path='cosmere/nacidos-de-la-bruma-era-1/el-imperio-final', story_id='01', severity_band='major', pass_index=1); print(r['findings_json_rel']); print(r['alerts_open'])"
