# Checklist operativo

## Antes

- Confirmar libro en `library/_inbox/<titulo-libro>/`.
- Confirmar ruta destino en `library/<nodos>/`.
- Confirmar que el cuento de destino usa `NN.json`.

## Durante

- Conservar fuente en `text.original` y `prompt.original`.
- Aplicar adaptaciones en `text.current` y `prompt.current`.
- Mantener `images.main` obligatorio.
- Crear `images.secondary` solo si aporta valor editorial.
- Guardar alternativas de imagen con `id` y `asset_rel_path`.
- Definir `active_id` por slot.

## Despues

- Verificar JSON valido.
- Verificar pagina por pagina en la UI.
- Verificar slot main/secondary y alternativa activa.
- Registrar trazabilidad en tarea/changelog.
