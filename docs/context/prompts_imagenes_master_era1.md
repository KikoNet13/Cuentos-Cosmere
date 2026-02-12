# Prompts de imÃ¡genes master (Era 1, Project-first)

## 1) Uso previsto

Este documento estÃ¡ preparado para:

- Crear un Project de ChatGPT: `Cosmere - Mistborn Era 1 - Imagenes`.
- Generar imÃ¡genes consistentes (estilo + personajes + mundo) con ChatGPT Plus.
- Trabajar por pÃ¡gina con prompts listos para copiar/pegar.
- Ejecutar un piloto: `L01P01`, pÃ¡ginas `1-8`.

## 2) Archivos que debes subir al Project

- `docs/context/flujo_revision.md`
- `docs/context/checklist_revision.md`
- `docs/context/glosario_simplificado_mistborn.md`
- `docs/context/lista_cambios_bloques_1_3.md`
- `biblioteca/nacidos-de-la-bruma-era-1/el-imperio-final/01/textos/origen_md.md`
- `biblioteca/nacidos-de-la-bruma-era-1/el-imperio-final/02/textos/origen_md.md`
- `biblioteca/nacidos-de-la-bruma-era-1/el-imperio-final/03/textos/origen_md.md`
- `biblioteca/nacidos-de-la-bruma-era-1/el-imperio-final/01/textos/referencia_pdf.pdf`
- `biblioteca/nacidos-de-la-bruma-era-1/el-imperio-final/02/textos/referencia_pdf.pdf`
- `biblioteca/nacidos-de-la-bruma-era-1/el-imperio-final/03/textos/referencia_pdf.pdf`
- `docs/assets/style_refs/photo_2026-02-11_15-28-12.jpg`
- `docs/assets/style_refs/photo_2026-02-11_15-28-15.jpg`
- `docs/assets/style_refs/photo_2026-02-11_15-28-17.jpg`

## 3) Instrucciones globales para pegar en el Project

Copia y pega este bloque en las instrucciones del Project:

```text
Eres un director de arte para cuentos infantiles de Mistborn Era 1.

Objetivo:
- Mantener consistencia visual estricta entre imÃ¡genes.
- Mantener identidad de personajes (rostro, peinado, silueta, vestuario base).
- Mantener coherencia de mundo (ceniza, bruma, arquitectura imperial, tono infantil 7-9 aÃ±os).

JerarquÃ­a de verdad:
1) Si una escena fue adaptada y validada en .md, la imagen sigue el .md.
2) Si no hubo adaptaciÃ³n, fidelidad al libro original (PDF/canon).
3) Glosario y checklist corrigen tÃ©rminos y reglas del mundo.
4) Si hay conflicto no resuelto, bloquea la generaciÃ³n.

Reglas visuales:
- Estilo Ãºnico de cuento ilustrado (no fotorealista).
- Formato base cuadrado 1:1.
- Sin texto incrustado, sin logos, sin marcas de agua.
- Sin elementos modernos fuera de mundo.
- Sin cambios arbitrarios de rasgos fÃ­sicos entre escenas.
- Violencia sin detalle grÃ¡fico.

Consistencia obligatoria:
- Generar primero anclas visuales (Vin, Kelsier, Inquisidor, Camon) dentro del Project.
- No generar escenas del piloto hasta tener anclas aceptadas.
- Reusar las anclas como referencia activa en todas las escenas.

Comportamiento de salida:
- Cuando recibas un prompt de escena, genera la imagen directamente.
- No devuelvas reformulaciÃ³n del prompt.
- No aÃ±adas explicaciÃ³n ni texto adicional.
- ExcepciÃ³n: si hay conflicto de canon no resuelto, bloquear y responder en 1-2 lÃ­neas con motivo de bloqueo.
```

## 4) Biblia visual global (fija)

### Estilo artÃ­stico (anclado en `docs/assets/style_refs/`)

- IlustraciÃ³n de cuento infantil, trazo dibujado a mano.
- Contorno oscuro suave, no grueso extremo.
- Color plano con textura ligera de acuarela/papel.
- Expresiones faciales claras y caricaturescas, coherentes de pÃ¡gina a pÃ¡gina.
- ComposiciÃ³n limpia, lectura inmediata.
- IluminaciÃ³n narrativa suave, sin contraste agresivo.

### Mundo y atmÃ³sfera

- Imperio Final opresivo: ceniza flotando, ambiente gris, bruma baja.
- Cielos frÃ­os o rojizos segÃºn escena, sin estÃ©tica moderna.
- Arquitectura imperial sobria (piedra, metal, torres, mansiones antiguas).
- VegetaciÃ³n apagada salvo escenas que explÃ­citamente requieran contraste.

### Paleta base

- Dominantes: grises ceniza, azul grisÃ¡ceo, marrones apagados.
- Acentos: rojo desaturado, cobre tenue, dorado envejecido.
- Color emocional puntual para foco narrativo (sin romper la atmÃ³sfera).

### Prohibiciones globales

- No estilo anime.
- No 3D plÃ¡stico.
- No fotorrealismo.
- No neÃ³n futurista.
- No armas modernas.
- No texto en imagen.

## 5) Fichas ancla (rasgos no negociables)

## 5.1 Vin (piloto P1-P8: introducciÃ³n)

- `id_personaje`: VIN_BASE
- `edad_aparente`: niÃ±a preadolescente (aprox. 11-13).
- `rasgos_fijos`:
- baja estatura, cuerpo delgado.
- cabello corto oscuro, liso, a la altura de las orejas.
- mirada alerta/desconfiada al inicio.
- `vestuario_base`:
- ropa sencilla y gastada en tonos gris/marrÃ³n.
- sin accesorios nobles en este tramo.
- `prohibiciones`:
- no cabello largo.
- no vestuario noble.
- no apariencia adulta.

## 5.2 Kelsier

- `id_personaje`: KELSIER_BASE
- `edad_aparente`: adulto joven-maduro (aprox. 30s).
- `rasgos_fijos`:
- complexiÃ³n atlÃ©tica.
- cicatrices visibles en antebrazos.
- sonrisa confiada/cÃ¡lida incluso en tensiÃ³n.
- `vestuario_base`:
- ropa oscura funcional.
- capa de tiras grises cuando hay acciÃ³n nocturna.
- `prohibiciones`:
- no armadura brillante de fantasÃ­a.
- no rostro severo constante (debe mantener carisma).

## 5.3 Inquisidor de acero

- `id_personaje`: INQUISIDOR_BASE
- `edad_aparente`: adulto, presencia intimidante.
- `rasgos_fijos`:
- clavos metÃ¡licos en lugar de ojos.
- silueta alta, rÃ­gida, amenazante.
- `vestuario_base`:
- tÃºnica oscura sobria de autoridad imperial.
- `prohibiciones`:
- no gore.
- no diseÃ±o monstruoso fuera de canon.
- no rasgos caricaturescos cÃ³micos.

## 5.4 Camon

- `id_personaje`: CAMON_BASE
- `edad_aparente`: adulto.
- `rasgos_fijos`:
- expresiÃ³n avara/controladora.
- porte de lÃ­der de banda menor.
- `vestuario_base`:
- ropa urbana gastada de ladrÃ³n en Luthadel.
- `prohibiciones`:
- no apariencia noble.
- no aspecto heroico.

## 6) Prompts ancla (obligatorio antes del piloto)

Regla obligatoria para el piloto:

- Genera primero estas 4 imÃ¡genes ancla.
- No pases a `P1-P8` hasta validar que las anclas estÃ¡n aceptadas.
- Ãšsalas como referencia de identidad en todas las escenas.

### ANCLA 1 - Vin

```text
IlustraciÃ³n infantil Ã©pica estilo cuento clÃ¡sico, formato cuadrado 1:1, trazo dibujado a mano, contorno oscuro suave, color plano con textura ligera de acuarela y grano de papel. Retrato de cuerpo medio de Vin (niÃ±a de 11-13 aÃ±os), baja, delgada, cabello corto oscuro liso hasta las orejas, ropa sencilla y gastada en tonos grises y marrones, expresiÃ³n alerta y reservada, callejÃ³n de Luthadel al fondo con ceniza en el aire y luz frÃ­a. Coherente con mundo de Mistborn Era 1, sin elementos modernos, sin texto en imagen.
```

### ANCLA 2 - Kelsier

```text
IlustraciÃ³n infantil Ã©pica estilo cuento clÃ¡sico, formato cuadrado 1:1, trazo dibujado a mano, contorno oscuro suave, color plano con textura ligera de acuarela y grano de papel. Retrato de cuerpo medio de Kelsier, adulto atlÃ©tico, antebrazos con cicatrices visibles, sonrisa confiada, ropa oscura funcional y capa de tiras grises, noche con bruma y ceniza de fondo, atmÃ³sfera de Luthadel. No fotorealista, no moderno, sin texto.
```

### ANCLA 3 - Inquisidor de acero

```text
IlustraciÃ³n infantil Ã©pica estilo cuento clÃ¡sico, formato cuadrado 1:1, trazo dibujado a mano, contorno oscuro suave, color plano con textura ligera de acuarela y grano de papel. Figura completa de un Inquisidor de acero: muy alto, tÃºnica oscura imperial, clavos metÃ¡licos en lugar de ojos, postura amenazante, calle oscura de Luthadel con ceniza y bruma. Tono inquietante pero apto para pÃºblico infantil (sin gore), sin elementos modernos, sin texto.
```

### ANCLA 4 - Camon

```text
IlustraciÃ³n infantil Ã©pica estilo cuento clÃ¡sico, formato cuadrado 1:1, trazo dibujado a mano, contorno oscuro suave, color plano con textura ligera de acuarela y grano de papel. Retrato de cuerpo medio de Camon, lÃ­der de banda de ladrones, expresiÃ³n desconfiada y mandona, ropa urbana gastada en tonos apagados, interior pobre de escondite en Luthadel con ceniza en ventanas. Sin elementos modernos, sin texto.
```

## 6.1) Flujo en el chat del Project

1. Pegar mensaje bootstrap (reglas globales + jerarquÃ­a de verdad + polÃ­tica de salida).
2. Generar anclas en este orden: `ANCLA 1 Vin`, `ANCLA 2 Kelsier`, `ANCLA 3 Inquisidor`, `ANCLA 4 Camon`.
3. Solo tras aceptar anclas, pegar cada bloque de escena completo (`prompt_final`) y generar imagen 1 a 1.
4. Si una imagen falla consistencia, reintentar con instrucciÃ³n corta referenciada al ancla:
`corregir para igualar rasgos de [ANCLA_X], mantener rostro, peinado, silueta y vestuario base`.

## 7) Contrato fijo por prompt

```text
id_prompt
bloque
pagina
tipo_imagen (principal|acompaÃ±amiento)
objetivo_narrativo
personajes_visibles
entorno
accion_clave
rasgos_fijos_personaje
estilo_global_fijo
restricciones_canon
negative_constraints
prompt_final
```

### 7.1) Contrato de uso real en el chat del Project

```text
Entrada real: bloque de prompt_final completo (copiar/pegar)
Salida esperada: imagen 1:1 (sin texto)
ExcepciÃ³n: bloqueo textual breve (1-2 lÃ­neas) solo si hay conflicto de canon no resuelto
```

## 8) Plantilla reutilizable (principal)

```text
id_prompt: {ID}
bloque: {BLOQUE}
pagina: {PAGINA}
tipo_imagen: principal
objetivo_narrativo: {OBJETIVO}
personajes_visibles: {PERSONAJES}
entorno: {ENTORNO}
accion_clave: {ACCION}
rasgos_fijos_personaje: {RASGOS}
estilo_global_fijo: IlustraciÃ³n infantil Ã©pica tipo cuento clÃ¡sico, trazo a mano, contorno oscuro suave, color plano con textura ligera, formato 1:1, atmÃ³sfera Mistborn Era 1.
restricciones_canon: {RESTRICCIONES}
negative_constraints: no texto, no logos, no marcas de agua, no elementos modernos, no fotorrealismo, no gore, no cambio de rasgos entre escenas
prompt_final: {PROMPT_FINAL}
```

## 9) Plantilla reutilizable (acompaÃ±amiento)

```text
id_prompt: {ID}
bloque: {BLOQUE}
pagina: {PAGINA}
tipo_imagen: acompaÃ±amiento
objetivo_narrativo: {OBJETIVO_SECUNDARIO}
personajes_visibles: {PERSONAJES}
entorno: {ENTORNO}
accion_clave: {ACCION}
rasgos_fijos_personaje: {RASGOS}
estilo_global_fijo: Igual que la imagen principal de su pÃ¡gina.
restricciones_canon: {RESTRICCIONES}
negative_constraints: no texto, no logos, no marcas de agua, no elementos modernos, no fotorrealismo, no gore, no cambio de rasgos
prompt_final: {PROMPT_FINAL}
```

## 10) Piloto implementado - L01P01 pÃ¡ginas 1-8

Estos bloques se pegan tal cual en el chat del Project para generar imagen.

Nota de uso (obligatoria):

- Primero genera las 4 imÃ¡genes ancla (secciÃ³n 6).
- Luego pega cada bloque de pÃ¡gina completo y genera imagen directa.
- Si ChatGPT permite referencia visual en cada generaciÃ³n, adjunta la ancla correspondiente (Vin/Kelsier/Inquisidor/Camon).

---

### P1 principal

```text
id_prompt: L01P01_P01_MAIN
bloque: L01P01
pagina: 1
tipo_imagen: principal
objetivo_narrativo: Presentar el mundo ceniciento del Imperio Final.
personajes_visibles: ninguno (escena de mundo)
entorno: ciudad tipo Luthadel, cielo rojizo, aire oscuro, ceniza cayendo
accion_clave: atmÃ³sfera opresiva del mundo
rasgos_fijos_personaje: no aplica
estilo_global_fijo: IlustraciÃ³n infantil Ã©pica, cuento clÃ¡sico, trazo a mano, textura suave, formato 1:1
restricciones_canon: mundo triste, plantas marrones, tejados cubiertos de ceniza
negative_constraints: no tecnologÃ­a moderna, no texto
prompt_final: IlustraciÃ³n infantil Ã©pica estilo cuento clÃ¡sico, formato cuadrado 1:1, trazo dibujado a mano con contorno oscuro suave y color plano con textura ligera de acuarela. Escena panorÃ¡mica de una ciudad inspirada en Luthadel: cielo rojo apagado, humo oscuro en el aire, ceniza gris cayendo como nieve negra sobre caminos, tejados y plantas marrones marchitas. SensaciÃ³n de mundo duro pero apto para niÃ±os, sin personajes protagonistas en primer plano, composiciÃ³n clara y narrativa. Sin texto en imagen, sin elementos modernos, no fotorealista.
```

### P2 principal

```text
id_prompt: L01P01_P02_MAIN
bloque: L01P01
pagina: 2
tipo_imagen: principal
objetivo_narrativo: Introducir a Kelsier como hÃ©roe carismÃ¡tico.
personajes_visibles: Kelsier
entorno: calle cenicienta de Luthadel
accion_clave: presencia heroica y alomancia sugerida
rasgos_fijos_personaje: cicatrices en antebrazos, sonrisa confiada, ropa oscura funcional
estilo_global_fijo: IlustraciÃ³n infantil Ã©pica, cuento clÃ¡sico, trazo a mano, textura suave, formato 1:1
restricciones_canon: Kelsier es protector, no brutal
negative_constraints: no gore, no estÃ©tica moderna, no texto
prompt_final: IlustraciÃ³n infantil Ã©pica estilo cuento clÃ¡sico en formato 1:1. Kelsier en plano medio-cuerpo completo, adulto atlÃ©tico con cicatrices visibles en antebrazos y sonrisa confiada, ropa oscura funcional de ladrÃ³n noble y aire de lÃ­der protector. Fondo: calle de Luthadel con ceniza flotando y luz frÃ­a. Sugerir alomancia con detalles sutiles de energÃ­a metÃ¡lica (sin efectos excesivos). Color apagado coherente con mundo de ceniza. Sin texto, no fotorealista, sin elementos modernos.
```

### P2 acompaÃ±amiento (personaje ancla)

```text
id_prompt: L01P01_P02_SUP_CHAR
bloque: L01P01
pagina: 2
tipo_imagen: acompaÃ±amiento
objetivo_narrativo: Reforzar identidad visual estable de Kelsier para escenas futuras.
personajes_visibles: Kelsier
entorno: fondo neutro de ciudad cenicienta
accion_clave: pose tranquila, carisma protector
rasgos_fijos_personaje: cicatrices, sonrisa cÃ¡lida, capa de tiras grises sugerida
estilo_global_fijo: Igual que principal
restricciones_canon: Kelsier reconocible
negative_constraints: no cambios de rostro, no texto
prompt_final: Retrato cuadrado 1:1 de Kelsier en estilo cuento infantil Ã©pico, trazo a mano y textura suave. Mantener rasgos fijos: adulto atlÃ©tico, antebrazos con cicatrices, sonrisa segura, ropa oscura y capa de tiras grises. Fondo sencillo de Luthadel con ceniza, iluminaciÃ³n suave. Debe funcionar como referencia visual estable del personaje para las siguientes pÃ¡ginas. Sin texto ni elementos modernos.
```

### P3 principal

```text
id_prompt: L01P01_P03_MAIN
bloque: L01P01
pagina: 3
tipo_imagen: principal
objetivo_narrativo: Mostrar el golpe nocturno de Kelsier y la huida de familias.
personajes_visibles: Kelsier, guardias, familias trabajadoras
entorno: granja/mansiÃ³n de noche
accion_clave: distracciÃ³n para permitir escape
rasgos_fijos_personaje: Kelsier Ã¡gil, protector
estilo_global_fijo: IlustraciÃ³n infantil Ã©pica, cuento clÃ¡sico, trazo a mano, textura suave, formato 1:1
restricciones_canon: acciÃ³n intensa sin detalle grÃ¡fico
negative_constraints: no gore, no armas modernas, no texto
prompt_final: IlustraciÃ³n infantil Ã©pica de noche en formato cuadrado 1:1. Kelsier irrumpe en una mansiÃ³n de plantaciÃ³n y crea una distracciÃ³n mientras familias trabajadoras escapan hacia la oscuridad segura. Mostrar movimiento y tensiÃ³n narrativa sin violencia grÃ¡fica: guardias sorprendidos, Kelsier Ã¡gil y decidido, ceniza en el aire y luz nocturna frÃ­a. ComposiciÃ³n clara y apta para niÃ±os, estilo de cuento ilustrado coherente. Sin texto.
```

### P4 principal

```text
id_prompt: L01P01_P04_MAIN
bloque: L01P01
pagina: 4
tipo_imagen: principal
objetivo_narrativo: Kelsier promete esperanza y parte hacia Luthadel.
personajes_visibles: Kelsier y grupo de trabajadores
entorno: camino con niebla/bruma
accion_clave: despedida esperanzadora
rasgos_fijos_personaje: Kelsier con mochila, postura lÃ­der cercano
estilo_global_fijo: IlustraciÃ³n infantil Ã©pica, cuento clÃ¡sico, trazo a mano, textura suave, formato 1:1
restricciones_canon: tono de esperanza dentro de ambiente duro
negative_constraints: no texto en imagen, no moderno
prompt_final: IlustraciÃ³n infantil Ã©pica 1:1: Kelsier se despide de un grupo de trabajadores y les promete tiempos mejores. Ã‰l aparece con mochila al hombro, de espaldas en parte del plano, entrando en un camino con bruma baja hacia Luthadel. Los trabajadores muestran mezcla de cansancio y esperanza. Paleta gris ceniza con un leve acento cÃ¡lido en la escena para transmitir Ã¡nimo. Sin texto, no fotorrealista.
```

### P5 principal

```text
id_prompt: L01P01_P05_MAIN
bloque: L01P01
pagina: 5
tipo_imagen: principal
objetivo_narrativo: Presentar a Vin en su contexto de supervivencia.
personajes_visibles: Vin
entorno: callejÃ³n oscuro de Luthadel
accion_clave: Vin escondida, alerta
rasgos_fijos_personaje: niÃ±a pequeÃ±a, cabello corto oscuro, ropa gastada
estilo_global_fijo: IlustraciÃ³n infantil Ã©pica, cuento clÃ¡sico, trazo a mano, textura suave, formato 1:1
restricciones_canon: Vin desconfiada y discreta
negative_constraints: no rasgos adultos, no texto
prompt_final: IlustraciÃ³n infantil Ã©pica en formato cuadrado 1:1. PresentaciÃ³n de Vin: niÃ±a pequeÃ±a y delgada, cabello corto oscuro a la altura de las orejas, ropa sencilla y gastada en tonos grises y marrones. EstÃ¡ semiescondida en un callejÃ³n oscuro de Luthadel, observando con mirada alerta y desconfiada. Ceniza en el ambiente, arquitectura de piedra envejecida, luz tenue. Debe verse vulnerable pero inteligente. Sin texto, sin elementos modernos.
```

### P5 acompaÃ±amiento (personaje ancla)

```text
id_prompt: L01P01_P05_SUP_CHAR
bloque: L01P01
pagina: 5
tipo_imagen: acompaÃ±amiento
objetivo_narrativo: Fijar la identidad visual de Vin para continuidad.
personajes_visibles: Vin
entorno: fondo simple urbano gris
accion_clave: retrato de referencia
rasgos_fijos_personaje: cabello corto oscuro, complexiÃ³n pequeÃ±a, expresiÃ³n vigilante
estilo_global_fijo: Igual que principal
restricciones_canon: apariencia infantil estable
negative_constraints: no cambio de edad, no texto
prompt_final: Retrato cuadrado 1:1 de Vin en estilo cuento infantil Ã©pico, trazo a mano y color con textura suave. Rasgos fijos: niÃ±a de 11-13 aÃ±os, baja y delgada, cabello oscuro corto y liso hasta las orejas, ojos atentos, ropa gastada de tonos apagados. Fondo urbano neutral de Luthadel con ceniza ligera. Esta imagen debe servir como referencia consistente para todas sus apariciones posteriores. Sin texto.
```

### P6 principal

```text
id_prompt: L01P01_P06_MAIN
bloque: L01P01
pagina: 6
tipo_imagen: principal
objetivo_narrativo: Mostrar la â€œSuerteâ€ de Vin como truco de supervivencia.
personajes_visibles: Vin y una persona enfadada
entorno: interior humilde en Luthadel
accion_clave: Vin calma a alguien con un gesto sutil
rasgos_fijos_personaje: Vin mantiene diseÃ±o ancla
estilo_global_fijo: IlustraciÃ³n infantil Ã©pica, cuento clÃ¡sico, trazo a mano, textura suave, formato 1:1
restricciones_canon: magia emocional sutil, no espectÃ¡culo exagerado
negative_constraints: no rayos neÃ³n, no texto
prompt_final: IlustraciÃ³n infantil Ã©pica 1:1 en interior humilde de Luthadel. Vin, pequeÃ±a y discreta, concentra su â€œSuerteâ€ para calmar a una persona claramente enfadada. La magia debe verse sutil: transiciÃ³n emocional en rostros y ambiente, sin efectos brillantes excesivos. Ceniza y tonos apagados del mundo presentes en paleta. Escena clara para niÃ±os, sin violencia grÃ¡fica, sin texto.
```

### P7 principal

```text
id_prompt: L01P01_P07_MAIN
bloque: L01P01
pagina: 7
tipo_imagen: principal
objetivo_narrativo: Trato con Camon y apariciÃ³n del peligro (guardia con ojos de metal).
personajes_visibles: Vin, Camon, funcionario del Ministerio, guardia de ojos de metal
entorno: edificio serio del Ministerio
accion_clave: Vin usa su â€œSuerteâ€, queda agotada; el guardia la detecta
rasgos_fijos_personaje: Vin ancla, Camon ancla, guardia inquietante
estilo_global_fijo: IlustraciÃ³n infantil Ã©pica, cuento clÃ¡sico, trazo a mano, textura suave, formato 1:1
restricciones_canon: tensiÃ³n sin gore
negative_constraints: no hiperdetalle terror, no texto
prompt_final: IlustraciÃ³n infantil Ã©pica 1:1 en sala formal del Ministerio. Camon negocia con un funcionario mientras Vin usa su â€œSuerteâ€ con esfuerzo y se ve cansada. Al fondo, un guardia muy inquietante con ojos de metal la observa y empieza a seguirle el rastro. ComposiciÃ³n que priorice tensiÃ³n narrativa, apta para niÃ±os, sin violencia grÃ¡fica. Paleta gris ceniza con contraste moderado. Sin texto.
```

### P7 acompaÃ±amiento (objeto/amenaza)

```text
id_prompt: L01P01_P07_SUP_OBJ
bloque: L01P01
pagina: 7
tipo_imagen: acompaÃ±amiento
objetivo_narrativo: Reforzar visualmente el rasgo del guardia con ojos de metal.
personajes_visibles: guardia/Inquisidor (detalle)
entorno: pasillo oscuro del Ministerio
accion_clave: mirada amenazante hacia Vin (fuera de campo)
rasgos_fijos_personaje: clavos metÃ¡licos en los ojos, silueta rÃ­gida
estilo_global_fijo: Igual que principal
restricciones_canon: inquietante, sin gore
negative_constraints: no sangre, no texto
prompt_final: IlustraciÃ³n cuadrada 1:1 de acompaÃ±amiento: primer plano del rostro parcial del guardia de ojos de metal en un pasillo oscuro del Ministerio, con expresiÃ³n frÃ­a y amenazante mirando hacia fuera de cuadro. Mantener tono infantil sin gore, estilo cuento ilustrado con contorno suave y textura ligera. Debe reforzar el peligro inminente para Vin. Sin texto.
```

### P8 principal

```text
id_prompt: L01P01_P08_MAIN
bloque: L01P01
pagina: 8
tipo_imagen: principal
objetivo_narrativo: Presentar al Inquisidor como amenaza y a Kelsier como distracciÃ³n salvadora.
personajes_visibles: Vin, Inquisidor, Kelsier
entorno: tejados nocturnos de Luthadel
accion_clave: Kelsier salta por tejados para distraer al Inquisidor y proteger a Vin
rasgos_fijos_personaje: Inquisidor alto con clavos, Kelsier Ã¡gil con capa de tiras, Vin pequeÃ±a en peligro
estilo_global_fijo: IlustraciÃ³n infantil Ã©pica, cuento clÃ¡sico, trazo a mano, textura suave, formato 1:1
restricciones_canon: acciÃ³n dinÃ¡mica sin violencia grÃ¡fica
negative_constraints: no gore, no texto, no moderno
prompt_final: IlustraciÃ³n infantil Ã©pica en formato 1:1, escena nocturna en tejados de Luthadel. El Inquisidor de acero (alto, clavos en los ojos, tÃºnica oscura) persigue a Vin, que corre asustada pero decidida. Kelsier irrumpe desde otro tejado con salto espectacular y capa de tiras grises para distraer al Inquisidor y protegerla. Mostrar dinamismo, bruma y ceniza en el aire, luces urbanas frÃ­as, composiciÃ³n clara y apta para pÃºblico infantil. Sin texto en imagen.
```

## 11) QA de consistencia (piloto P1-P8)

Usar esta lista despuÃ©s de generar cada imagen:

| PÃ¡gina | Rostro/silueta consistente | Vestuario consistente | Mundo ceniza/bruma coherente | Magia coherente con reglas | Sin elementos fuera de mundo | Estado (ok/ajustar/bloquear) | Nota |
| ------ | -------------------------- | --------------------- | ---------------------------- | -------------------------- | ---------------------------- | ---------------------------- | ---- |
| P1     | N/A                        | N/A                   |                              | N/A                        |                              |                              |      |
| P2     |                            |                       |                              |                            |                              |                              |      |
| P3     |                            |                       |                              |                            |                              |                              |      |
| P4     |                            |                       |                              |                            |                              |                              |      |
| P5     |                            |                       |                              |                            |                              |                              |      |
| P6     |                            |                       |                              |                            |                              |                              |      |
| P7     |                            |                       |                              |                            |                              |                              |      |
| P8     |                            |                       |                              |                            |                              |                              |      |

## 12) Procedimiento operativo rÃ¡pido

1. Genera y guarda anclas (`ANCLA 1-4`).
2. Genera `P1` principal.
3. Genera `P2` principal y su acompaÃ±amiento.
4. ContinÃºa hasta `P8` (aÃ±adiendo acompaÃ±amiento solo donde estÃ¡ definido).
5. Rellena QA por pÃ¡gina.
6. Si una imagen falla QA:

- MantÃ©n el mismo `id_prompt`.
- Repite generaciÃ³n aÃ±adiendo al final:
- `corregir para igualar rasgos de [ANCLA_X], mantener vestuario y rostro idÃ©nticos`.

## 13) Escalado despuÃ©s del piloto

- Reutilizar esta misma biblia y contrato para `L01P01` pÃ¡ginas `9-32`.
- DespuÃ©s aplicar igual en `L01P02` y `L01P03`.
- Solo aÃ±adir fichas ancla nuevas cuando aparezca personaje nuevo.
- Nunca redefinir Vin/Kelsier/Inquisidor/Camon una vez fijados.

## 14) Bloques finales listos para copiar/pegar

### Bloque A - Instrucciones del Project (versiÃ³n final)

```text
Eres un director de arte para cuentos infantiles de Mistborn Era 1.

Objetivo:
- Mantener consistencia visual estricta entre imÃ¡genes.
- Mantener identidad de personajes (rostro, peinado, silueta, vestuario base).
- Mantener coherencia de mundo (ceniza, bruma, arquitectura imperial, tono infantil 7-9 aÃ±os).

JerarquÃ­a de verdad:
1) Si una escena fue adaptada y validada en .md, la imagen sigue el .md.
2) Si no hubo adaptaciÃ³n, fidelidad al libro original (PDF/canon).
3) Glosario y checklist corrigen tÃ©rminos y reglas del mundo.
4) Si hay conflicto no resuelto, bloquear generaciÃ³n.

Reglas visuales:
- Estilo Ãºnico de cuento ilustrado (no fotorealista).
- Formato base cuadrado 1:1.
- Sin texto incrustado, sin logos, sin marcas de agua.
- Sin elementos modernos fuera de mundo.
- Sin cambios arbitrarios de rasgos fÃ­sicos entre escenas.
- Violencia sin detalle grÃ¡fico.

Consistencia obligatoria:
- Generar primero anclas visuales (Vin, Kelsier, Inquisidor, Camon) dentro del Project.
- No generar escenas del piloto hasta tener anclas aceptadas.
- Reusar las anclas como referencia activa en todas las escenas.

Comportamiento de salida:
- Cuando recibas un prompt de escena, genera la imagen directamente.
- No reformules el prompt.
- No aÃ±adas explicaciones ni texto adicional.
- ExcepciÃ³n: si hay conflicto de canon no resuelto, responde en 1-2 lÃ­neas explicando el bloqueo.
```

### Bloque B - Mensaje inicial del chat del Project (arranque operativo)

```text
Arrancamos sesiÃ³n de generaciÃ³n de imÃ¡genes para Mistborn Era 1.

Aplica jerarquÃ­a de verdad y reglas globales del Project.
Primero genera anclas obligatorias en este orden:
1) ANCLA 1 - Vin
2) ANCLA 2 - Kelsier
3) ANCLA 3 - Inquisidor de acero
4) ANCLA 4 - Camon

No pases al piloto L01P01 P1-P8 hasta confirmar que las 4 anclas estÃ¡n aceptadas.
DespuÃ©s, generarÃ© escenas pegando cada prompt completo 1 a 1.
Tu salida debe ser solo imagen (sin texto), salvo bloqueo de canon en 1-2 lÃ­neas.
```

