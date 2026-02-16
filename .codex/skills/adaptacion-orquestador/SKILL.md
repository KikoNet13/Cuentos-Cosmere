---
name: "adaptacion-orquestador"
description: "Orquesta en modo conversacional el flujo completo de adaptacion de propuestas inbox a version definitiva usando solo scripts dentro de skills, nunca logica editorial en app/."
---

# Skill: adaptacion-orquestador

## Objetivo
- Coordinar el flujo editorial completo por cuento y libro:
  - `contexto -> texto -> prompts -> cierre`
- Convertir propuestas `library/_inbox/.../NN.md` en `library/.../NN.json` con estado final `definitive` cuando no queden hallazgos abiertos.

## Regla de frontera obligatoria
- `app/` es solo webapp Flask de visualizacion/edicion.
- Toda logica editorial vive en scripts de skills.
- Este orquestador no usa `app.editorial_orquestador` ni agrega pipeline en `app/`.

## Scripts del modulo
- `scripts/orquestar.py`
- `scripts/adaptacion_lib.py` (utilidades compartidas)

## Modulos que coordina
- `../adaptacion-contexto/scripts/contexto.py`
- `../adaptacion-texto/scripts/texto.py`
- `../adaptacion-prompts/scripts/prompts.py`
- `../adaptacion-cierre/scripts/cierre.py`

## Protocolo conversacional
1. Pedir `target_age` si no viene dado. Es obligatorio.
2. Lanzar contexto y confirmar inventario detectado en inbox.
3. Procesar texto por bloques de severidad: `critical -> major -> minor -> info`.
4. Para cada hallazgo, presentar propuestas IA (1-3) y opcion `D` libre humana.
5. Aplicar decisiones en texto con trazabilidad.
6. Repetir ciclo por severidad para `prompt.main` (visual gate).
7. Ejecutar cierre y confirmar:
   - `definitive` si hay cero hallazgos abiertos.
   - `in_review` si queda alguno abierto.

## Contrato de sidecars
- Maestro por cuento: `library/<book>/_reviews/NN.review.json`
- Log de decisiones: `library/<book>/_reviews/NN.decisions.log.jsonl`
- Legacy sidecars previos se limpian al arrancar el nuevo flujo.

