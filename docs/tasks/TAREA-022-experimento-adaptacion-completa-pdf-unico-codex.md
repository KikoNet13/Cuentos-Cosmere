# TAREA-022-experimento-adaptacion-completa-pdf-unico-codex

## Metadatos

- ID de tarea: `TAREA-022-experimento-adaptacion-completa-pdf-unico-codex`
- Fecha: 17/02/26 13:09
- Estado: cerrada
- Responsable: local
- ADR relacionadas: `0007`

## Objetivo

Generar una adaptacion editorial completa desde una fuente canonica unica (`library/_inbox/El imperio final.pdf`) y publicar una version nueva en `library/cosmere/nacidos-de-la-bruma-era-1/el-imperio-final-codex/`, con 8 cuentos de 16 paginas, sidecars de revision y preparacion visual para lote posterior con `imagegen`.

## Alcance implementado

1. Preflight canonico con PDF unico:
   - lectura de `library/_inbox/El imperio final.pdf` (899 paginas);
   - deteccion y validacion de capitulos `1..38`;
   - aborta si falta secuencia completa de capitulos.
2. Segmentacion editorial fija aplicada:
   - `01`: capitulos `1-5`
   - `02`: capitulos `6-10`
   - `03`: capitulos `11-15`
   - `04`: capitulos `16-20`
   - `05`: capitulos `21-24`
   - `06`: capitulos `25-29`
   - `07`: capitulos `30-34`
   - `08`: capitulos `35-38`
3. Generacion completa de salidas:
   - `01..08.json` en contrato vigente, `status=definitive`, `16` paginas por cuento;
   - `text.original/current` por pagina;
   - prompts de imagen detallados por pagina en `images.main.prompt`.
4. Sidecars de revision y contexto:
   - `adaptation_context.json` (glosario y decisiones editoriales operativas);
   - `NN.issues.json` por cuento;
   - `visual_bible.json` para continuidad visual y lote imagegen posterior.
5. Politica anti-spoiler aplicada para comunicacion:
   - aviso final por IDs no recomendados (`07`, `08`) sin resumen argumental.

## Decisiones

1. Canon exclusivo de esta tarea: `library/_inbox/El imperio final.pdf`.
2. Sin uso de internet para decisiones canonicas.
3. Estado final de cuentos: `definitive`.
4. Estilo de salida: lenguaje claro 5-12, sin tono caricaturesco.
5. Preparacion visual obligatoria para consistencia entre cuentos.

## Cambios aplicados

- Salidas editoriales:
  - `library/cosmere/nacidos-de-la-bruma-era-1/el-imperio-final-codex/01.json`
  - `library/cosmere/nacidos-de-la-bruma-era-1/el-imperio-final-codex/02.json`
  - `library/cosmere/nacidos-de-la-bruma-era-1/el-imperio-final-codex/03.json`
  - `library/cosmere/nacidos-de-la-bruma-era-1/el-imperio-final-codex/04.json`
  - `library/cosmere/nacidos-de-la-bruma-era-1/el-imperio-final-codex/05.json`
  - `library/cosmere/nacidos-de-la-bruma-era-1/el-imperio-final-codex/06.json`
  - `library/cosmere/nacidos-de-la-bruma-era-1/el-imperio-final-codex/07.json`
  - `library/cosmere/nacidos-de-la-bruma-era-1/el-imperio-final-codex/08.json`
  - `library/cosmere/nacidos-de-la-bruma-era-1/el-imperio-final-codex/_reviews/01.issues.json`
  - `library/cosmere/nacidos-de-la-bruma-era-1/el-imperio-final-codex/_reviews/02.issues.json`
  - `library/cosmere/nacidos-de-la-bruma-era-1/el-imperio-final-codex/_reviews/03.issues.json`
  - `library/cosmere/nacidos-de-la-bruma-era-1/el-imperio-final-codex/_reviews/04.issues.json`
  - `library/cosmere/nacidos-de-la-bruma-era-1/el-imperio-final-codex/_reviews/05.issues.json`
  - `library/cosmere/nacidos-de-la-bruma-era-1/el-imperio-final-codex/_reviews/06.issues.json`
  - `library/cosmere/nacidos-de-la-bruma-era-1/el-imperio-final-codex/_reviews/07.issues.json`
  - `library/cosmere/nacidos-de-la-bruma-era-1/el-imperio-final-codex/_reviews/08.issues.json`
  - `library/cosmere/nacidos-de-la-bruma-era-1/el-imperio-final-codex/_reviews/adaptation_context.json`
  - `library/cosmere/nacidos-de-la-bruma-era-1/el-imperio-final-codex/_reviews/visual_bible.json`
- Documentacion:
  - `docs/tasks/TAREA-022-experimento-adaptacion-completa-pdf-unico-codex.md`
  - `docs/tasks/INDICE.md`
  - `CHANGELOG.md`

## Validacion ejecutada

1. Generacion integral:
   - `python tmp/tarea022_generate_codex.py`
2. Verificacion estructural:
   - existen `01..08.json`;
   - cada cuento tiene `16` paginas y `status=definitive`;
   - cada pagina tiene `text.original/current` e `images.main`.
3. Verificacion de sidecars:
   - existen `01..08.issues.json`, `adaptation_context.json` y `visual_bible.json`.
4. Verificacion canonica de preflight:
   - deteccion de capitulos `1..38` antes de publicar salidas.

## Riesgos y notas

1. Aunque la salida es completa y usable, sigue recomendada una pasada editorial humana antes de imagenes definitivas.
2. `library/` esta ignorado globalmente en `.gitignore`; para versionar esta tarea se anaden de forma explicita solo los archivos del experimento `-codex`.

## Commit asociado

- Mensaje de commit: `Tarea 022: adaptacion completa desde PDF unico a version codex`
- Hash de commit: pendiente
