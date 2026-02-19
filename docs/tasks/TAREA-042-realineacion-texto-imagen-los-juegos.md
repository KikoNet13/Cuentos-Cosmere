# TAREA-042 - Realineacion texto-imagen en Los juegos del hambre

- Fecha: 19/02/26 13:47
- Estado: cerrada
- Responsable: Codex
- ADR relacionadas: `0008`

## Resumen
Se corrige un desfase narrativo en `library/los_juegos_del_hambre/01.json` donde texto, prompt e imagen estaban corridos en el tramo final de la Cosecha. Se auditan tambien los cuentos `02..11` con una regla lexica de alta confianza y no se detectan mas casos para autocorreccion.

## Alcance aplicado
1. Correccion editorial en `01.json` sin modificar textos de `p1..p16`.
2. Liberacion de `p11` y `p12` para regeneracion (`prompt + reference_ids`, sin imagen activa).
3. Conservacion de 2 imagenes sobrantes como alternativas inactivas:
- `p15` conserva activa la escena alineada y agrega la alternativa heredada de `p14`.
- `p16` conserva activa la escena de cierre y agrega la alternativa heredada de `p15`.
4. Auditoria automatizada de `01..11` con score Jaccard por pagina.
5. Actualizacion documental en `docs/tasks/INDICE.md` y `CHANGELOG.md`.

## Regla de auditoria de alta confianza
Se evalua cada cuento para `n = 13, 14, 15`:

`score(text_n, prompt_{n-2}) > score(text_n, prompt_n) + 0.01`

Un cuento es candidato solo si las 3 paginas cumplen simultaneamente.

## Resultado de auditoria (`01..11`)
- `01.json`: candidato `True`
  - `n13`: self=`0.015152`, minus2=`0.060606`, ok=`True`
  - `n14`: self=`0.023438`, minus2=`0.040650`, ok=`True`
  - `n15`: self=`0.015038`, minus2=`0.078125`, ok=`True`
- `02.json`: candidato `False`
- `03.json`: candidato `False`
- `04.json`: candidato `False`
- `05.json`: candidato `False`
- `06.json`: candidato `False`
- `07.json`: candidato `False`
- `08.json`: candidato `False`
- `09.json`: candidato `False`
- `10.json`: candidato `False`
- `11.json`: candidato `False`

## Correccion aplicada en `01.json`
1. Reasignacion de slots:
- `p13 <- p11` (slot visual completo).
- `p14 <- p12` (slot visual completo).
- `p15 <- p13` como activo + alternativa inactiva heredada de `p14`.
- `p16` mantiene activo de cierre (`p16`) + alternativa inactiva heredada de `p15`.

2. `p11` y `p12` en estado de regeneracion:
- `status = draft`
- `active_id = ""`
- `alternatives = []`
- Prompt regenerado y alineado al texto.
- `reference_ids` minimos:
  - `p11`: `anchors/char-effie.png`, `anchors/env-reaping-square.png`
  - `p12`: `anchors/char-effie.png`, `anchors/char-prim.png`, `anchors/env-reaping-square.png`

3. Integridad:
- No se borran ni mueven archivos en `library/los_juegos_del_hambre/images/01/`.
- Se actualiza `updated_at` del cuento.

## Validaciones ejecutadas
1. Ayuda CLI (validacion finita):
- `python manage.py --help`

2. Validacion estructural y de assets activos en `01..11`:
- Parse JSON (`utf-8-sig`) correcto.
- Secuencia `1..16` correcta en todos los cuentos.
- Presencia de `status`, `prompt`, `active_id`, `alternatives` en cada `pages[].images.main`.
- Verificacion de `active_id` contra `alternatives` y existencia fisica de `asset_rel_path`.
- Resultado: `VALIDATION_OK=01..11 json/slots/assets`.

3. Verificacion puntual del cuento `01`:
- `p11` y `p12` quedan pendientes (prompt presente sin imagen activa).
- `p13..p16` quedan realineadas segun mapeo.
- `p15` y `p16` quedan con 2 alternativas cada una (1 activa + 1 inactiva).

## Archivos modificados
- `library/los_juegos_del_hambre/01.json`
- `docs/tasks/TAREA-042-realineacion-texto-imagen-los-juegos.md`
- `docs/tasks/INDICE.md`
- `CHANGELOG.md`
