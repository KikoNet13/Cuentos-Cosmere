# Prompts de im?genes master Era 1

## Uso previsto

Este documento sirve para:

- crear un Proyecto de ChatGPT para im?genes
- mantener consistencia visual entre p?ginas
- trabajar por p?gina con prompts listos para copiar
- ejecutar piloto de `L01P01` p?ginas `1-8`

## Archivos a subir al Proyecto

- `docs/context/flujo_revision.md`
- `docs/context/checklist_revision.md`
- `docs/context/glosario_simplificado_mistborn.md`
- `docs/context/lista_cambios_bloques_1_3.md`
- `biblioteca/nacidos-de-la-bruma-era-1/el-imperio-final/01/textos/origen_md.md`
- `biblioteca/nacidos-de-la-bruma-era-1/el-imperio-final/02/textos/origen_md.md`
- `biblioteca/nacidos-de-la-bruma-era-1/el-imperio-final/03/textos/origen_md.md`
- `biblioteca/.../01/textos/referencia_pdf.pdf`
- `biblioteca/.../02/textos/referencia_pdf.pdf`
- `biblioteca/.../03/textos/referencia_pdf.pdf`
- `docs/assets/style_refs/photo_2026-02-11_15-28-12.jpg`
- `docs/assets/style_refs/photo_2026-02-11_15-28-15.jpg`
- `docs/assets/style_refs/photo_2026-02-11_15-28-17.jpg`

## Instrucciones globales del Proyecto

Pegar este bloque en instrucciones del Proyecto:

```text
Eres director de arte para cuentos infantiles de Mistborn Era 1.

Objetivo:
- Mantener consistencia visual estricta entre im?genes.
- Mantener identidad de personajes entre escenas.
- Mantener coherencia de mundo y tono infantil 7-9 a?os.

Jerarqu?a de verdad:
1. Si una escena fue validada en `.md`, la imagen sigue ese `.md`.
2. Si no hay adaptaci?n, prioriza fidelidad al canon base.
3. Glosario y checklist corrigen t?rminos y reglas.
4. Si hay conflicto no resuelto, bloquea la generaci?n.

Reglas visuales:
- Estilo de cuento ilustrado, no fotorealista.
- Formato cuadrado 1:1.
- Sin texto incrustado, logos ni marcas de agua.
- Sin elementos modernos fuera del mundo narrativo.
- Sin cambios arbitrarios de rasgos f?sicos.
- Violencia sin detalle gr?fico.

Comportamiento de salida:
- Recibir prompt de escena y generar imagen directamente.
- No reformular prompt.
- No a?adir explicaci?n extra.
- Si hay conflicto can?nico, bloquear en 1-2 l?neas.
```

## Biblia visual global

### Estilo art?stico

- Ilustraci?n infantil de trazo manual.
- Contorno oscuro suave.
- Color plano con textura ligera de papel.
- Expresiones faciales claras y consistentes.
- Composici?n limpia y lectura inmediata.

### Mundo y atm?sfera

- Imperio Final opresivo con ceniza y bruma baja.
- Cielos fr?os o rojizos seg?n escena.
- Arquitectura imperial sobria de piedra y metal.
- Vegetaci?n apagada salvo contraste narrativo expl?cito.

### Paleta base

- Dominantes: gris ceniza, azul gris?ceo y marr?n apagado.
- Acentos: rojo desaturado, cobre tenue y dorado envejecido.
- Color emocional puntual sin romper la atm?sfera.

### Prohibiciones

- No anime.
- No 3D pl?stico.
- No fotorrealismo.
- No ne?n futurista.
- No armas modernas.
- No texto en imagen.

## Fichas ancla

### Vin

- ID: `VIN_BASE`
- Edad aparente: 11-13.
- Rasgos: baja estatura, delgada, cabello corto oscuro, mirada alerta.
- Vestuario: ropa gastada gris o marr?n.
- Prohibiciones: no cabello largo, no vestuario noble, no adulta.

### Kelsier

- ID: `KELSIER_BASE`
- Edad aparente: 30s.
- Rasgos: atl?tico, cicatrices en antebrazos, sonrisa confiada.
- Vestuario: ropa oscura funcional, capa de tiras en escenas nocturnas.
- Prohibiciones: no armadura brillante, no gesto severo permanente.

### Inquisidor de acero

- ID: `INQUISIDOR_BASE`
- Rasgos: clavos met?licos en lugar de ojos, silueta alta amenazante.
- Vestuario: t?nica oscura imperial sobria.
- Prohibiciones: no gore, no caricatura c?mica, no monstruo fuera canon.

### Camon

- ID: `CAMON_BASE`
- Rasgos: expresi?n avara, porte de l?der de banda menor.
- Vestuario: ropa urbana gastada de ladr?n en Luthadel.
- Prohibiciones: no aspecto noble, no aspecto heroico.

## Prompts ancla obligatorios

Generar estas cuatro im?genes antes del piloto.

### Ancla 1 Vin

```text
Ilustraci?n infantil estilo cuento cl?sico, formato 1:1, trazo manual,
contorno oscuro suave y textura ligera de papel. Vin ni?a de 11-13, baja,
delgada, cabello corto oscuro hasta las orejas, ropa gastada gris y marr?n,
expresi?n alerta en callej?n de Luthadel con ceniza y luz fr?a. Sin texto.
```

### Ancla 2 Kelsier

```text
Ilustraci?n infantil estilo cuento cl?sico, formato 1:1, trazo manual,
contorno oscuro suave y textura ligera de papel. Kelsier adulto atl?tico,
cicatrices visibles en antebrazos, sonrisa confiada, ropa oscura funcional y
capa de tiras grises. Noche con bruma y ceniza en Luthadel. Sin texto.
```

### Ancla 3 Inquisidor

```text
Ilustraci?n infantil estilo cuento cl?sico, formato 1:1, trazo manual,
contorno oscuro suave y textura ligera de papel. Inquisidor de acero muy alto,
t?nica imperial oscura, clavos met?licos en lugar de ojos, postura amenazante,
calle de Luthadel con ceniza y bruma. Tono infantil sin gore. Sin texto.
```

### Ancla 4 Camon

```text
Ilustraci?n infantil estilo cuento cl?sico, formato 1:1, trazo manual,
contorno oscuro suave y textura ligera de papel. Camon l?der de banda,
expresi?n mandona y desconfiada, ropa urbana gastada en tonos apagados,
interior pobre de escondite en Luthadel con ceniza en ventanas. Sin texto.
```

## Contrato por prompt de escena

Cada prompt debe incluir:

1. n?mero de p?gina
2. tipo de plano
3. personajes visibles
4. acci?n principal
5. ambiente y paleta
6. restricciones de consistencia

Plantilla base:

```text
P?gina: <N>
Plano: <general|medio|detalle>
Personajes: <lista>
Acci?n: <acci?n principal>
Ambiente: <atm?sfera, luz, paleta>
Consistencia: igualar rasgos de anclas y mantener vestuario base.
Salida: generar imagen 1:1 sin texto ni explicaci?n adicional.
```

## Piloto L01P01 p?ginas 1-8

### P?gina 1

```text
P?gina: 1
Plano: general
Personajes: paisaje sin personaje principal
Acci?n: mostrar cielo rojizo, ceniza cayendo y ciudad triste
Ambiente: gris ceniza, rojo apagado, bruma baja
Consistencia: estilo cuento infantil, sin elementos modernos
Salida: imagen 1:1 sin texto
```

### P?gina 2

```text
P?gina: 2
Plano: medio
Personajes: Kelsier
Acci?n: Kelsier sonriente con cicatrices visibles en antebrazos
Ambiente: exterior urbano de Luthadel con ceniza en suspensi?n
Consistencia: igualar rasgos de KELSIER_BASE
Salida: imagen 1:1 sin texto
```

### P?gina 3

```text
P?gina: 3
Plano: general
Personajes: Kelsier y trabajadores
Acci?n: distracci?n en plantaci?n para permitir huida parcial
Ambiente: noche gris con tensi?n controlada
Consistencia: violencia sugerida sin detalle gr?fico
Salida: imagen 1:1 sin texto
```

### P?gina 4

```text
P?gina: 4
Plano: medio
Personajes: Kelsier
Acci?n: promesa de esperanza antes de partir hacia Luthadel
Ambiente: camino con niebla y ceniza suave
Consistencia: mantener capa y gesto c?lido de Kelsier
Salida: imagen 1:1 sin texto
```

### P?gina 5

```text
P?gina: 5
Plano: medio
Personajes: Vin
Acci?n: Vin escondida observando desde un rinc?n oscuro
Ambiente: interior pobre y sombr?o
Consistencia: igualar rasgos de VIN_BASE
Salida: imagen 1:1 sin texto
```

### P?gina 6

```text
P?gina: 6
Plano: detalle
Personajes: Vin y figura secundaria desenfocada
Acci?n: Vin usa suerte para calmar tensi?n
Ambiente: luz tenue con foco en expresi?n de Vin
Consistencia: tono infantil, sin dramatismo extremo
Salida: imagen 1:1 sin texto
```

### P?gina 7

```text
P?gina: 7
Plano: medio
Personajes: Vin, Camon, funcionario del Ministerio
Acci?n: negociaci?n tensa en edificio oficial
Ambiente: interior serio, paleta gris y marr?n
Consistencia: igualar rasgos de VIN_BASE y CAMON_BASE
Salida: imagen 1:1 sin texto
```

### P?gina 8

```text
P?gina: 8
Plano: general
Personajes: Vin, Kelsier, Inquisidor
Acci?n: persecuci?n con salto en tejados para distraer inquisidor
Ambiente: noche con bruma y ceniza
Consistencia: igualar KELSIER_BASE, VIN_BASE e INQUISIDOR_BASE
Salida: imagen 1:1 sin texto
```

## QA de consistencia

- Mantener rostro, peinado y silueta de cada ancla.
- Mantener vestuario base salvo cambio expl?cito de escena.
- Mantener paleta y atm?sfera del Imperio Final.
- Bloquear generaci?n ante conflicto can?nico no resuelto.

## Procedimiento operativo r?pido

1. Configurar instrucciones globales del Proyecto.
2. Generar y aprobar las cuatro anclas.
3. Generar p?ginas del piloto una a una.
4. Corregir desv?os referenciando ancla concreta.
5. Registrar observaciones antes de escalar a m?s p?ginas.
