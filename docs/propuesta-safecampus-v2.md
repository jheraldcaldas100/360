# Tres60 SafeCampus: evaluación, propuesta consolidada y plan de validación

> Versión 2 de la propuesta. Parte del documento original (frente S2: Ciudades Inteligentes, Movilidad, Seguridad y GovTech) y agrega: evaluación de viabilidad por caso de uso, requisitos medibles, plan de validación con métricas, herramientas recomendadas, riesgos y una proyección de resultados.

---

## 1. Veredicto rápido

**El proyecto es viable como MVP académico o piloto en 10 a 12 semanas**, pero los cuatro casos de uso no tienen la misma dificultad. Hay que presentarlo con expectativas diferenciadas:

| Caso de uso | Madurez técnica | Dificultad | Riesgo principal | Recomendación para el MVP |
|---|---|---|---|---|
| 3.2 Ingreso a zona restringida | Alta | Baja | Cámaras con ángulo malo; sombras y reflejos | **Núcleo del MVP.** Debe funcionar casi perfecto. |
| 3.4 Aglomeraciones inusuales | Alta en densidad baja o media | Media | Oclusión cuando hay mucha gente: el conteo se subestima | **Núcleo del MVP.** Umbral por zona más una comparación con el histórico de esa hora. |
| 3.3 Objetos desatendidos | Media | Media-alta | Falsos positivos: mochilas junto a estudiantes sentados, objetos de mobiliario | Incluir: **activo en zonas de tránsito**; en bibliotecas, salones y salas de estudio, **solo fuera del horario de uso** (sección 4.3). |
| 3.1 Caídas o persona en el suelo | Media-baja con cámaras CCTV reales | Alta | Cámaras altas o cenitales; poca gente cae de verdad (pocos datos); confusión con personas sentadas en el piso | Incluir como **"persona tendida en el suelo más de N segundos"**, más robusto que detectar el instante de la caída. Validar en escenarios controlados. |

**Mensaje clave:** el valor no está en detectar todo, sino en **reducir el tiempo de detección de ciertos eventos sin inundar al operador de falsas alarmas.** La fatiga por alarmas es la causa número uno de que estos sistemas se apaguen en la práctica. Por eso la métrica estrella debe ser **falsas alarmas por cámara por hora**, no solo la "precisión".

### Posicionamiento honesto frente a lo que ya existe

Muchas cámaras y NVR comerciales (Hikvision, Dahua, Axis) ya traen detección de intrusión o cruce de línea. Plataformas como Avigilon, Genetec, Milestone o Verkada ofrecen analítica avanzada a un costo alto. El diferencial de SafeCampus debe ser:

1. **Agnóstico de cámara:** funciona sobre cámaras existentes (RTSP), incluso las antiguas.
2. **Flujo de verificación humana y registro de incidentes** pensado para el protocolo universitario, que es lo que las cámaras por sí solas no traen.
3. **Bajo costo y en español,** configurable por la propia universidad (zonas, horarios, umbrales).
4. **Métricas de gestión:** tiempos de atención, mapa de incidencias, tasa de alertas confirmadas.
5. **Privacidad por diseño:** sin reconocimiento facial ni atributos personales.

---

## 2. Concepto consolidado

> **Tres60 SafeCampus es un copiloto para el operador de videovigilancia:** analiza las cámaras existentes, detecta cuatro tipos de situaciones observables (intrusión, aglomeración, objeto desatendido y persona en el suelo), propone alertas con evidencia y deja la decisión al personal de seguridad. Cada decisión humana retroalimenta al sistema para reducir las falsas alarmas.

Principios de diseño:

- **Humano en el bucle (human-in-the-loop):** ninguna alerta se convierte en incidente sin confirmación humana.
- **Eventos observables, no personas:** detecta conductas o situaciones, nunca identidad, género, edad ni etnia.
- **Configurable por espacio:** cada cámara tiene sus propias zonas, horarios, umbrales y sensibilidad.
- **Medible:** cada alerta guarda su resultado (confirmada o descartada, con motivo) para calcular métricas reales.

---

## 3. Arquitectura propuesta para el MVP

```
 Cámaras IP (RTSP) / videos de prueba
            │
            ▼
 ┌──────────────────────┐
 │ Ingesta de video     │  OpenCV/FFmpeg; reconexión automática; 5 a 10 fps por cámara
 │ + buffer circular    │  (guarda los últimos ~15 s para armar el clip de evidencia)
 └─────────┬────────────┘
           ▼
 ┌──────────────────────┐
 │ Percepción (IA)      │  Detector (personas, mochilas, bolsos, maletas)
 │                      │  + tracker (ByteTrack/BoT-SORT) + pose (keypoints)
 └─────────┬────────────┘
           ▼
 ┌──────────────────────┐
 │ Motor de reglas      │  Zonas (polígonos), horarios, tiempos mínimos,
 │ por caso de uso      │  umbrales, enfriamiento (cooldown) entre alertas
 └─────────┬────────────┘
           ▼
 ┌──────────────────────┐   opcional
 │ Verificación por IA  │◄─ Modelo de visión y lenguaje (VLM) que revisa el clip
 │ de segunda etapa     │   y da una descripción y un nivel de confianza
 └─────────┬────────────┘
           ▼
 ┌──────────────────────┐      ┌───────────────────────┐
 │ Alertas + registro   │─────►│ Dashboard (operador)  │
 │ SQLite: eventos,     │      │ confirmar / descartar │
 │ evidencias, auditoría│      │ + motivo + atención   │
 └─────────┬────────────┘      └───────────────────────┘
           ▼
  Notificaciones (Telegram, correo, webhook)
```

Decisión importante: **Streamlit sirve para el dashboard de alertas e historial, pero no para mostrar video en vivo de varias cámaras con baja latencia.** Separar en dos procesos:

1. **Worker de análisis** en Python, uno por cámara o uno multihilo, que escribe eventos y evidencias.
2. **Dashboard** en Streamlit, que lee SQLite y muestra alertas, snapshots, clips y estados.

Si después se necesita video en vivo dentro del dashboard, usar MediaMTX (re-streaming por WebRTC o HLS) o migrar el frontend a FastAPI con React.

---

## 4. Diseño técnico por caso de uso (reglas y parámetros)

Todos los parámetros son **configurables por cámara o zona** y empiezan con un valor inicial que se calibra en la fase de validación.

### 4.1 Ingreso a zona restringida

- **Lógica:** persona detectada y seguida cuyo **punto de apoyo** (centro inferior del recuadro, es decir, los pies) entra a un polígono, dentro de un horario no autorizado, y permanece ahí `t_min` segundos.
- **Parámetros:** `polígono`, `horario_restringido`, `t_min` (inicial: 2 s), `confianza_min` (0.5), `cooldown` (60 s por track).
- **Variantes:** cruce de línea con dirección (entrar o salir), que es útil en puertas.
- **Por qué los pies y no el centro del recuadro:** reduce falsas alarmas por perspectiva, por ejemplo cuando alguien camina delante de la zona.

### 4.2 Aglomeración inusual

- **Lógica:** conteo de personas dentro de la zona (promedio móvil de 10 a 30 s) y comparación con:
  - un **umbral absoluto** (aforo seguro de la zona), y
  - un **umbral relativo** al histórico de esa zona en ese día y hora (por ejemplo, más de 2.5 veces la mediana).
- **Parámetros:** `aforo_max`, `factor_vs_historico`, `ventana_s`, `t_sostenido` (inicial: 60 s).
- **Extra útil:** detectar el **cambio brusco** (dispersión repentina o concentración rápida), que suele indicar un incidente.
- **Límite conocido:** con más de unas 50 personas por cuadro y mucha oclusión, el detector subestima. Si eso importa, evaluar modelos de estimación de densidad (tipo CSRNet) en una segunda versión.

### 4.3 Objeto desatendido

En bibliotecas, salones y salas de estudio **el personal ya avisa cuando alguien deja sus cosas mucho tiempo.** El sistema no debe duplicar ese proceso ni generar ruido mientras esos espacios están en uso. Por eso la regla depende de **dos cosas: el tipo de zona y el horario.**

#### Política por tipo de zona

| Tipo de zona | Ejemplos | Durante el horario de uso | Fuera del horario de uso (sin clases o cerrado) | Tipo de alerta |
|---|---|---|---|---|
| **Tránsito** | Pasillos, accesos, escaleras, patios, paraderos | **Activa** (`t_abandono` de 2 a 5 min, sin persona cerca) | Activa (`t_abandono` más corto) | *Objeto desatendido*, prioridad media o alta |
| **Estancia** | Biblioteca, salones, salas de estudio, comedores | **Desactivada:** la cubre el personal | **Activa:** el espacio debería estar vacío | *Objeto olvidado o desatendido fuera de horario*, prioridad baja o media |
| **Excluida** | Depósitos, casilleros, zonas con mobiliario cambiante | Desactivada | Desactivada | No genera alerta |

#### Cómo se define "fuera de horario"

- **Horario fijo por zona** en la configuración, por ejemplo biblioteca de 07:00 a 22:00 y salones de 07:00 a 23:00 de lunes a sábado.
- **Horario académico:** se importa un CSV o calendario con las clases por salón. Un salón queda "fuera de horario" en los bloques sin clase, no solo de noche.
- **Margen de cierre:** se espera `margen_cierre` (inicial: 15 min) después del cierre o del fin de la clase antes de activar la regla, para que la gente salga y el personal haga su ronda.
- **Feriados y eventos especiales:** calendario de excepciones (exámenes, eventos nocturnos) que vuelve a desactivar la regla.

#### Lógica

- **Zona de tránsito**:
  1. Se detecta un objeto de clase mochila, bolso o maleta (clases COCO `backpack`, `handbag`, `suitcase`).
  2. El objeto queda **estático** (desplazamiento menor a X píxeles) durante `t_estatico`.
  3. **No hay ninguna persona** a menos de `radio_r` (en proporción a la altura media de una persona en esa cámara) durante `t_abandono`.
  4. Mejora: asociar el objeto con la persona que lo trajo (el track más cercano cuando apareció) y alertar cuando esa persona sale de la escena.
- **Zona de estancia fuera de horario**: la regla es más simple y más confiable, porque el espacio debería estar vacío:
  1. **No hay personas** en la zona durante `t_vacio` (inicial: 5 min).
  2. Hay un objeto detectado y estático en la zona.
  3. Se genera **una sola alerta agrupada por espacio** ("Salón 204: 2 objetos detectados tras el cierre") con un snapshot, en lugar de una alerta por objeto.

Beneficios del modo fuera de horario:

- Menos falsas alarmas, porque no hay estudiantes sentados junto a sus mochilas.
- Apoya la ronda de cierre del personal de seguridad o limpieza.
- Alimenta un flujo de **objetos perdidos.**
- **Dato extra:** detectar una persona en una zona de estancia fuera de horario se puede tratar como *ingreso a zona restringida* (sección 4.1) con el mismo calendario.

**Parámetros:** `tipo_zona` (tránsito, estancia o excluida), `horario_uso`, `calendario_academico`, `margen_cierre`, `t_abandono`, `t_vacio`, `radio_r`, `clases`.

**Validación específica:** comparar en el piloto los objetos que el sistema detecta tras el cierre con los que el personal encuentra en su ronda (sensibilidad), y medir cuántas alertas fueron objetos realmente olvidados frente a mobiliario o falsos positivos.

### 4.4 Caída o persona en el suelo

- **Lógica en dos niveles:**
  1. **Señal de caída:** con un modelo de pose (17 keypoints), descenso rápido de la cadera o los hombros, cambio de la orientación del torso de vertical a horizontal y cambio en la relación alto/ancho del recuadro.
  2. **Confirmación:** la persona **permanece horizontal o en el suelo** más de `t_suelo` (inicial: 10 a 20 s) sin incorporarse.
- **La alerta se genera en el paso 2.** Así se reducen falsas alarmas por gente que se agacha, se sienta en el piso o se amarra los zapatos.
- **Parámetros:** `t_suelo`, `angulo_torso_max`, `velocidad_descenso_min`, `zonas_excluidas` (por ejemplo, áreas verdes donde la gente se recuesta).
- **Límite conocido:** con cámaras muy altas o cenitales la pose se degrada. Hay que documentar en qué cámaras sí aplica.

### 4.5 Funcionalidad extra recomendada: salud de cámaras

Es muy valorada por los operadores y es fácil de hacer: alertar cuando una cámara está **caída, tapada, desenfocada o movida** (sabotaje o tamper). Detecta problemas reales desde el primer día.

---

## 5. El componente de "análisis con inteligencia artificial"

Hay tres niveles de IA. Conviene explicarlos así en la presentación:

| Nivel | Qué hace | Tecnología | Cuándo |
|---|---|---|---|
| 1. Percepción | Detecta personas y objetos, los sigue y estima la pose | YOLO (u otro detector), ByteTrack, modelo de pose | MVP |
| 2. Reglas contextuales | Convierte las detecciones en eventos según zona, tiempo y umbral | Motor de reglas propio, configurable | MVP |
| 3. Verificación y análisis con modelos de visión y lenguaje (VLM) | Revisa 3 a 5 fotogramas del clip de la alerta y responde preguntas cerradas ("¿Hay una persona tendida en el suelo? ¿Hay alguien junto a la mochila?"); genera una **descripción breve** para el operador y una **segunda opinión** que puede bajar la prioridad de alertas dudosas | VLM en la nube (Claude, GPT) o local (Qwen2.5-VL, Florence-2, Moondream) | MVP+ (experimental) |

Además, un **LLM** puede generar **reportes semanales** en lenguaje natural a partir del registro de incidentes: zonas críticas, horarios, tiempos de atención.

Reglas para usar VLM o LLM de forma responsable:

- El VLM **nunca descarta una alerta por sí solo.** Solo reordena la prioridad y agrega contexto.
- **Antes de enviar imágenes a un servicio externo, difuminar los rostros**, o usar un modelo local. Debe constar en la evaluación de privacidad.
- Medir si el VLM realmente mejora la precisión. Si no la mejora, no se usa (ver la sección 7).
- Medir latencia y costo por alerta.

---

## 6. Requisitos mejorados

### 6.1 Requisitos funcionales

| ID | Requisito | Criterio de aceptación |
|---|---|---|
| RF-01 | Ingerir video por RTSP y desde archivos de prueba | Conecta al menos 4 cámaras simultáneas; se reconecta sola en menos de 30 s si se cae el stream |
| RF-02 | Configurar por cámara: zonas (polígonos) con **tipo de zona** (tránsito, estancia o excluida), líneas, horarios, **calendario académico y feriados**, umbrales, tiempos mínimos y sensibilidad | Desde un archivo YAML o la UI; los cambios se aplican sin reiniciar todo el sistema |
| RF-03 | Detectar los 4 eventos definidos según las reglas de la sección 4 | Cumple las metas de la sección 7.2 |
| RF-04 | Generar alertas con: tipo, cámara, ubicación, fecha y hora, confianza, **snapshot con recuadro** y **clip de unos 10 s** (5 s antes y 5 s después) | El 100 % de las alertas tienen evidencia adjunta |
| RF-05 | Ciclo de vida de la alerta: `nueva → en revisión → confirmada / descartada (motivo) → atendida → cerrada` | Cada transición registra usuario y hora |
| RF-06 | Motivos de descarte estandarizados (persona sentada, objeto del mobiliario, sombra, prueba, otro) | Se usan para recalibrar umbrales |
| RF-07 | Enfriamiento y agrupación de alertas para no repetir el mismo evento | Como máximo 1 alerta por evento físico |
| RF-08 | Notificaciones por Telegram, correo o webhook según tipo y prioridad | Llegan en menos de 5 s desde la generación |
| RF-09 | Dashboard: lista de alertas por prioridad, filtros, detalle con evidencia, historial y métricas | Un operador nuevo lo usa sin capacitación de más de 15 min |
| RF-10 | Monitoreo de salud de cámaras (caída, obstrucción, desenfoque) | Alerta en menos de 60 s |
| RF-11 | Registro de auditoría de accesos y acciones | Quién vio, exportó o modificó cada evidencia |
| RF-12 | Roles: operador, supervisor y administrador | Solo el administrador configura zonas y retención |
| RF-13 | Exportar reportes (CSV o PDF) de incidentes y métricas | Por rango de fechas y zona |

### 6.2 Requisitos no funcionales

| ID | Requisito | Meta inicial |
|---|---|---|
| RNF-01 | Latencia del evento a la alerta (sin contar el tiempo mínimo de la regla) | p95 menor a 3 s |
| RNF-02 | Capacidad | 4 cámaras a 1080p y 5 a 10 fps en una laptop o PC con una GPU de gama media; documentar el resultado sin GPU |
| RNF-03 | Disponibilidad del worker | Se reinicia solo ante fallas y registra los errores |
| RNF-04 | Privacidad | Sin reconocimiento facial ni clasificación por atributos personales; rostros difuminados en las evidencias exportadas; retención configurable (por ejemplo, 30 días para alertas descartadas) |
| RNF-05 | Seguridad | Credenciales RTSP fuera del código; contraseñas con hash; acceso al dashboard solo desde la red interna o por VPN |
| RNF-06 | Funcionamiento local (on-premise) | Funciona sin internet; la nube es opcional (solo para el VLM y las notificaciones) |
| RNF-07 | Reproducibilidad | Versiones de modelos y configuraciones guardadas junto con cada evaluación |
| RNF-08 | Robustez | Desempeño documentado de día, de noche (cámara infrarroja) y con lluvia o contraluz |

### 6.3 Requisitos éticos y legales

- **Evaluación de impacto en privacidad** antes del piloto, según la ley de protección de datos personales del país. Por ejemplo: Ley 29733 en Perú, Ley 1581 en Colombia, LFPDPPP en México.
- **Aprobación institucional:** dirección de seguridad, TI, área legal y, si se graban escenas con voluntarios, consentimiento informado.
- **Señalización** de videovigilancia con analítica en las zonas del piloto.
- Como referencia de buenas prácticas, el **Reglamento de IA de la UE** prohíbe la identificación biométrica remota en tiempo real en espacios públicos, salvo excepciones. SafeCampus queda fuera de esa categoría precisamente porque **no identifica personas.** Conviene decirlo de forma explícita.
- **Política de uso:** el sistema no se usa para sancionar estudiantes ni para vigilar a trabajadores.

---

## 7. Cómo validar la idea

Hay que validar dos cosas distintas: **(A) que el problema y la solución le importan al cliente** y **(B) que la tecnología funciona con métricas aceptables.**

### 7.1 Fases de validación

| Fase | Duración | Objetivo | Entregable | Criterio para pasar a la siguiente fase |
|---|---|---|---|---|
| **0. Descubrimiento** | 1 a 2 semanas | Validar el problema con los usuarios reales | 3 a 5 entrevistas con jefes de seguridad y operadores; inventario de cámaras (cantidad, resolución, ángulo, acceso RTSP, marca del NVR); revisión del historial de incidentes (¿cuáles son los más frecuentes?); protocolo actual de atención | Al menos 3 de 5 entrevistados priorizan al menos 2 de los 4 casos, y hay acceso técnico a por lo menos 2 cámaras |
| **1. Benchmark offline** | 3 a 4 semanas | Medir la técnica con videos etiquetados | Datasets públicos más **videos propios escenificados** (con voluntarios y consentimiento); etiquetado del inicio y el fin de cada evento; script de evaluación | Cumple las metas de la tabla 7.2 en el conjunto de prueba |
| **2. Modo sombra** | 2 a 3 semanas | Medir falsas alarmas en condiciones reales | El sistema corre sobre 2 a 4 cámaras reales y **solo registra** las alertas, sin avisar a los operadores; el equipo revisa todas las alertas | FA/h dentro de la meta; ajuste de umbrales por cámara |
| **3. Piloto asistido** | 3 a 4 semanas | Medir el valor para el operador | Operadores usan el dashboard; **simulacros** planificados (caídas sobre colchonetas, mochilas dejadas, ingresos fuera de horario, aglomeraciones simuladas); comparación de "operador solo" contra "operador más SafeCampus" | Mejora significativa del tiempo y la tasa de detección (sección 7.3) y una tasa de aceptación aceptable |

### 7.2 Métricas técnicas (por tipo de evento)

Las métricas se calculan **a nivel de evento**, no de fotograma. Una alerta es un verdadero positivo si ocurre dentro de la ventana del evento real, con una tolerancia de ±N segundos.

| Métrica | Definición |
|---|---|
| Sensibilidad (recall) | Eventos reales detectados / eventos reales |
| Precisión | Alertas correctas / alertas emitidas |
| **FA/h** | Falsas alarmas por cámara por hora de operación. **Es la métrica clave para el operador.** |
| Latencia de detección | Tiempo entre el inicio real del evento y la alerta |
| Error de conteo (solo aglomeraciones) | MAE y error porcentual frente al conteo manual |

**Metas iniciales propuestas.** Son hipótesis que se calibran en la fase 0 con lo que el cliente considera tolerable:

| Evento | Sensibilidad | FA/h por cámara | Latencia p95 |
|---|---|---|---|
| Zona restringida | ≥ 95 % | ≤ 0.1 | ≤ 3 s después de `t_min` |
| Aglomeración | ≥ 90 % | ≤ 0.1 | ≤ 10 s después de `t_sostenido` |
| Objeto desatendido (tránsito) | ≥ 85 % | ≤ 0.3 | ≤ 5 s después de `t_abandono` |
| Objeto fuera de horario (estancia) | ≥ 90 % frente a la ronda del personal | ≤ 1 alerta falsa por espacio por noche | ≤ 1 min después de `t_vacio` |
| Persona en el suelo | ≥ 80 % (escenarios controlados) | ≤ 0.3 | ≤ 5 s después de `t_suelo` |

Ejemplo de por qué importa la FA/h: 0.3 FA/h con 20 cámaras en 12 horas de operación son **unas 72 falsas alarmas al día.** Ese número probablemente sea demasiado alto. Por eso los umbrales se ajustan por cámara y se limitan las zonas.

### 7.3 Métricas de valor (piloto)

- **Tiempo de detección:** con sistema frente a sin sistema, en los simulacros. Es la prueba directa de la "detección temprana".
- **Tasa de detección del operador** en los simulacros, con sistema frente a sin sistema.
- **Tasa de aceptación:** alertas confirmadas / alertas revisadas.
- **Tiempo de atención:** desde la alerta hasta que se atiende.
- **Usabilidad:** cuestionario SUS a los operadores (meta: 70 o más) y entrevistas cualitativas.
- **Carga de trabajo percibida:** NASA-TLX simplificado (¿el sistema le quita trabajo al operador o se lo agrega?).

### 7.4 Datasets públicos útiles

**Verificar la licencia de cada uno: muchos son solo para investigación.**

- **Caídas:** UR Fall Detection Dataset, Le2i Fall Detection, Multiple Cameras Fall Dataset, CAUCAFall.
- **Objetos abandonados:** ABODA, PETS 2006, i-LIDS / AVSS 2007.
- **Multitudes y conteo:** ShanghaiTech (densidad), MOT17 y MOT20 (seguimiento en escenas concurridas).
- **Anomalías generales y vigilancia:** UCF-Crime, VIRAT, CAVIAR, CUHK Avenue.
- **Datos propios (lo más importante):** grabar escenas con voluntarios **en las mismas cámaras del campus**, con consentimiento. Los datasets públicos no representan el ángulo ni la iluminación de su universidad.

---

## 8. Herramientas y recursos recomendados

| Necesidad | Herramienta | Comentario |
|---|---|---|
| Detección | **Ultralytics YOLO (v8 o 11)** | Rápido y bien documentado. ⚠️ **Licencia AGPL-3.0:** para uso comercial cerrado se necesita una licencia empresarial. |
| Detección (alternativas con licencia permisiva) | RF-DETR, D-FINE, YOLOX, RTMDet (MMDetection) | Apache 2.0; buena opción si se piensa comercializar |
| Seguimiento | ByteTrack, BoT-SORT | Integrados en Ultralytics y en `supervision` |
| Zonas, líneas, conteo y anotaciones | **`supervision` (Roboflow, MIT)** | Trae `PolygonZone`, `LineZone`, trackers y anotadores listos. Ahorra semanas. |
| Pose (caídas) | YOLO-pose, RTMPose (MMPose), MediaPipe | Comparar en las cámaras reales |
| Video | OpenCV, FFmpeg, **MediaMTX** (re-streaming RTSP, WebRTC o HLS) | MediaMTX también sirve para simular cámaras RTSP a partir de archivos de video |
| Optimización | ONNX Runtime, OpenVINO (CPU Intel), TensorRT (GPU NVIDIA) | Para escalar a más cámaras |
| Escalamiento a futuro | NVIDIA DeepStream, Savant | Pipelines multicámara en producción |
| Referencia de arquitectura | **Frigate NVR** (open source) | Buen ejemplo de NVR con detección, zonas y eventos |
| Etiquetado | CVAT, Label Studio, Roboflow | CVAT es ideal para video y seguimiento |
| Inspección de datos y errores | FiftyOne | Visualiza falsos positivos y falsos negativos |
| Evaluación | Scripts propios de métricas por evento; `py-motmetrics` para seguimiento | |
| VLM (segunda opinión) | Claude o GPT (nube); Qwen2.5-VL, Florence-2, Moondream (locales) | Difuminar rostros antes de enviar imágenes a la nube |
| Backend | FastAPI | Si se separa el dashboard del worker |
| Dashboard | Streamlit (MVP) → React (producto) | |
| Base de datos | SQLite (MVP) → PostgreSQL | |
| Notificaciones | Bot de Telegram, SMTP, webhooks | |
| Configuración y despliegue | YAML por cámara, Docker Compose | Instalación reproducible en el servidor de la universidad |
| Calidad | GitHub Actions, pytest, videos de regresión | Cada cambio se evalúa contra el mismo conjunto de videos |

**Hardware de referencia para el piloto:** una PC con una GPU de consumo (por ejemplo, de la gama RTX 3060 o 4060, con 8 a 12 GB) debería procesar varias cámaras a 5 a 10 fps con modelos pequeños (n/s). Sin GPU, contar con 1 a 3 cámaras a baja resolución. **Hay que medirlo en la fase 1** y no prometerlo antes.

---

## 9. Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Demasiadas falsas alarmas y los operadores ignoran el sistema | Alto | Modo sombra antes del piloto; umbrales por cámara; zonas limitadas; cooldown; VLM como filtro de prioridad; FA/h como métrica principal |
| No hay acceso a las cámaras (TI, legal) | Alto | Gestionarlo en la fase 0; plan B: cámaras propias o videos grabados en el campus |
| Ángulos y resolución de las cámaras no aptos (sobre todo para caídas) | Medio-alto | Inventario de cámaras; definir qué casos aplican en cada cámara |
| Rechazo por privacidad (estudiantes, sindicatos) | Alto | Sin biometría; evaluación de impacto; comunicación transparente; rostros difuminados; retención mínima |
| Pocos datos reales de caídas y abandonos | Medio | Escenificaciones con voluntarios; datasets públicos; reglas en lugar de modelos entrenados desde cero |
| Licencia AGPL de YOLO si se comercializa | Medio | Decidir temprano: licencia comercial o detector con Apache 2.0 |
| Alcance excesivo | Medio | Priorizar zona restringida y aglomeración; los otros dos casos, con alcance acotado |
| Noche, lluvia y contraluz | Medio | Evaluar por separado; documentar los límites |

---

## 10. Cronograma sugerido (unas 12 semanas)

| Semana | Actividad |
|---|---|
| 1-2 | Fase 0: entrevistas, inventario de cámaras, permisos; arquitectura base e ingesta de video |
| 3-4 | Detector, tracker y zonas: **zona restringida** completa; dashboard básico y SQLite |
| 5-6 | **Aglomeración** y **objeto desatendido**; evidencias (snapshot y clip); ciclo de vida de alertas |
| 7-8 | **Persona en el suelo** (pose); grabación de escenarios propios; benchmark offline (fase 1) |
| 9-10 | Modo sombra en cámaras reales (fase 2); calibración; VLM experimental; notificaciones |
| 11-12 | Piloto asistido con simulacros (fase 3); métricas de valor; informe final y demo |

---

## 11. ¿Cómo podría resultar el proyecto?

**Escenario realista, el más probable con un buen trabajo:**

- **Zona restringida:** funciona de forma confiable y es la demo más convincente.
- **Aglomeraciones:** el conteo y las alertas son útiles en patios y accesos; el histórico por hora permite detectar situaciones fuera de lo normal.
- **Objetos desatendidos:** funciona bien en pasillos y accesos con tiempos de 2 a 5 minutos, con algunas falsas alarmas que se reducen con la retroalimentación del operador.
- **Persona en el suelo:** funciona en cámaras con buen ángulo y en simulacros; se documentan sus límites con cámaras altas.
- **Evidencia de valor:** con los simulacros se puede mostrar algo como "con SafeCampus, el operador detectó X de Y eventos en Z segundos, frente a X' de Y en Z' segundos sin el sistema". **Ese resultado es el argumento central** para una universidad, un jurado o un inversionista.

**Escenario optimista:** el piloto convence a la universidad de extenderlo a más cámaras. El registro y las métricas (mapa de calor de incidentes, tiempos de atención) se vuelven el producto, y SafeCampus evoluciona a una plataforma de gestión de seguridad del campus.

**Escenario de riesgo:** sin acceso a cámaras reales o con demasiadas falsas alarmas, el proyecto se queda en una demo con videos. Se mitiga con la fase 0 temprana y el modo sombra.

**Visión de producto (post-MVP):** multisede, mapa del campus con las cámaras, reportes automáticos con LLM, integración con el protocolo de emergencias (botón de pánico, enfermería) y aprendizaje continuo con las alertas descartadas.

---

## 12. Próximos pasos inmediatos

1. Agendar 3 a 5 entrevistas con personal de seguridad y operadores (guion: incidentes más frecuentes, tiempos actuales, cuántas cámaras ve cada operador, qué alertas les servirían, cuántas falsas alarmas tolerarían).
2. Solicitar acceso de prueba a 2 cámaras, o grabar videos propios con permiso.
3. Elegir el detector según la licencia: Ultralytics (AGPL) o una alternativa con Apache 2.0.
4. Crear la estructura del repositorio: `ingest/`, `perception/`, `rules/`, `alerts/`, `dashboard/`, `eval/`, `configs/`.
5. Definir el formato de etiquetado de eventos (inicio, fin, tipo, cámara) y el script de evaluación **antes** de programar las reglas.
6. Implementar zona restringida de punta a punta (video → alerta → dashboard → confirmar o descartar) como primer hito.
