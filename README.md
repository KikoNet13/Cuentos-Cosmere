# Generador de cuentos ilustrados

Proyecto local para preparar cuentos ilustrados con fuente de verdad en
archivos y caché SQLite temporal para navegación rápida.

## Arquitectura vigente

- Fuente de verdad: `biblioteca/`.
- Contrato de cuento: `meta.md` + páginas `NNN.md`.
- Frontmatter de contenido en castellano (`pagina`, `imagenes`, `requisitos`).
- Caché temporal: `db/library_cache.sqlite`.
- UI: lectura/copia de texto y prompts, subida o pegado de imágenes por slot.

## Estructura canónica de cuento

```text
biblioteca/<ruta-nodos>/.../<cuento>/
  meta.md
  001.md
  002.md
  ...
  assets/
    imagenes/
      pagina-001-principal.png
  referencias/
    referencia.pdf
```

## Comandos CLI vigentes

- `python manage.py rebuild-cache`
- `python manage.py migrate-library-layout --dry-run`
- `python manage.py migrate-library-layout --apply`
- `python manage.py runserver`

## Flujo recomendado

1. Ejecutar migración de layout si hay material legacy:
   `python manage.py migrate-library-layout --apply`
2. Reconstruir caché:
   `python manage.py rebuild-cache`
3. Levantar servidor solo cuando se solicite explícitamente:
   `python manage.py runserver`

## Trazabilidad

- Operación: `AGENTS.md`
- Tareas: `docs/tasks/`
- ADR: `docs/adr/`
- Historial breve: `CHANGELOG.md`
