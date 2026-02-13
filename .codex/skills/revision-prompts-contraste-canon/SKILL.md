---
name: revision-prompts-contraste-canon
description: Contrastar prompts contra canon y continuidad visual.
---

# Prompts Contraste Canon

Comando:
python -c "from app.editorial_orquestador import run_prompt_contrast_canon as f; r=f(inbox_book_title='El imperio final', book_rel_path='cosmere/nacidos-de-la-bruma-era-1/el-imperio-final', story_id='01', severity_band='major'); print(r['contrast_json_rel']); print(r['alerts'])"
