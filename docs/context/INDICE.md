# Índice de contexto

## Alcance vigente

`docs/context/` queda mínimo y solo documenta dónde vive el contexto canónico.

## Contexto canónico

1. Cuentos finales por libro: `library/.../<book-node>/NN.json`.
2. Propuestas de entrada: `library/_inbox/<titulo-libro>/NN.md`.
3. Canon de referencia: PDFs dentro de `library/_inbox/<titulo-libro>/`.
4. Contexto jerárquico por nodos: `meta.md`, `anclas.md`, `glosario.md`, `canon.md`, `contexto.md`.
5. Sidecars consolidados por libro:
   - `_reviews/context_chain.json`
   - `_reviews/glossary_merged.json`
   - `_reviews/adaptation_profile.json`
   - `_reviews/context_review.json` (opcional, revisión ligera manual)
6. Skill operativa principal: `revision-orquestador-editorial`.

## Nota

No se mantienen documentos de prompts o canon editorial redundantes en `docs/context/`.
