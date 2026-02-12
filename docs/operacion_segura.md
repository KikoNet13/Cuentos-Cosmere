# Operaci?n segura

## Pol?tica de comandos

1. No ejecutar comandos persistentes sin petici?n expl?cita.
2. Evitar por defecto `runserver`, observadores y bucles interactivos.
3. Preferir comprobaciones finitas (`--help`, scripts acotados).

## Pol?tica de validaci?n

1. Ejecutar validaciones finitas y reproducibles.
2. Registrar comandos y resultados en el archivo de tarea.
3. Documentar l?mites o validaciones omitidas con su motivo.

## Pol?tica de datos

1. La base SQLite se mantiene en `db/`.
2. Los archivos SQLite son estado local y no se versionan.
3. Importaci?n y respaldo deben ser mecanismos repetibles.

## Pol?tica de cambios

1. Trabajar una tarea planificada cada vez.
2. Mantener cambios acotados y reversibles.
3. Actualizar tarea, ?ndice y registro de cambios antes de cerrar.
