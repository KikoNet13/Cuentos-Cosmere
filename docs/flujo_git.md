# Flujo Git

## Estrategia de ramas

- Rama ?nica: `main`.
- Sin ramas de funcionalidad por defecto.

## Convenci?n de commits

- Un commit por tarea planificada.
- Formato vigente: `tarea(TAREA-YYYYMMDD-HHMM): <resumen>`.

## Checklist de cierre

1. Archivo de tarea actualizado (`docs/tasks/TAREA-*.md`).
2. ?ndice de tareas actualizado (`docs/tasks/INDICE.md`).
3. Registro breve actualizado (`CHANGELOG.md`).
4. Validaciones finitas documentadas.
5. Commit ?nico de cierre creado.

## Configuraci?n local

1. `git init`
2. `git branch -M main`

## Configuraci?n remota

Cuando exista repositorio en GitHub:

1. `git remote add origin <repo-url>`
2. `git push -u origin main`
