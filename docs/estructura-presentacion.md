# Tres60 SafeCampus: estructura de la presentación (categoría Senior)

> Estructura del pitch de 3 minutos, la demo y las preguntas del jurado, ordenada según los cinco criterios de la rúbrica.
>
> - **Valores entre corchetes, como [X]:** se completan con **mediciones propias** (entrevista, encuesta, `experimento.py`, `evaluar.py`). No se inventan.
> - **Cifras públicas:** salen de [`investigacion-relevancia-peru.md`](investigacion-relevancia-peru.md), donde está cada fuente. Las marcadas **(verificar)** se confirman en el documento original antes de presentarlas.
> - **Complementa** a [`pitch-y-negocio.md`](pitch-y-negocio.md) (Lean Canvas y respuestas) y a [`plan-mejora-rubrica.md`](plan-mejora-rubrica.md) (tareas).

---

## 1. Cómo se reparte el puntaje en la presentación

| Criterio | Peso | Qué evalúan | Dónde se gana | Prueba que hay que mostrar |
|---|---|---|---|---|
| **Desarrollo técnico y MVP** | **35 %** (y desempate) | Lógica de backend, datos o IA real | Demo de principio a fin (0:45 a 1:45), diapositiva «Cómo funciona» y resultados medidos | La demo funcionando en vivo; qué recibe y qué produce cada IA; tabla de `evaluar.py`; qué está implementado y qué falta |
| **Viabilidad de negocio** | 20 % | Estrategia de adopción y sostenibilidad | Diapositiva de negocio (2:15 a 2:45) | Quién usa, quién paga, costos sustentados, precio con su cálculo y plan de adopción |
| **Validación de problemática** | 15 % | Claridad del dolor y evidencia real | Primeros 30 s y diapositiva del problema | Datos públicos con fuente **más** evidencia propia: cita del jefe de seguridad, encuesta y experimento |
| **Diseño UX/UI y flujo** | 15 % | Intuitividad del recorrido del usuario | La demo mostrada **desde el punto de vista del guardia** | El recorrido completo: llega la alerta → evidencia → confirmar → atender → estadísticas; y qué pasa ante errores |
| **Innovación, pitch y sustentación** | 15 % | Originalidad, síntesis en 3 min y solidez en las preguntas | Cierre, diferenciación y preguntas | Comparación con las alternativas; respuestas de 20 s; limitaciones dichas con honestidad |

**Regla de oro:** como el desempate es el MVP técnico, la demo de principio a fin **no se recorta nunca**. Si falta tiempo, se acorta el negocio, nunca la demo.

---

## 2. Línea de tiempo del pitch (3:00, unas 400 palabras)

| Tiempo | Bloque | Criterio principal | Diapositiva | Palabras |
|---|---|---|---|---|
| 0:00 – 0:30 | El problema y su evidencia | Validación (15 %) | D1 y D2 | ~70 |
| 0:30 – 0:45 | La solución en una frase | Innovación y UX | D3 | ~35 |
| 0:45 – 1:45 | **Demo en vivo, de principio a fin** | **Técnico (35 %)** y UX (15 %) | Pantalla del dashboard y celular con Telegram | ~110 |
| 1:45 – 2:15 | Cómo funciona por dentro y resultados medidos | **Técnico (35 %)** | D4 y D5 | ~70 |
| 2:15 – 2:45 | Negocio: quién paga, costos y adopción | Negocio (20 %) | D6 | ~70 |
| 2:45 – 3:00 | Diferenciación y cierre | Innovación (15 %) | D7 | ~35 |

**Roles:** uno habla; uno opera la laptop (dashboard) y sostiene el celular del guardia (Telegram); uno o dos actúan frente a la cámara (entrar en grupo, dejar la mochila, acostarse en la colchoneta).

---

## 3. Diapositivas y guion

### D1. Portada y gancho (0:00 – 0:10) · Validación

- **En pantalla:** «Tres60 SafeCampus: ojos extra para el personal de seguridad», el logo y una foto real de una sala o una pantalla de cámaras del campus.
- **Decir:** «En el Perú, **8 de cada 10 personas** temen ser víctimas de un delito, y los jóvenes de 15 a 29 años, la edad universitaria, son el grupo más victimizado.» *(INEI, verificar el semestre.)*

### D2. El dolor: quién lo tiene, cómo lo resuelven hoy y qué falla (0:10 – 0:30) · Validación

La rúbrica pide **qué problema, quién lo tiene, la evidencia, cómo lo resuelven hoy y qué dificultades persisten.** La diapositiva tiene cuatro bloques:

| Bloque | Contenido | Fuente |
|---|---|---|
| **Quién lo tiene** | El operador de cámaras y el guardia de la universidad; detrás de ellos, estudiantes y personal | Lean Canvas |
| **Evidencia pública** | Robos de laptops en aulas y laboratorios sin personal (UTEC, La Cantuta, Científica del Sur); estudiantes desmayados o tendidos en biblioteca y estacionamiento (USMP, PUCP); exámenes de admisión con unos 29,000 postulantes (UNMSM) | Investigación, sección 2.3 |
| **Cómo lo resuelven hoy** | Un operador mira muchas cámaras y los guardias hacen rondas. Con 4 pantallas se detecta cerca del **83 %** de los incidentes; con 16, el **64 %** (Tickner y Poulton) | Investigación, sección 2.4 |
| **Evidencia propia** | «En nuestra universidad hay **[X] cámaras** y **[Y] personas** mirándolas.» Cita del jefe de seguridad: «**[cita textual]**». Experimento: «**[N] de [10]** no notaron la mochila; los que sí, tardaron **[Z] s**». Encuesta: «**[%]** de **[n]** estudiantes…» | Entrevista, `experimento.py`, encuesta |

- **Decir (unas 50 palabras):** «Las cámaras ya están, pero alguien tiene que mirar la correcta en el momento justo. En nuestra universidad hay [X] cámaras y [Y] personas mirándolas. Simulamos una sala de monitoreo: [N] de 10 compañeros no notaron la mochila abandonada, y quienes la vieron tardaron [Z] segundos.»
- **No decir:** que el sistema evita asaltos en la calle. Las cámaras del campus no cubren la vía pública y el sistema no detecta «robos».

### D3. La solución en una frase (0:30 – 0:45) · Innovación y UX

- **En pantalla:** el flujo en una línea, con íconos: `Cámara existente → IA detecta → reglas objetivas → alerta con foto → el guardia decide → registro y métricas`.
- **Decir (unas 35 palabras):** «Tres60 SafeCampus analiza las cámaras que ya existen, verifica criterios objetivos (cuántas personas, cuánto tiempo, en qué posición) y avisa al guardia en tiempo real. **No reemplaza al personal: cada alerta la confirma una persona.**»

### DEMO EN VIVO (0:45 – 1:45) · Técnico 35 % y UX 15 %

Se muestra **desde el punto de vista del usuario**, desde que entra hasta que obtiene el resultado. Se proyecta el dashboard (pestaña Monitoreo) y el celular del guardia queda a la vista.

| Paso | Acción en escena | Qué se ve | Qué decir | Criterio |
|---|---|---|---|---|
| 1 | El operador ya está en el dashboard | Video en vivo con recuadros, contador de personas y mapa del campus | «Este celular es una cámara del campus.» | UX |
| 2 | Entran 3 personas y se quedan 5 s | El contador sube; aparece una alerta **naranja** (prioridad media) con sonido; la cámara se pone roja en el mapa | «Supera el umbral 5 segundos y alerta: aglomeración.» | Técnico |
| 3 | Se muestra el celular del guardia | Llega por Telegram **con foto y botones** | «Le llega al guardia en ronda, con evidencia.» | UX |
| 4 | Alguien deja la mochila y se va | Contador `00:05/00:20` y alerta de objeto desatendido | «El conteo empieza cuando no hay nadie cerca. En la demo son 20 segundos; en la realidad, 10 minutos.» | Técnico |
| 5 | Si la IA está activa: se lee la descripción | «🤖 IA: se observa una mochila sola en el piso… Coincide: sí» | «La IA describe la foto en una frase; no decide.» | Técnico (IA) |
| 6 | El guardia toca **Confirmar** en Telegram | El dashboard cambia de estado al instante | «Lo que hace el guardia en el celular se ve en la central, y al revés.» | UX |
| 7 | **Marcar atendida** | Se registran el tiempo de respuesta y de atención, y quién lo hizo | «Todo queda medido.» | Técnico (datos) |
| 8 | Una alerta dudosa se **descarta** | Pasa a descartada, con su registro | «Si es una falsa alarma, se descarta en un toque.» | UX (manejo de errores) |
| 9 | Pestaña **Configuración**: mover un deslizador | El nuevo umbral se aplica en un segundo | «Cada universidad ajusta sus criterios, en vivo.» | Técnico y UX |
| 10 | Pestaña **Estadísticas** (5 s) | Tasa de confirmación y tiempos por tipo | «Y la jefatura ve cuánto se tarda en detectar y atender.» | Técnico (datos) |

**Si falta tiempo**, se saltan los pasos 9 y 10 y se muestran en las preguntas. **Nunca** se saltan los pasos 2, 3, 6 y 7: son el flujo completo.

**Persona en el suelo:** solo se incluye si salió bien en el ensayo final con colchoneta. En el ensayo del 5 de noviembre dio 3 falsas alarmas y ninguna correcta confirmada (`resultados-pruebas-2026-11-05.md`).

### D4. Cómo funciona por dentro (1:45 – 2:00) · Técnico 35 %

La rúbrica pide explicar **lógica, almacenamiento, integraciones e IA**, y para la IA, **qué recibe, qué produce y cómo se usa su resultado.**

**En pantalla, un diagrama:**

```
Cámara (celular hoy, RTSP mañana)
   │  cuadros de video
   ▼
YOLO11n (IA de visión) ──► personas, mochilas, bolsos y maletas, con recuadro y confianza
   │
   ▼
Motor de reglas (Python) ──► aglomeración · objeto desatendido · persona en el suelo · zona restringida
   │  alerta + foto
   ▼
SQLite (registro y tiempos) ──► Dashboard (Streamlit) ◄──► Telegram (foto y botones)
   │
   └──► IA generativa opcional (OpenAI): descripción de una frase, después de la alerta
```

**Tabla de IA (en la diapositiva o como anexo):**

| IA | Qué recibe | Qué produce | Cómo se usa |
|---|---|---|---|
| **YOLO11n** (visión por computadora, local, sin internet) | Cada cuadro del video | Recuadros de personas y objetos con su confianza | Las reglas cuentan personas, miden tiempos y posiciones, y deciden si hay alerta |
| **Modelo de visión de OpenAI** (opcional, en la nube) | La foto de la alerta **con los rostros difuminados**, reducida a 1024 px, y el mensaje de la regla | Una frase de hasta 25 palabras y «Coincide: sí, no o incierto» | Se agrega a la alerta en el dashboard y en Telegram. **Nunca decide, descarta ni retrasa la alerta** |

- **Decir (unas 35 palabras):** «Usamos dos IA. YOLO detecta personas y objetos en cada cuadro, sin internet. Las reglas convierten esas detecciones en alertas, que se guardan con sus tiempos. Un modelo de OpenAI describe la foto, pero no decide.»

### D5. Resultados medidos y estado del MVP (2:00 – 2:15) · Técnico 35 %

**Resultados:**

| Medición | Resultado | Fuente |
|---|---|---|
| Situaciones detectadas | **[X] de [Y]** | `evaluar.py` → `data/evaluacion/resumen.md` |
| Falsas alarmas | **[Z]** en **[minutos]** de video | `evaluar.py` |
| Tiempo desde que empieza la situación hasta la alerta | **[T] s** | `evaluar.py` |
| Velocidad | **[fps]** en una laptop **[con o sin GPU]** | Esquina del video o `verificar.py` |
| Personas frente al sistema | Las personas: **[N] de 10** lo notaron, en **[Z] s**. SafeCampus: **[T] s** | `experimento.py` |

**Implementado frente a pendiente** (la rúbrica lo pide explícitamente):

| ✅ Implementado y demostrable | 🟡 Pendiente (hoja de ruta) |
|---|---|
| Detección en vivo con YOLO11n y 4 reglas configurables | Varias cámaras IP (RTSP) a la vez |
| Foto de evidencia y registro en SQLite: nueva → confirmada o descartada → atendida, con tiempos y usuario | Horarios y calendario por zona (objetos en bibliotecas solo fuera de horario) |
| Dashboard: video, mapa, prioridad por color, sonido, estadísticas y deslizadores en vivo | Aviso cuando la cámara se pierde (hoy queda la pantalla negra, sin alerta) |
| Telegram con foto y botones, sincronizado con el dashboard | Modelo de pose para caídas |
| Descripción opcional con IA, con rostros difuminados | Usuarios y roles; difuminar también la foto que va por Telegram |
| `evaluar.py`, `experimento.py`, `verificar.py` y 34 pruebas automáticas | Piloto en modo sombra con cámaras reales y validación formal |

- **Decir (unas 35 palabras):** «Lo medimos: detectó [X] de [Y] situaciones, con [Z] falsas alarmas, y alertó en [T] segundos. Lo que ven funciona hoy; varias cámaras, horarios por zona y el piloto son el siguiente paso.»

### D6. Negocio: quién paga, cuánto cuesta y cómo se adopta (2:15 – 2:45) · Negocio 20 %

La rúbrica pide **quién la usa, quién paga, los costos principales, el incentivo para adoptarla y estimaciones sustentadas.**

| Bloque | Contenido | Sustento |
|---|---|---|
| **Quién la usa** | Operadores de la central y guardias en ronda | Lean Canvas |
| **Quién paga** | La universidad (jefatura de seguridad o administración), con una suscripción mensual por cámara o una licencia más implementación | `pitch-y-negocio.md` |
| **Incentivo** | La SUNEDU exige vigilancia 24 horas y ha denegado licencias por no tener personal suficiente. Las cámaras ya están compradas. Un puesto de monitoreo 24/7 cuesta unos **S/ 12,300 a 15,400 al mes** | Investigación, secciones 2.5 y 5.4 (el costo del puesto es un cálculo propio) |
| **Costos principales** | (1) Una PC por cada **[N]** cámaras, inversión única de **[S/ precio]**. (2) Instalación y calibración. (3) Soporte. (4) **API de OpenAI, opcional y el único pago por uso: de S/ 0.001 a 0.011 por alerta**, unos S/ 7 al mes en un piloto de 4 cámaras. (5) El software base es libre (YOLO bajo AGPL) | Investigación, secciones 1 y 5 |
| **Precio** | **[S/ Y] por cámara al mes** = de 3 a 5 veces el costo por cámara (PC ÷ 36 meses ÷ N cámaras, más el soporte), y menos de **[fracción]** de un operador adicional | Completar con sus fps y la cotización de la PC |
| **Adopción** | 1) Piloto gratuito de 1 mes en nuestra universidad → 2) caso de éxito con métricas → 3) otras universidades (alrededor de cien licenciadas) → 4) GovTech: centrales municipales, terminales y mercados | `pitch-y-negocio.md` |
| **Sostenibilidad** | Ingreso recurrente por suscripción; costo variable casi nulo; agregar una cámara es configuración, no desarrollo | — |

- **Decir (unas 70 palabras):** «Nuestro cliente es la universidad, que ya debe tener vigilancia las 24 horas y ya compró las cámaras. Un puesto de monitoreo 24/7 cuesta más de doce mil soles al mes; SafeCampus cuesta [Y] soles por cámara al mes. El único pago por uso, la IA de OpenAI, cuesta menos de un céntimo por alerta. Empezamos con un piloto gratuito aquí y seguimos con otras universidades y centrales municipales.»

### D7. Diferenciación y cierre (2:45 – 3:00) · Innovación 15 %

| Alternativa | Su límite | SafeCampus |
|---|---|---|
| Operador solo mirando pantallas | Su atención cae al aumentar las pantallas | Avisa cuando algo pasa, en cualquier cámara |
| Cámaras nuevas con analítica incluida | Hay que cambiar el equipo y casi solo detectan cruces de línea | Funciona con **cualquier cámara existente** |
| Plataformas comerciales (Milestone, BriefCam, Avigilon) | Precio no público; se venden por integradores y por canal | Bajo costo, en español y configurable por la universidad |
| Centrales con reconocimiento facial | Identifican personas: mayor riesgo legal y rechazo | **Detecta situaciones, no personas**; rostros difuminados |

- **Decir (unas 35 palabras):** «Las cámaras ya están; lo que falta es que alguien las mire a tiempo. SafeCampus le da ojos extra al personal, sin identificar a nadie. Queremos hacer el piloto en [universidad]. Gracias.»

---

## 4. Anexos para las preguntas

Diapositivas ocultas, listas para abrir si las piden:

| Anexo | Contenido | Fuente |
|---|---|---|
| A1. Privacidad y ley | Ley 29733 y su reglamento de 2024, directiva de videovigilancia, Ley 31814 de IA; sin reconocimiento facial; rostros difuminados; `store: false` | Investigación, sección 3 |
| A2. Costo de la IA | Tabla de costo por alerta y por mes; punto de equilibrio (debe ahorrar de 0.3 a 3 s por alerta) | Investigación, sección 5 |
| A3. Limitaciones y hoja de ruta | Los pendientes de D5 y las 12 semanas de la propuesta v2 | `propuesta-safecampus-v2.md` |
| A4. Reglas y parámetros | Demo frente a hipótesis real (3 personas y 5 s frente a 15 y 60 s; mochila 20 s frente a 10 min) | `mvp/README.md` |
| A5. Casos en campus | Tabla de incidentes y de la regla que aplica a cada uno | Investigación, sección 2.3 |
| A6. Ensayo honesto | Resultados del 5 de noviembre: qué funcionó y qué falló | `resultados-pruebas-2026-11-05.md` |
| A7. Arquitectura completa | Varias cámaras, buffer, estado «desconocido» y VLM | `propuesta-safecampus-v2.md`, sección 3 |

---

## 5. Preguntas probables, por criterio (respuestas de 20 s)

| Criterio | Pregunta | Respuesta |
|---|---|---|
| Validación | ¿Cómo saben que el problema existe? | «Datos del INEI, casos documentados en campus peruanos y nuestra propia evidencia: la entrevista con [cargo], la encuesta a [n] personas y el experimento, donde [N] de 10 no notaron la mochila.» |
| Validación | ¿Esto evita robos? | «No directamente: detecta situaciones observables, como alguien en un laboratorio fuera de horario o una mochila sola. Los asaltos en la calle quedan fuera del alcance de las cámaras del campus.» |
| UX | ¿Qué pasa si hay una falsa alarma? | «El guardia la descarta en un toque y queda registrada para recalibrar. Por eso cada alerta la decide una persona.» |
| UX | ¿Y si se cae la cámara? | Con honestidad: «Hoy el detector sigue con la pantalla negra y no avisa; es el primer pendiente de la hoja de ruta: marcar la cámara como "desconocida" y alertar.» |
| Técnico | ¿Qué IA usan y qué hace cada una? | La tabla de D4: YOLO detecta; las reglas deciden; OpenAI solo describe. |
| Técnico | ¿Qué tan preciso es? | «En nuestras pruebas, [X] de [Y], con [Z] falsas alarmas. Es un MVP evaluado en escenarios controlados; el siguiente paso es un piloto en modo sombra.» |
| Técnico | ¿Funciona sin internet? | «Sí: la detección, las reglas y el dashboard son locales. Solo Telegram y la descripción con IA necesitan internet, y si fallan la alerta llega igual al dashboard.» |
| Técnico | ¿Por qué no usar la IA para decidir? | «Porque los modelos de visión todavía fallan como detectores: el mejor obtuvo un F1 de 57 % al describir anomalías (CAVE, 2025). Por eso solo describe.» |
| Negocio | ¿Cuánto cuesta la IA de OpenAI? | «Entre S/ 0.001 y 0.011 por alerta, según el modelo: unos S/ 7 al mes en un piloto de 4 cámaras. Se paga sola si le ahorra al guardia unos pocos segundos por alerta.» |
| Negocio | ¿Por qué pagaría la universidad? | «Porque ya debe tener vigilancia 24 horas, ya compró las cámaras, y un puesto de monitoreo 24/7 cuesta más de S/ 12,000 al mes.» |
| Negocio | ¿Y la licencia de YOLO? | «Es AGPL: gratis para uso interno o código abierto. Si se vende como servicio cerrado, se compra la licencia empresarial o se cambia a un detector con licencia Apache.» |
| Innovación | San Marcos ya instala cámaras con reconocimiento facial. ¿Qué aportan ustedes? | «Somos complementarios: no identificamos a nadie, alertamos situaciones y medimos los tiempos de atención, sobre las cámaras que ya existen.» |
| Innovación | ¿Qué harían con más tiempo? | «Un piloto de un mes en modo sombra, varias cámaras, horarios por zona, aviso de cámara caída y pose para caídas.» |

---

## 6. Lista de verificación antes de presentar

**Evidencia, para Validación y Técnico**

- [ ] Cita textual del jefe de seguridad, con [X] cámaras y [Y] operadores
- [ ] Encuesta con n = [ ] respuestas
- [ ] Experimento «¿quién lo ve primero?» con 10 participantes
- [ ] Tabla de `evaluar.py` con el número de pruebas
- [ ] Cifras del INEI verificadas en el PDF original

**Demo, para Técnico, UX y el desempate**

- [ ] Celular fijo en trípode a 1.5 o 2 m; laptop enchufada; [fps] de 3 o más
- [ ] Demo completa (pasos 1 a 8) **3 veces seguidas sin fallas** en el lugar real
- [ ] Telegram probado con `python notificador.py`
- [ ] Si se usa la IA: saldo cargado, `ia.activa: true` y el modelo definido; y si no hay internet, la demo sigue
- [ ] Plan B: `python iniciar_demo.py --fuente videos/respaldo.mp4` y el video grabado de la demo completa
- [ ] `python iniciar_demo.py --limpiar` antes de entrar

**Pitch, para Negocio e Innovación**

- [ ] Precio con su cálculo ([N] cámaras por PC y cotización de la PC)
- [ ] Menos de 3:00, cronometrado y ensayado 5 veces o más
- [ ] Simulacro de preguntas con un «jurado difícil»
- [ ] Anexos A1 a A7 listos y ocultos
