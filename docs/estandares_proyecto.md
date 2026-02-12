# Est?ndares del proyecto

## Principios de ingenier?a de contexto

1. Mantener expl?citos los archivos fuente de verdad.
2. Separar activos de ejecuci?n y documentaci?n de proceso.
3. Reducir supuestos impl?citos mediante decisiones registradas.
4. Priorizar comandos repetibles frente a pasos manuales ad hoc.
5. Mantener tareas acotadas, revisables y trazables.

## Capas de documentaci?n

1. `AGENTS.md`: contrato de ejecuci?n y gobernanza.
2. `docs/adr/`: decisiones arquitect?nicas.
3. `docs/tasks/`: ciclo completo de cada tarea.
4. `CHANGELOG.md`: resumen ejecutivo breve.

## Disciplina de decisiones

1. Registrar el porqu?, no solo el qu?.
2. Crear ADR solo cuando cambie estructura, contrato o mantenimiento.
3. Enlazar tarea y ADR cuando exista relaci?n directa.

## Criterio de cierre de tarea

Una tarea se considera cerrada cuando:

1. El alcance acordado est? implementado.
2. Se ejecut? validaci?n finita y reproducible.
3. Se actualiz? archivo de tarea e ?ndice.
4. Se a?adi? entrada breve en `CHANGELOG.md`.
