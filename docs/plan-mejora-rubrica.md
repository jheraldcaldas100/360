# Tres60 SafeCampus: plan de mejora según la rúbrica (Frente S2, categoría Senior)

## 1. Qué nos piden y cómo nos califican

**Frente S2, Ciudades Inteligentes: Movilidad, Seguridad y GovTech.**

- **Problemática que atacamos:** "Inseguridad ciudadana y falta de alertas preventivas en tiempo real".
- **La solución debe:** "Procesar información en tiempo real, optimizar rutas o **alertas**, o digitalizar servicios públicos **reduciendo tiempos** y costos".

Nuestra frase de encaje: *"SafeCampus procesa video en tiempo real y genera alertas preventivas verificadas por una persona, reduciendo el tiempo en que el personal de seguridad detecta una situación de riesgo."*

| Criterio (Senior) | Peso | Qué evalúan | Qué tenemos hoy | Brecha principal |
|---|---|---|---|---|
| **Desarrollo técnico y MVP** | **35 %** (y es el **desempate**) | Lógica de backend, datos o IA real | Detector en vivo, 3 reglas, SQLite, dashboard | Falta demostrar con **números** que funciona y que **reduce tiempos** |
| Viabilidad de negocio | 20 % | Estrategia de adopción y sostenibilidad | Nada formal | Modelo de negocio, costos y adopción |
| Validación de problemática | 15 % | Claridad del dolor y **evidencia real** | Supuestos razonables | **Datos propios**: encuesta, entrevista, experimento |
| Diseño UX/UI y flujo | 15 % | Intuitividad del recorrido de usuario | Dashboard funcional básico | Flujo completo del guardia y pruebas con usuarios |
| Innovación, pitch y sustentación | 15 % | Originalidad, síntesis en 3 min y solidez en preguntas | — | Pitch ensayado y respuestas preparadas |

**Conclusión:** más de un tercio del puntaje y el desempate dependen del MVP técnico. La prioridad es que **la demo en vivo funcione siempre** y que tengamos **números medidos por nosotros**.

---

## 2. Las mejoras, priorizadas por impacto en la rúbrica

Esfuerzo: 🟢 menos de 2 h · 🟡 de 2 a 4 h · 🔴 más de 4 h.

### A. Desarrollo técnico y MVP (35 %)

| # | Mejora | Por qué suma puntos | Esfuerzo | Prioridad |
|---|---|---|---|---|
| A1 | **Demo en vivo estable**: celular en trípode, ensayos en el lugar real, videos de respaldo | Si la demo falla, se pierde el criterio más pesado | 🟢 | Imprescindible |
| A2 | **Alerta al celular del guardia** por Telegram, con foto y botones de confirmar o descartar | Cumple literalmente "alertas en tiempo real"; el jurado ve llegar la alerta a un celular | 🟡 | Imprescindible |
| A3 | **Métricas de tiempo en el dashboard**: tiempo de detección (desde que empieza la situación hasta la alerta), tiempo de respuesta (desde la alerta hasta la confirmación) y tasa de confirmación | Demuestra "**reduciendo tiempos**", que es lo que pide el frente | 🟢 | Imprescindible |
| A4 | **Script de evaluación** `evaluar.py`: corre videos etiquetados y genera una tabla de detecciones, omisiones, falsas alarmas y tiempos | Convierte "creemos que funciona" en "medimos que funciona": IA real con datos reales | 🟡 | Imprescindible |
| A5 | **Parámetros editables desde el dashboard** (deslizadores para personas, segundos y confianza) | Muestra en vivo que los criterios son **objetivos y configurables** | 🟡 | Alta |
| A6 | **Zona restringida dibujada** sobre el video (ya existe en el código, viene apagada) | Cuarto caso con muy poco esfuerzo; es el más confiable | 🟢 | Alta |
| A7 | **Descripción de la alerta con IA generativa** (GPT o Claude describe la foto en una frase) | Suma a "IA real" e innovación. Riesgo: necesita internet y una clave de API con saldo (ChatGPT Plus **no** incluye la API) | 🟡 | Opcional |
| A8 | Modelo de pose para caídas | Más preciso, pero más lento y complejo | 🔴 | **No hacer** en 3 días |

### B. Validación de problemática (15 %): evidencia propia

| # | Mejora | Cómo hacerlo | Esfuerzo |
|---|---|---|---|
| B1 | **Encuesta rápida** a estudiantes y personal (meta: 30 o más respuestas) | Google Forms con 5 preguntas: ¿te has sentido inseguro en el campus?, ¿has visto objetos abandonados, aglomeraciones o a alguien que necesitó ayuda?, ¿cuánto tardó en llegar seguridad?, ¿confiarías en alertas automáticas revisadas por una persona?, ¿te preocupa la privacidad? Difundir por los grupos de WhatsApp de la universidad | 🟢 |
| B2 | **Entrevista al personal de seguridad** (1 o 2 personas, 15 min) | Preguntar: cuántas cámaras hay, cuántas personas las monitorean, qué incidentes son más frecuentes y cómo se enteran hoy. **Una cita textual en el pitch vale mucho** | 🟢 |
| B3 | **Experimento "¿quién lo ve primero?"** | Armar un mosaico de 4 a 9 videos simulando una sala de monitoreo; en uno ocurre un evento (alguien deja una mochila o alguien cae). Pedir a 10 compañeros que avisen cuando lo noten y medir su tiempo; correr el mismo video en SafeCampus. Resultado tipo: *"las personas tardaron en promedio X s y 3 de 10 no lo notaron; SafeCampus alertó en Y s"* | 🟡 |
| B4 | **Datos públicos** | Buscar estadísticas oficiales de inseguridad del país o la ciudad, y datos de la propia universidad si son públicos. Citar siempre la fuente; no usar cifras sin fuente | 🟢 |

**B3 es lo más valioso de todo el plan:** valida el problema (a las personas se les escapan eventos) y la solución (el sistema los detecta antes) con datos propios, y además sirve de demostración en el pitch.

### C. Diseño UX/UI y flujo (15 %)

| # | Mejora | Esfuerzo |
|---|---|---|
| C1 | **Recorrido completo del guardia en 3 pasos**: llega la alerta (sonido, notificación y color) → ve la evidencia → confirma o descarta → marca "atendida". Agregar el estado **"atendida"** y su tiempo | 🟢 |
| C2 | **Prioridad visual**: persona en el suelo en rojo, objeto en naranja, aglomeración en amarillo; las alertas nuevas arriba y con sonido | 🟢 |
| C3 | **Vista de historial y estadísticas**: alertas por tipo y por hora, y los tiempos promedio de A3 | 🟡 |
| C4 | **Mapa simple del campus** (una imagen con un punto por cámara que se enciende al haber una alerta) | 🟡 |
| C5 | **Prueba con 3 a 5 usuarios**: darles la tarea "atiende esta alerta" sin explicarles nada, medir el tiempo y anotar dónde dudan. Mostrar el "antes y después" en el pitch | 🟢 |
| C6 | Diagrama del flujo de usuario (una diapositiva) | 🟢 |

### D. Viabilidad de negocio (20 %)

| # | Entregable | Contenido |
|---|---|---|
| D1 | **Lean Canvas** (una diapositiva) | Cliente: universidades públicas y privadas. Comprador: jefe de seguridad o administración. Usuario: operadores y guardias. Beneficiarios: la comunidad universitaria |
| D2 | **Modelo de ingresos** | Suscripción por cámara al mes (SaaS) o licencia instalada en la universidad más el costo de implementación. **Calcular el precio con datos reales**: comparar con el costo mensual de un operador adicional y con el de cámaras con analítica incluida |
| D3 | **Costos de operación** | Una PC con GPU procesa varias cámaras; se usan las cámaras existentes, sin comprar cámaras nuevas; el software es open source. Medir cuántas cámaras soporta su laptop (A4 da los fps) |
| D4 | **Estrategia de adopción** | 1) Piloto gratuito de 1 mes en nuestra universidad. 2) Caso de éxito con métricas. 3) Otras universidades y colegios. 4) Alianzas con instaladores de cámaras. 5) **GovTech**: centrales de monitoreo municipales, terminales y mercados (encaja con el frente S2) |
| D5 | **Diferenciación** | Funciona con cualquier cámara existente; flujo de verificación humana y registro de incidentes; parámetros configurables por espacio; privacidad por diseño (sin reconocimiento facial); bajo costo |
| D6 | **Riesgos y respuesta** | Privacidad (sin biometría, retención mínima), falsas alarmas (verificación humana y ajuste de umbrales), acceso a las cámaras (piloto institucional) |

### E. Innovación, pitch y sustentación (15 %)

**Pitch de 3 minutos (estructura sugerida):**

| Tiempo | Contenido |
|---|---|
| 0:00 – 0:25 | **El problema con datos propios**: cita del guardia y resultado del experimento B3 ("3 de cada 10 personas no notaron la mochila abandonada") |
| 0:25 – 0:45 | **La solución en una frase** y el flujo: cámara → IA → reglas objetivas → alerta → la persona decide |
| 0:45 – 1:45 | **Demo en vivo** (60 s): aglomeración o mochila frente al celular; la alerta llega al dashboard **y al celular del guardia**; se confirma con un toque |
| 1:45 – 2:15 | **Resultados medidos**: tabla de A4 (detecciones, falsas alarmas, tiempos) |
| 2:15 – 2:45 | **Negocio**: cliente, precio, piloto y escalamiento a GovTech |
| 2:45 – 3:00 | **Cierre**: "No reemplazamos al personal: le damos ojos extra". Pedido o próximo paso |

**Lo innovador, en tres puntos:** convierte cámaras existentes en alertas preventivas; los criterios son objetivos y configurables por espacio, por ejemplo objetos en bibliotecas solo fuera de horario; y el flujo humano queda en el centro, con privacidad por diseño.

**Preguntas probables del jurado (preparar una respuesta de 20 s para cada una):**

1. ¿Qué pasa con la privacidad? → Sin reconocimiento facial ni identificación; se detectan situaciones, no personas; la evidencia se guarda poco tiempo y solo la ve personal autorizado.
2. ¿Y las falsas alarmas? → Las decide una persona; los parámetros se ajustan por espacio; mostramos la tasa medida en A4.
3. ¿Qué tan preciso es? → Los números de A4, con su tamaño de muestra, y dicho con honestidad: "es un MVP; el siguiente paso es un piloto".
4. ¿Por qué no usar la analítica que ya traen las cámaras? → Funciona con cualquier cámara, agrega el flujo de verificación, el registro y las métricas, y es configurable por la universidad.
5. ¿Cuánto cuesta y quién paga? → D2 y D3.
6. ¿Cómo escala a muchas cámaras? → Una PC con GPU procesa varias cámaras; arquitectura por módulos (detector, reglas, dashboard).
7. ¿Qué pasa de noche o sin internet? → Funciona sin internet, instalado en la universidad; de noche depende de la cámara (infrarroja) y está en la hoja de ruta.
8. ¿Cómo lo validaron? → B1, B2 y B3.

---

## 3. Fases de trabajo (3 días)

Roles sugeridos para un equipo de 3 a 5 personas: **Técnico 1** (detector y reglas), **Técnico 2** (dashboard y Telegram), **Producto** (validación y UX), **Negocio y pitch**.

### Fase 1, Día 1: base sólida y evidencia en marcha

| Quién | Tareas | Hecho cuando… |
|---|---|---|
| Técnico 1 | Correr el MVP con el celular (A1); ajustar la posición, la `confianza` y el modelo (n o s); activar la zona restringida (A6) | Las 3 situaciones generan alerta en vivo en el lugar de la demo |
| Técnico 2 | Telegram (A2); estado "atendida" y métricas de tiempo (A3, C1) | La alerta llega al celular con foto; el dashboard muestra los tiempos |
| Producto | Lanzar la encuesta (B1); agendar la entrevista (B2); grabar los videos para el mosaico (B3) | Encuesta circulando y entrevista hecha o agendada |
| Negocio | Lean Canvas (D1); investigar precios de referencia (D2) | Primera versión del modelo de negocio |

### Fase 2, Día 2: mejoras y medición

| Quién | Tareas | Hecho cuando… |
|---|---|---|
| Técnico 1 | Script de evaluación (A4); grabar y etiquetar unos 20 clips (5 por situación más 5 sin eventos) | Hay una tabla de resultados reproducible |
| Técnico 2 | Deslizadores de parámetros (A5); prioridad visual y sonido (C2); historial y estadísticas (C3) | Un operador puede ajustar y revisar todo desde el dashboard |
| Producto | Experimento B3 con 10 personas; prueba de usabilidad C5 con 3 a 5 usuarios | Hay números del experimento y una lista de mejoras de UX |
| Negocio | Costos y precio (D2, D3); estrategia de adopción (D4); diapositivas en borrador | Diapositivas de negocio listas |

### Fase 3, Día 3: prueba final, pulido y pitch

| Hora | Tareas |
|---|---|
| Mañana | Corregir lo que salió de C5; corrida final de A4 para los números del pitch; **congelar el código al mediodía** (después solo se corrigen errores) |
| Mediodía | Grabar el video de respaldo de la demo completa (plan B) |
| Tarde | Ensayar el pitch **al menos 5 veces** con cronómetro; simulacro de preguntas, con un compañero de "jurado difícil"; revisar la lista de verificación |

### Si van atrasados, este es el orden en que se recorta

1. A7 (IA generativa) → 2. C4 (mapa) → 3. C3 (historial) → 4. A5 (deslizadores).

**Nunca recortar:** A1, A2, A3, A4, B2 y B3.

---

## 4. Lista de verificación antes de presentar

- [ ] La demo en vivo funcionó **3 veces seguidas** en el lugar real
- [ ] Video de respaldo grabado y probado en la laptop de la presentación
- [ ] La alerta llega al celular del guardia (Telegram) con foto
- [ ] El dashboard muestra el tiempo de detección y el tiempo de respuesta
- [ ] Tabla de resultados medida (A4), con el número de pruebas
- [ ] Resultado del experimento "¿quién lo ve primero?" (B3)
- [ ] Encuesta (n = ?) y cita del personal de seguridad
- [ ] Lean Canvas, precio con su cálculo y estrategia de adopción
- [ ] Pitch de menos de 3:00, ensayado 5 veces o más
- [ ] Respuestas a las 8 preguntas probables
- [ ] Mensajes de privacidad y de "apoyo, no reemplazo" claros
- [ ] Laptop cargada, hotspot del celular listo y trípode
