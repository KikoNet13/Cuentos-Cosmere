# Registro de cambios

Registro breve de cambios relevantes.
El detalle operativo vive en `docs/tasks/`.

## [Sin publicar]

## [12/02/26] - Reestructuración Página/Ancla/Imagen

- Se introdujo el modelo v3: `Pagina`, `Ancla`, `AnclaVersion`, `Imagen`
  e `ImagenRequisito`.
- Se añadió migración estructural `migrate-models-v3` con migración de
  datos legacy y alias deprecados.
- Se rehizo la UI de cuento para navegación por página, edición de texto,
  gestión de imágenes y requisitos visuales.
- Se agregó vista de gestión de anclas por saga.
- Tarea: `docs/tasks/TAREA-003-reestructuracion-pagina-ancla-imagen-ui.md`.

## [12/02/26] - Paginación adaptativa por archivo importado

- Se eliminó la expectativa fija de páginas en importación y UI.
- El total de páginas ahora depende del archivo `origen_md.md` importado.
- Se actualizó el canon documental para tratar 16 páginas como perfil
  recomendado, no obligatorio.
- Tarea: `docs/tasks/TAREA-002-paginacion-adaptativa-archivo-importado.md`.

## [12/02/26] - Base de gobernanza

- Se definió la base de gobernanza del repositorio y su trazabilidad.
- Se incorporó el sistema de ADR y tareas con índice dedicado.
- Se curaron activos heredados en rutas canónicas dentro de `docs/`.
- Se formalizó la política de SQLite local en `.gitignore`.
- Tarea: `docs/tasks/TAREA-001-proyecto-profesional-contexto.md`.