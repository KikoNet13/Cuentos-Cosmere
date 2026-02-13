---
name: revision-prompts-decision-interactiva
description: Aplicar decisiones por finding en prompts.
---

# Prompts Decisión Interactiva

Comando:
python -c "from app.editorial_orquestador import run_prompt_decision_interactiva as f; r=f(inbox_book_title='El imperio final', book_rel_path='cosmere/nacidos-de-la-bruma-era-1/el-imperio-final', story_id='01', severity_band='major', pass_index=1); print(r['choices_json_rel']); print(r['applied_changes'])"
