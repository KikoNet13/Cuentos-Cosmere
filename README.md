# Generador de cuentos ilustrados

Proyecto local para revisar, adaptar y publicar cuentos ilustrados con fuente de verdad en JSON por cuento.

## Arquitectura vigente

- Fuente de verdad: `library/`.
- Contrato canonico: un cuento por archivo `NN.json` dentro de un nodo libro.
- `NN.json` guarda:
  - metadata de cuento
  - paginas con `text.original` y `text.current`
  - imagenes por slot (`main` obligatorio, `secondary` opcional)
  - alternativas de imagen con `active_id`
- Runtime sin SQLite: la app navega por escaneo directo de disco.
- Flujo editorial oficial: skill `revision-adaptacion-editorial`.

## Estructura canonica de libro

```text
library/<ruta-nodos>/.../<book-node>/
  01.json
  01.pdf                  # opcional referencia
  img_<uuid>_<slug>.png   # alternativas de imagen
  02.json
library/_inbox/           # propuestas de entrada (NN.md, NN.pdf)
library/_backups/         # opcional
```

## Comando CLI vigente

- `python manage.py runserver`

## Flujo recomendado

1. Dejar propuestas en `library/_inbox/<titulo-libro>/`.
2. Ejecutar trabajo editorial guiado con la skill `revision-adaptacion-editorial`.
3. Publicar/actualizar `NN.json` en `library/<nodos>/`.
4. Revisar en webapp la comparativa original/current y alternativas activas.

## Trazabilidad

- Operacion: `AGENTS.md`
- Tareas: `docs/tasks/`
- ADR: `docs/adr/`
- Historial breve: `CHANGELOG.md`
