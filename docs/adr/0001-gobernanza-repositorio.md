# 0001 - Gobernanza y trazabilidad del repositorio

- Estado: aceptado
- Fecha: 12/02/26

## Contexto

El proyecto es personal, pero requiere disciplina operativa profesional.
Las notas sueltas y el flujo ad hoc dificultan mantenimiento y trazabilidad.

## Decisión

Adoptar una base de gobernanza con:

- `AGENTS.md` como contrato de ejecución
- archivos de tarea en `docs/tasks/`
- `CHANGELOG.md` breve con enlace a tareas
- un commit por tarea planificada sobre `main`

## Consecuencias

- Mejora la trazabilidad y la repetibilidad.
- Aumenta el coste mínimo de documentación por tarea.
- Fortalece el mantenimiento a largo plazo.
