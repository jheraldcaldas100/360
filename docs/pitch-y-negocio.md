# Tres60 SafeCampus: negocio, pitch y preguntas del jurado

> Material para el día 3. Los valores entre corchetes, como **[X]**, se completan con **sus propias mediciones**: la evaluación (`evaluar.py`), el experimento (`experimento.py`), la encuesta y la entrevista. **No inventen cifras:** el jurado valora la evidencia real, y una cifra sin fuente es lo primero que cuestionan.

---

## 1. Lean Canvas

| Bloque | Contenido |
|---|---|
| **Problema** | 1) Los operadores vigilan muchas cámaras a la vez y se les escapan situaciones de riesgo. 2) Las alertas dependen de que alguien esté mirando la cámara correcta en el momento justo. 3) No hay registro ni métricas de cuánto se tarda en detectar y atender. |
| **Segmento de clientes** | Universidades públicas y privadas con cámaras de vigilancia. *Primeros clientes (early adopters):* universidades con central de monitoreo y pocos operadores para muchas cámaras. |
| **Propuesta de valor única** | "Ojos extra para el personal de seguridad": convierte las cámaras que ya existen en **alertas preventivas en tiempo real**, verificadas por una persona, con evidencia y métricas de tiempo. |
| **Solución** | IA (YOLO) más reglas con parámetros objetivos y configurables por espacio; alerta en el dashboard y en el celular del guardia; flujo confirmar → atender; registro y estadísticas. |
| **Canales** | Piloto directo con la oficina de seguridad de nuestra universidad; alianzas con instaladores de cámaras; redes y eventos de gestión universitaria. |
| **Fuentes de ingreso** | Suscripción mensual por cámara (SaaS), o licencia instalada en la universidad más implementación. Soporte y ajustes como servicio. |
| **Estructura de costos** | Desarrollo y soporte; una computadora con GPU por cada grupo de cámaras (en la universidad); instalación y calibración; servidores solo si se usa la nube. |
| **Métricas clave** | Tiempo desde que empieza la situación hasta la alerta; tiempo de respuesta del guardia; tasa de alertas confirmadas; falsas alarmas por cámara al día; cámaras activas. |
| **Ventaja diferencial** | Funciona con **cualquier cámara existente**; el flujo de verificación humana es el centro del producto; configurable por espacio (por ejemplo, objetos en bibliotecas solo fuera de horario); privacidad por diseño (sin reconocimiento facial); datos medidos en el propio campus. |

---

## 2. Cálculo del precio (completar con datos reales)

La idea es mostrar que el precio tiene lógica, no que sea exacto.

1. **Costo de la alternativa.** Un operador adicional cuesta al mes **[sueldo + beneficios de un operador en su país]** = **[A]**. Las cámaras con analítica incluida cuestan **[precio de referencia por cámara]** y obligan a cambiar el equipo.
2. **Nuestro costo por cámara.** Hardware: una PC con GPU de **[precio]** procesa unas **[N]** cámaras (estimar N con los fps de `verificar.py` y `evaluar.py`; con 5 fps por cámara basta). Amortizado en 36 meses: **[precio ÷ 36 ÷ N]** por cámara al mes. A eso se suma el soporte.
3. **Precio propuesto.** Entre 3 y 5 veces el costo por cámara, y siempre **muy por debajo** del costo de un operador adicional para el número típico de cámaras de una universidad, que son **[cámaras de su campus]**.
4. **Frase para el pitch:** "Monitorear **[cámaras]** cámaras con SafeCampus cuesta **[Y]** al mes, menos que **[fracción]** de un operador adicional, y funciona las 24 horas."

**Estrategia de adopción:**

1. Piloto gratuito de 1 mes en nuestra universidad.
2. Caso de éxito con métricas.
3. Otras universidades y colegios.
4. GovTech: centrales de monitoreo municipales, terminales, mercados.

**Sostenibilidad:** ingresos recurrentes por suscripción, costos bajos porque se reutilizan las cámaras, y software modular, así que agregar una cámara es configuración y no desarrollo.

---

## 3. Guion del pitch (3 minutos, unas 420 palabras)

> Ensayen con cronómetro. Si se pasan, recorten la sección de negocio, nunca la demo ni los resultados.

**[0:00 – 0:25] El problema, con evidencia propia**

"En nuestra universidad hay **[X]** cámaras y **[Y]** personas mirándolas. Le preguntamos al personal de seguridad cómo se enteran de un incidente, y nos dijeron: *'[cita textual de la entrevista]'*. Hicimos un experimento: simulamos una sala de monitoreo con **[4]** cámaras y le pedimos a **[10]** compañeros que avisaran si veían algo raro. **[N] de [10] no notaron la mochila abandonada**, y quienes la vieron tardaron **[Z]** segundos en promedio."

**[0:25 – 0:45] La solución**

"Por eso creamos **Tres60 SafeCampus**: una IA que analiza las cámaras que ya existen, verifica criterios objetivos (cuántas personas, cuánto tiempo, en qué posición) y alerta al guardia en tiempo real. **No reemplaza al personal: cada alerta la confirma una persona.**"

**[0:45 – 1:45] Demo en vivo**

"Este celular es nuestra cámara."

1. Entran 3 compañeros: "El sistema cuenta personas; al superar el umbral durante 5 segundos… alerta de aglomeración".
2. "Y llega al celular del guardia, con foto." Muestren Telegram y toquen **Confirmar**.
3. Alguien deja la mochila y se va: "El contador empieza cuando no hay nadie cerca. En la demo son 20 segundos; en la realidad, 10 minutos".
4. En la pestaña Configuración, muevan un deslizador: "Cada universidad ajusta sus propios criterios, en vivo".

**[1:45 – 2:15] Resultados medidos**

"No nos quedamos en la demo. Grabamos **[20]** situaciones en el campus y medimos: detectó **[X] de [Y]** situaciones, con **[Z]** falsas alarmas, y alerta en **[T]** segundos desde que empieza la situación. Procesa cada imagen en unos **[ms]** milisegundos, sin internet."

**[2:15 – 2:45] Negocio**

"Nuestros clientes son las universidades. Cobramos una suscripción por cámara que cuesta menos que **[fracción]** de un operador adicional. Empezamos con un piloto gratuito aquí, y el mismo sistema sirve para colegios y para centrales de monitoreo municipales."

**[2:45 – 3:00] Cierre**

"Las cámaras ya están; lo que falta es que alguien las mire a tiempo. **SafeCampus le da ojos extra al personal de seguridad.** Queremos hacer el piloto en **[universidad]**. Gracias."

---

## 4. Preguntas del jurado: respuestas preparadas (20 segundos cada una)

| Pregunta | Respuesta |
|---|---|
| **¿Y la privacidad?** | "No identificamos a nadie: no hay reconocimiento facial ni clasificamos por género, edad o rasgos. Detectamos situaciones, no personas. Si se usa la IA en la nube, difuminamos las caras antes de enviar la foto. La evidencia la ven solo los usuarios autorizados y se guarda poco tiempo." |
| **¿Qué pasa con las falsas alarmas?** | "Por diseño, cada alerta la confirma una persona, y medimos [Z] falsas alarmas en [horas] de video. Los parámetros se ajustan por espacio, y cada descarte queda registrado para calibrar." |
| **¿Qué tan preciso es?** | "En nuestras pruebas detectó [X] de [Y] situaciones. Es un MVP evaluado en escenarios controlados; el siguiente paso es un piloto en modo sombra con cámaras reales para medir en operación." |
| **¿Por qué no usar la analítica que ya traen las cámaras?** | "Solo las cámaras nuevas y caras la traen, y suelen detectar cruces de línea. SafeCampus funciona con cualquier cámara, agrega el flujo de verificación y atención, el registro y las métricas, y criterios configurables por espacio." |
| **¿Cuánto cuesta? ¿Quién paga?** | "La universidad, por suscripción por cámara: [Y] al mes por [cámaras], menos que [fracción] de un operador. El hardware es una PC por cada [N] cámaras." |
| **¿Cómo escala?** | "Cada cámara se analiza de forma independiente; agregar cámaras es agregar capacidad de cómputo y configuración. El diseño es modular: detector, reglas, alertas y dashboard." |
| **¿Funciona de noche o sin internet?** | "Funciona sin internet: todo corre en la universidad, y la nube es opcional. De noche depende de la cámara: con cámaras infrarrojas funciona, y es parte de lo que mediríamos en el piloto." |
| **¿Cómo validaron el problema?** | "Con [n] respuestas de la encuesta, la entrevista al personal de seguridad y el experimento de la sala de monitoreo: [resultado]." |
| **¿Qué IA usan?** | "YOLO, un modelo de visión por computadora, para detectar personas y objetos en tiempo real, más reglas con parámetros objetivos. Opcionalmente, un modelo de visión y lenguaje describe la foto de la alerta." |
| **¿Por qué 10 minutos para la mochila?** | "Es nuestra hipótesis inicial, configurable por espacio. En bibliotecas y salones solo se activa fuera de horario, porque ahí el personal ya avisa durante el uso." |
| **¿Qué harían con más tiempo?** | "Un piloto de un mes en modo sombra, horarios por zona, más cámaras, un modelo de pose para caídas y la integración con el protocolo de emergencias." |

---

## 5. El día de la presentación

- **Antes de entrar:** correr `python verificar.py`, y luego `python iniciar_demo.py --limpiar` para empezar sin las alertas de los ensayos.
- **Pantalla:** el dashboard a pantalla completa en la pestaña Monitoreo y Telegram abierto en un celular visible, o duplicado en la pantalla.
- **Roles:** uno habla, uno opera la demo y uno o dos actúan (entran, dejan la mochila, se acuestan en la colchoneta).
- **Plan B listo:** si la cámara falla, `python iniciar_demo.py --fuente videos/respaldo.mp4`. Si falla todo, mostrar el video grabado de la demo completa.
- **Después del pitch:** tener abiertas la pestaña Estadísticas y la tabla de `data/evaluacion/resumen.md`, por si las piden en las preguntas.
