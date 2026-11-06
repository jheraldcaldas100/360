# Tres60 SafeCampus: contenido completo del PPT

> Todo el contenido del pitch deck, diapositiva por diapositiva: el texto que va en la pantalla, lo que se dice (con su tiempo) y la fuente de cada dato.
>
> - **Reglas del Demo Day:** máximo 8 diapositivas, 3 min de pitch continuo, 2 min de preguntas y 3 integrantes presentes.
> - **Valores entre corchetes, como [X]:** son mediciones propias que hay que completar. No se inventan; si un dato no existe, se quita la tarjeta.
> - **Detalle de las fuentes:** `docs/investigacion-relevancia-peru.md`. Las cifras marcadas **(verificar)** se confirman en el documento original antes de presentar.
> - **Diseño usado:** fondo azul noche `#14213D`, fondo claro `#F7F6F2`, acento naranja `#F5A65B` (oscuro `#C2610C`) y azul `#1F5BC4`. Títulos en Space Grotesk y texto en Inter.

---

## Resumen del orden y los tiempos

| # | Diapositiva | Criterio de la rúbrica | Tiempo | Palabras |
|---|---|---|---|---|
| 1 | Portada y gancho | Validación (15 %) | 0:00 – 0:10 | ~30 |
| 2 | El problema y su evidencia | Validación (15 %) | 0:10 – 0:30 | ~50 |
| 3 | La solución y el recorrido del guardia | UX (15 %) e Innovación | 0:30 – 0:45 | ~35 |
| 4 | Demo en vivo | **Técnico (35 %)** y UX | 0:45 – 1:45 | ~110 |
| 5 | Cómo funciona por dentro | **Técnico (35 %)** | 1:45 – 2:00 | ~35 |
| 6 | Resultados medidos | **Técnico (35 %)** | 2:00 – 2:15 | ~35 |
| 7 | Negocio | Negocio (20 %) | 2:15 – 2:45 | ~70 |
| 8 | Diferenciación y cierre | Innovación (15 %) | 2:45 – 3:00 | ~35 |

**Roles:** el integrante 1 habla; el integrante 2 opera la laptop y muestra el celular del guardia; el integrante 3 actúa frente a la cámara (entra en grupo, deja la mochila).

---

## Diapositiva 1. Portada

**En pantalla**

- Etiqueta superior: FRENTE S2 · SEGURIDAD Y GOVTECH
- Título: **Tres60 SafeCampus**
- Subtítulo: *Ojos extra para el personal de seguridad: las cámaras que ya existen avisan a tiempo, y una persona decide.*
- Dato destacado: **8 de cada 10 peruanos temen ser víctimas de un delito** (INEI, julio a diciembre de 2025)
- Pie: [Integrante 1] · [Integrante 2] · [Integrante 3] — [Universidad] — CODE UP 2026

**Qué decir (0:00 – 0:10)**

> «En el Perú, 8 de cada 10 personas temen ser víctimas de un delito, y los jóvenes de 15 a 29 años, la edad universitaria, son el grupo más victimizado.»

**Fuente:** INEI. 83.7 % de percepción de inseguridad en julio a diciembre de 2025; 33.7 % de víctimas en el grupo de 15 a 29 años. **(verificar el semestre)**

---

## Diapositiva 2. El problema

**En pantalla**

- Etiqueta: VALIDACIÓN DEL PROBLEMA
- Título: **Las cámaras ya están; falta que alguien mire la correcta a tiempo**
- Cuatro tarjetas:

| Tarjeta | Texto |
|---|---|
| **Quién lo sufre** | El operador que vigila muchas cámaras y el guardia en ronda. Detrás: estudiantes de 15 a 29 años, el grupo más victimizado (33.7 %, INEI). |
| **Pasa en campus peruanos** | Laptops robadas en aulas y laboratorios sin personal (UTEC, La Cantuta, Científica del Sur). Estudiantes desvanecidos o tendidos (USMP, PUCP). |
| **Cómo se resuelve hoy** | Una persona mira pantallas y otras hacen rondas. Con 4 pantallas detecta ~83 % de incidentes; con 16, ~64 % (Tickner y Poulton). |
| **Nuestra evidencia** *(tarjeta oscura)* | [X] cámaras y [Y] operadores en nuestro campus. «[Cita del jefe de seguridad]». Experimento: [N] de 10 no vieron la mochila; el resto tardó [Z] s. |

- Pie de fuentes: INEI; Panamericana, América TV, Trome, La República (2023–2025); Tickner y Poulton, Ergonomics (1973).

**Qué decir (0:10 – 0:30)**

> «Las cámaras ya están, pero alguien tiene que mirar la correcta en el momento justo. En nuestra universidad hay [X] cámaras y [Y] personas mirándolas. Simulamos una sala de monitoreo: [N] de 10 compañeros no notaron la mochila abandonada, y quienes la vieron tardaron [Z] segundos.»

⚠️ **No decir** que el sistema evita asaltos en la calle: las cámaras del campus no cubren la vía pública.

**Casos en detalle (por si los piden)**

| Caso | Qué pasó | Regla que aplica |
|---|---|---|
| UTEC, Barranco (abril de 2024) | Robaron laptops en una zona sin personal usada como biblioteca | Zona restringida fuera de horario |
| La Cantuta (mayo de 2024) | Desaparecieron 31 laptops de un laboratorio | Zona restringida fuera de horario |
| Científica del Sur, Villa El Salvador (noviembre de 2023) | Dos personas que se hicieron pasar por estudiantes se llevaron 4 laptops; «la universidad no reaccionó a tiempo» | Objeto desatendido y registro con evidencia |
| USMP | Una estudiante se desvaneció en la biblioteca; la familia denunció falta de primeros auxilios | Persona en el suelo |
| PUCP (marzo de 2025) | Un vigilante encontró a un estudiante tendido en el estacionamiento | Persona en el suelo |
| UNMSM, admisión 2025 | 28,665 y 29,302 postulantes por proceso | Aglomeración |

---

## Diapositiva 3. La solución

**En pantalla**

- Etiqueta: LA SOLUCIÓN · RECORRIDO DEL GUARDIA
- Título: **La IA detecta, las reglas verifican, una persona decide**
- Cinco pasos:

| Paso | Texto |
|---|---|
| 1. Detecta | Cámara existente + YOLO: personas y mochilas |
| 2. Verifica | Criterios objetivos: cuántos, cuánto tiempo, qué posición |
| 3. Avisa | Dashboard con color y sonido + Telegram con foto |
| 4. Decide *(destacado)* | El guardia confirma o descarta y marca «atendida» |
| 5. Mide | Tiempos de detección, respuesta y atención |

- Las cuatro situaciones: 👥 Aglomeración · 🎒 Objeto desatendido · 🚑 Persona en el suelo · ⛔ Zona restringida
- Pie: *Apoya al personal, no lo reemplaza · Sin reconocimiento facial: detecta situaciones, no personas*

**Qué decir (0:30 – 0:45)**

> «Tres60 SafeCampus analiza las cámaras que ya existen, verifica criterios objetivos (cuántas personas, cuánto tiempo, en qué posición) y avisa al guardia en tiempo real. No reemplaza al personal: cada alerta la confirma una persona.»

---

## Diapositiva 4. Demo en vivo

**En pantalla**

- Etiqueta: DEMO EN VIVO · DE PRINCIPIO A FIN
- Título: **Este celular es una cámara del campus**

| # | En escena | Qué ve el usuario |
|---|---|---|
| 1 | Entran 3 personas y se quedan 5 s | Alerta naranja con sonido; la cámara se enciende en el mapa |
| 2 | El guardia mira su celular | Telegram con foto y botones |
| 3 | Alguien deja la mochila y se va | Contador 00:05/00:20 y alerta de objeto |
| 4 | La IA describe la foto | «Mochila sola en el piso… Coincide: sí» |
| 5 | Confirmar → Marcar atendida | Se registran los tiempos y quién atendió |
| 6 | Una falsa alarma | Se descarta en un toque y queda registrada |
| 7 | Mover un deslizador | El criterio cambia en vivo, en 1 s |

- Pie: *Plan B: video grabado con `python iniciar_demo.py --fuente videos/respaldo.mp4`*

**Qué decir (0:45 – 1:45)**, mientras se cambia a la pantalla del dashboard (pestaña Monitoreo):

1. «Supera el umbral durante 5 segundos y alerta: aglomeración.»
2. «Le llega al guardia en ronda, con evidencia.»
3. «El conteo empieza cuando no hay nadie cerca. En la demo son 20 segundos; en la realidad, 10 minutos.»
4. «La IA describe la foto en una frase; no decide.»
5. «Lo que hace el guardia en el celular se ve en la central, y al revés. Todo queda medido.»
6. «Si es una falsa alarma, se descarta en un toque.»
7. «Cada universidad ajusta sus criterios, en vivo.»

**Reglas de la demo**

- Los pasos 1, 2, 5 y 6 **nunca** se saltan: son el flujo completo.
- Si falta tiempo, se salta el paso 7.
- **Persona en el suelo** solo entra si salió bien en el ensayo final con colchoneta. En el ensayo del 5 de noviembre dio 3 falsas alarmas.
- Antes de entrar: `python verificar.py` y `python iniciar_demo.py --limpiar`.

---

## Diapositiva 5. Cómo funciona por dentro

**En pantalla**

- Etiqueta: DESARROLLO TÉCNICO · IA REAL
- Título: **Cómo funciona por dentro**
- Flujo: `Cámara → YOLO11n → Reglas (Python) → SQLite → Dashboard ⇄ Telegram`

| IA | Recibe | Produce | Cómo se usa |
|---|---|---|---|
| YOLO11n (local, sin internet) | Cada cuadro de video | Recuadros de personas y mochilas, con su confianza | Las reglas miden cantidad, tiempo y posición |
| Visión de OpenAI (opcional) | La foto de la alerta con los rostros difuminados | Una frase y «Coincide: sí, no o incierto» | Contexto en el dashboard y en Telegram; **nunca decide** |

| ✅ Implementado | Pendiente |
|---|---|
| 4 reglas configurables en vivo · registro con tiempos · dashboard, mapa y estadísticas · Telegram en los dos sentidos · evaluación y 34 pruebas automáticas | Varias cámaras RTSP · horarios por zona · aviso de cámara caída · modelo de pose · piloto en modo sombra |

**Qué decir (1:45 – 2:00)**

> «Usamos dos IA. YOLO detecta personas y objetos en cada cuadro, sin internet. Las reglas convierten esas detecciones en alertas, que se guardan con sus tiempos en SQLite. Un modelo de OpenAI describe la foto, pero no decide.»

---

## Diapositiva 6. Resultados medidos

**En pantalla**

- Etiqueta: RESULTADOS MEDIDOS POR NOSOTROS
- Título: **No nos quedamos en la demo: lo medimos**
- Tres cifras grandes:
  - **[X]/[Y]**: situaciones detectadas en video etiquetado
  - **[Z]**: falsas alarmas en [min] de video
  - **[T] s**: desde que empieza la situación hasta la alerta
- Banda oscura: **[N]/10** personas notaron la mochila en el mosaico de 4 cámaras, en [Z] s en promedio. SafeCampus alertó en [T] s.
- Pie: *Fuente: `evaluar.py` (`data/evaluacion/resumen.md`) y `experimento.py` · [fps] fps en una laptop [con o sin GPU]*

**Qué decir (2:00 – 2:15)**

> «Lo medimos: detectó [X] de [Y] situaciones, con [Z] falsas alarmas, y alertó en [T] segundos. Lo que ven funciona hoy; varias cámaras, horarios por zona y el piloto son el siguiente paso.»

**Cómo obtener los números:** `python evaluar.py clips/etiquetas.csv` y `python experimento.py resumen --sistema [T]`.

---

## Diapositiva 7. Negocio

**En pantalla**

- Etiqueta: VIABILIDAD DE NEGOCIO
- Título: **La universidad paga menos que un operador más**

| Tarjeta | Texto |
|---|---|
| **Quién usa y quién paga** | Usan operadores y guardias. Paga la universidad: suscripción de [S/ Y] por cámara al mes. |
| **Por qué adopta** | La SUNEDU exige vigilancia 24 h. Las cámaras ya están compradas. Un puesto de monitoreo 24/7 cuesta ~S/ 12,300–15,400 al mes. |
| **Costos principales** | Una PC por cada [N] cámaras, instalación y soporte. Software base libre. Telegram gratis. |

- Banda destacada: **< S/ 0.012 por alerta**: el único pago por uso (API de OpenAI, modelo económico). Unos S/ 7 al mes en un piloto de 4 cámaras. Se paga sola si ahorra 3 s por alerta.
- Adopción: piloto gratis de 1 mes aquí → caso de éxito con métricas → otras universidades → GovTech (centrales municipales)
- Pie: *Supuestos: operador de S/ 2,000 a 2,500 + 47 % de cargas; precios oficiales de OpenAI (noviembre de 2026); S/ 3.46 por dólar.*

**Qué decir (2:15 – 2:45)**

> «Nuestro cliente es la universidad, que ya debe tener vigilancia las 24 horas y ya compró las cámaras. Un puesto de monitoreo 24/7 cuesta más de doce mil soles al mes; SafeCampus cuesta [Y] soles por cámara al mes. El único pago por uso, la IA de OpenAI, cuesta menos de un céntimo por alerta. Empezamos con un piloto gratuito aquí y seguimos con otras universidades y centrales municipales.»

**Cálculo del precio:** de 3 a 5 veces el costo por cámara, que es PC ÷ 36 meses ÷ N cámaras, más el soporte.

**Respaldo de costos (por si lo piden)**

| Modelo de OpenAI | Costo por alerta (peor caso) | Piloto de 600 alertas al mes | Campus grande de 45,000 alertas al mes |
|---|---|---|---|
| GPT-6 Luna | S/ 0.0011 | S/ 0.69 | S/ 51 |
| GPT-6.1 Terra | S/ 0.0114 | S/ 6.85 | S/ 514 |

- **Punto de equilibrio:** se paga sola si ahorra 0.3 s (Luna) o 3 s (Terra) por alerta.
- **Remuneración mínima vital:** S/ 1,230 desde octubre de 2026.
- **Operador CCTV en Lima:** S/ 1,900 a 2,500 al mes.

---

## Diapositiva 8. Diferenciación y cierre

**En pantalla**

- Etiqueta: POR QUÉ NOSOTROS

| Alternativa | Su límite | SafeCampus |
|---|---|---|
| Operador solo | Su atención cae con más pantallas | Avisa en cualquier cámara |
| Cámaras con analítica | Hay que cambiar el equipo | Usa las cámaras existentes |
| Plataformas comerciales | Precio por canal, vía integradores | Bajo costo y en español |
| Reconocimiento facial | Identifica personas: riesgo legal | Detecta situaciones, no personas |

- Frase final: **Las cámaras ya están. SafeCampus le da ojos extra al personal de seguridad.**
- Pedido: *Queremos hacer el piloto en [universidad]. ¡Gracias!*

**Qué decir (2:45 – 3:00)**

> «Las cámaras ya están; lo que falta es que alguien las mire a tiempo. SafeCampus le da ojos extra al personal, sin identificar a nadie. Queremos hacer el piloto en [universidad]. Gracias.»

---

## Preguntas del jurado (2 min, respuestas de 20 s)

| Pregunta | Respuesta |
|---|---|
| ¿Cómo saben que el problema existe? | «Datos del INEI, casos documentados en campus peruanos y nuestra propia evidencia: la entrevista, la encuesta y el experimento, donde [N] de 10 no notaron la mochila.» |
| ¿Esto evita robos? | «No directamente: detecta situaciones observables, como alguien en un laboratorio fuera de horario o una mochila sola. Los asaltos en la calle quedan fuera de las cámaras del campus.» |
| ¿Qué pasa con las falsas alarmas? | «El guardia la descarta en un toque y queda registrada para recalibrar. Por eso decide una persona.» |
| ¿Y si se cae la cámara? | «Hoy no avisa; es el primer pendiente: marcar la cámara como "desconocida" y alertar.» |
| ¿Qué tan preciso es? | «En nuestras pruebas, [X] de [Y], con [Z] falsas alarmas. Es un MVP; el siguiente paso es un piloto en modo sombra.» |
| ¿Funciona sin internet? | «Sí: la detección, las reglas y el dashboard son locales. Solo Telegram y la IA de OpenAI necesitan internet, y si fallan la alerta llega igual.» |
| ¿Por qué la IA no decide? | «Los modelos de visión todavía fallan como detectores: el mejor obtuvo un F1 de 57 % al describir anomalías (CAVE, 2025). Por eso solo describe.» |
| ¿Y la privacidad? | «Sin reconocimiento facial; difuminamos los rostros antes de enviar la foto a la IA; cumplimos la Ley 29733 y su reglamento de 2024. Pendiente: difuminar también la foto de Telegram.» |
| ¿Cuánto cuesta la IA? | «Menos de un céntimo de sol por alerta: unos S/ 7 al mes en un piloto.» |
| ¿Por qué pagaría la universidad? | «Ya debe tener vigilancia 24 horas, ya compró las cámaras, y un puesto 24/7 cuesta más de S/ 12,000 al mes.» |
| ¿Y la licencia de YOLO? | «Es AGPL: libre para uso interno; si se vende como servicio cerrado, se compra la licencia empresarial o se cambia a un detector Apache.» |
| San Marcos ya instala cámaras con reconocimiento facial. ¿Qué aportan? | «Somos complementarios: no identificamos a nadie, alertamos situaciones y medimos los tiempos de atención.» |
| ¿Qué harían con más tiempo? | «Un piloto de un mes en modo sombra, varias cámaras, horarios por zona, aviso de cámara caída y pose para caídas.» |

---

## Antes de presentar

- [ ] Completar todos los [corchetes] con datos reales, o quitar esa tarjeta
- [ ] Confirmar las cifras del INEI en el PDF original
- [ ] **Entregable «MVP desplegado (Sr)»:** tener un enlace funcional activo, o confirmar con los organizadores que vale la demo en vivo más el repositorio
- [ ] Demo completa 3 veces seguidas sin fallas en el lugar real; celular en trípode
- [ ] Telegram probado con `python notificador.py`
- [ ] Plan B: video de respaldo listo
- [ ] Pitch cronometrado en menos de 3:00, ensayado 5 veces
