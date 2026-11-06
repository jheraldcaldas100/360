# Tres60 SafeCampus en universidades del Perú: relevancia, contextos de uso y costo-utilidad

> Investigación del 6 de noviembre de 2026. Responde tres preguntas:
>
> 1. ¿La problemática que aborda SafeCampus es relevante y aplicable en universidades del Perú? ¿Qué pruebas hay?
> 2. ¿En qué contextos conviene usarlo y en cuáles no?
> 3. Si la única herramienta de pago es la API de OpenAI para describir las alertas, ¿se justifica su relación costo-utilidad?
>
> **Cómo leer las cifras.** Cada dato lleva su fuente en la sección 8. La red de esta sesión bloqueó la descarga directa de los PDF oficiales (INEI, El Peruano, Contraloría), así que varias cifras salen de fragmentos de esas fuentes que devolvió el buscador. Las marcadas con **(verificar)** deben confirmarse en el documento original antes de usarlas en el pitch o en un informe formal. No se inventó ninguna cifra; donde no hay dato, se dice.

---

## 0. Resumen

| Pregunta | Respuesta corta | Confianza |
|---|---|---|
| ¿Es un problema relevante en el Perú? | **Sí.** La inseguridad es alta y los jóvenes de 15 a 29 años son el grupo más victimizado. Hay casos documentados en campus peruanos de robos de laptops en aulas y laboratorios, de emergencias médicas atendidas tarde y de aglomeraciones masivas. El Estado y las universidades ya invierten en cámaras. | Alta para el contexto general; **media** para el interior de los campus, porque no hay estadística oficial de incidentes dentro de las universidades. |
| ¿Es aplicable? | **Sí, con condiciones:** cámaras operativas, una persona que reciba y atienda las alertas, base legal para el tratamiento de imágenes y espacios donde los eventos sean visibles para la cámara. | Media-alta |
| ¿Dónde conviene? | Campus con muchas cámaras y pocos operadores; turnos nocturnos y fines de semana; laboratorios, bibliotecas y aulas fuera de horario; accesos y exámenes de admisión. | Media-alta |
| ¿Se justifica pagar la API de OpenAI? | **Sí, como función opcional y medida.** Con un modelo económico, cada descripción cuesta entre **S/ 0.001 y S/ 0.011** en el peor caso. Se paga sola si le ahorra al operador entre **0.3 y 3 segundos por alerta**. El costo no es la restricción real. Lo que hay que resolver es la privacidad (transferencia de imágenes al extranjero), la confiabilidad del texto y la demostración de que sirve. | Alta para el costo; **la utilidad todavía no se ha medido** |

**Conclusión:** la base del sistema (YOLO, reglas y verificación humana) atiende un problema real y no tiene costo de licencia. La descripción con OpenAI es un complemento barato que solo se justifica si se configura bien (sección 5.7) y si se demuestra con los datos del propio piloto que ayuda al operador (sección 6).

---

## 1. Qué es el proyecto y qué se paga

SafeCampus analiza el video de una cámara con YOLO y aplica cuatro reglas: aglomeración, objeto desatendido, persona en el suelo y zona restringida. Cada alerta queda en SQLite con su foto, aparece en un dashboard de Streamlit, puede enviarse por Telegram, y una persona la confirma o la descarta. De forma **opcional**, `mvp/ia.py` envía la foto, con los rostros difuminados, a un modelo de visión de OpenAI que responde con una frase de hasta 25 palabras y un veredicto: «Coincide: sí, no o incierto».

| Componente | Herramienta | ¿Se paga? | Condición |
|---|---|---|---|
| Detección | Ultralytics YOLO11n | No | Licencia **AGPL-3.0**: gratis para uso interno o código abierto; si se vende como servicio cerrado hay que publicar el código o comprar la licencia empresarial |
| Video, reglas y registro | OpenCV, Python, SQLite | No | Software libre |
| Dashboard | Streamlit | No | Software libre |
| Aviso al guardia | API de bots de Telegram | No | Gratis; requiere internet |
| **Descripción de la alerta** | **API de OpenAI (Responses)** | **Sí, por uso** | Saldo prepagado en platform.openai.com; ChatGPT Plus no incluye la API |
| Hardware | Laptop o PC existente; GPU opcional | Inversión única | En el ensayo del 5 de noviembre, una laptop sin GPU llegó a 0.5 a 1.4 fps con todo abierto (`resultados-pruebas-2026-11-05.md`) |

Por eso la pregunta de costo-utilidad se concentra en la API de OpenAI: es el único gasto variable y recurrente.

---

## 2. ¿Es una problemática relevante en el Perú? La evidencia

### 2.1 La inseguridad es el contexto general

- **83.7 %** de la población urbana de 15 años o más cree que puede ser víctima de un delito en los próximos 12 meses (INEI, semestre julio a diciembre de 2025). **(verificar)**
- La victimización bajó a 18.2 % en 2021 y volvió a subir a **27.1 % en 2024**, según el análisis del IEP sobre datos del INEI.
- En el semestre noviembre de 2025 a abril de 2026, en Lima Metropolitana y el Callao, el **robo o intento de robo de dinero, cartera o celular** fue el delito más frecuente (INEI).
- Osiptel registró más de medio millón de celulares robados en 2024.

### 2.2 Los jóvenes en edad universitaria son el grupo más afectado

- En la medición del INEI que reportó **27.7 %** de víctimas en zonas urbanas (29.7 % en ciudades de 20 mil habitantes o más), el grupo de **15 a 29 años tuvo el porcentaje más alto: 33.7 %**, por encima del grupo de 30 a 49 años (30.9 %). La nota de El Peruano corresponde al semestre enero a junio de 2024. **(verificar el periodo)**
- Un estudio sobre representaciones sociales de la seguridad ciudadana en universitarios de Lima concluye que el miedo y la victimización los mantienen «constantemente alerta» (REDI-CEDIA, 2017).

**Lectura:** la población universitaria coincide con el grupo de edad más victimizado del país. Eso no prueba que los delitos ocurran dentro del campus, pero sí que la seguridad del estudiante es un problema prioritario.

### 2.3 Incidentes documentados en campus peruanos, y qué regla de SafeCampus los cubre

| Caso (fuente, fecha) | Qué pasó | Regla de SafeCampus que aplica | Qué habría aportado |
|---|---|---|---|
| UTEC, Barranco (Panamericana, abril de 2024) | Dos personas burlaron la seguridad y robaron laptops **aprovechando la desatención de una zona usada como biblioteca** | Zona restringida o de estancia **fuera de horario**; objeto desatendido | Alerta temprana de presencia en una zona sin personal |
| Universidad Nacional de Educación (La Cantuta) (Panamericana, mayo de 2024) | Desaparecieron **31 laptops** de un laboratorio | Zona restringida fuera de horario | Alerta y foto de evidencia del ingreso |
| Universidad Científica del Sur, Villa El Salvador (América TV, noviembre de 2023) | Dos personas se hicieron pasar por estudiantes y se llevaron 4 laptops de un aula; las víctimas dijeron que **la universidad no reaccionó a tiempo** | Objeto desatendido; registro con hora y foto | Evidencia con hora exacta para reaccionar y para la denuncia |
| USMP, Lima (Trome) | Una estudiante de Medicina **se desvaneció en la biblioteca**; la familia denunció que no recibió primeros auxilios a tiempo | Persona en el suelo | Aviso al personal en segundos, sin depender de que alguien esté mirando esa cámara |
| PUCP, Lima (La República, marzo de 2025) | Un vigilante encontró a un estudiante **tendido en el estacionamiento** cerca de la puerta 1 | Persona en el suelo | Aviso al personal sin depender de la ronda |
| UPN, Trujillo (La República, mayo de 2025) | Una estudiante murió dentro del campus, presuntamente por un paro cardiaco | Persona en el suelo | En emergencias cardiacas, cada minuto sin atención cuenta |
| UNMSM, admisión 2025-I y 2025-II (Andina) | **28,665** y **29,302** postulantes por proceso; Canal N reportó caos y aglomeración en un examen con una sola puerta de ingreso (año sin confirmar) | Aglomeración | Conteo por zona y aviso cuando se supera el aforo |
| UNMSM, toma del campus (RPP) | La universidad denunció robo de equipos y agresiones a su personal de seguridad | Zona restringida y aglomeración | Registro con evidencia, sin reconocimiento facial |
| Exteriores de la UNMSM, de la facultad San Fernando y de la Científica del Sur en Los Olivos (Correo, Panamericana 2023, América TV) | Asaltos frecuentes, a veces armados, a estudiantes en la calle | **Ninguna directamente** | Fuera de alcance: las cámaras del campus rara vez cubren la vía pública, y SafeCampus no detecta «robo» |

**Lectura:** los casos dentro del campus (robo de equipos en espacios sin personal, emergencias médicas y aglomeraciones masivas) coinciden con tres de las cuatro reglas. Los asaltos en la calle, que son los más mencionados en la prensa, **no** los resuelve SafeCampus, y conviene decirlo en el pitch para no prometer de más.

### 2.4 La cámara ya está; lo que falta es quien la mire

Las universidades y el Estado peruano ya invierten fuerte en cámaras, así que SafeCampus no le pide a nadie que compre cámaras nuevas:

- **UNMSM:** la ATU instala **21 cámaras 4K con reconocimiento facial** para una comunidad de más de **40,000 estudiantes**, junto con 879 m de cerco perimétrico en las avenidas Amézaga y Venezuela (El Peruano y Caretas, 2026).
- **UPAO, Trujillo:** desde mayo de 2024 controla el acceso al campus con reconocimiento facial (nota de la universidad).
- **Municipios de Lima:** Miraflores puso en marcha 565 cámaras con IA, con 1,364 operativas y la meta de 2,400 al cierre de 2026. Surco abrió una central con 2,000 cámaras con IA. En el Callao se inauguró una central de alrededor de **S/ 245 millones** con 1,100 cámaras (Caretas).
- **Mininter:** el Sistema Nacional de Videovigilancia Inteligente integra en su primera etapa **3,282 cámaras** de la PNP, municipios y privados en una nube policial (El Peruano y Panamericana). **(verificar la fecha)**

Pero tener cámaras no equivale a vigilar:

- **Las cámaras se apagan o no se mantienen.** La Contraloría reportó cerca de **30 %** de las cámaras municipales inoperativas en una supervisión nacional y, en otro operativo, **1,553 de 6,144 (20 %)**. En Lima y el Callao encontró **729 cámaras inoperativas** en 27 municipios, y el 42 % de ellos no tenía un plan para mantenerlas funcionando. **(verificar los años de cada informe)**
- **Una persona no puede mirar muchas pantallas.** En los estudios clásicos de Tickner y Poulton sobre monitoreo de CCTV, la detección de incidentes fue de aproximadamente **83 % con 4 monitores, 84 % con 9 y 64 % con 16**. Su estudio de 1972 encontró más incidentes perdidos cuando se repartían en 24 pantallas en lugar de 16. Son estudios antiguos y de laboratorio, pero la tendencia se repite en trabajos posteriores, como Wallace et al. (1997). Las guías de diseño de salas de control recomiendan **16 vistas por operador o menos**.
- **Ejemplo regional:** en Chile, la Contraloría encontró una central municipal con **un operador por turno para 132 cámaras** (CNN Chile). No es un dato peruano, pero muestra la proporción típica de una central sin analítica.

**Lectura:** el cuello de botella no es la cámara, sino la **atención humana**. Esa es exactamente la propuesta de SafeCampus: «ojos extra» que avisan cuando una de las muchas cámaras muestra algo que merece atención.

### 2.5 Las universidades están obligadas a tener vigilancia

- En el modelo de licenciamiento de la SUNEDU, la **Condición Básica de Calidad VII** exige servicios complementarios, entre ellos **seguridad y vigilancia** (guía oficial en gob.pe).
- La SUNEDU **denegó licencias** citando, entre otras causas, que la universidad «no cuenta con el personal suficiente para garantizar el servicio de vigilancia las 24 horas del día» (caso de la Universidad Santo Domingo de Guzmán, Exitosa).
- En 2025 la SUNEDU presentó un proyecto de reglamento que reorganiza las condiciones en seis ejes y mantiene los servicios complementarios. **(verificar si ya se aprobó)**

**Lectura:** la universidad ya debe pagar vigilancia 24 horas. SafeCampus **no sustituye** ese personal (la SUNEDU exige personas), pero lo hace más eficaz y genera **registros y métricas** útiles para demostrar el servicio en una supervisión.

### 2.6 Lo que la evidencia todavía no demuestra

1. **No hay estadística oficial de incidentes dentro de los campus peruanos.** La prensa cubre los casos graves; los menores (objetos perdidos, ingresos fuera de horario, desmayos leves) no se publican.
2. **No hay datos públicos de cuántas cámaras y operadores tiene cada universidad.**
3. **La relación entre más vigilancia y menos incidentes en universidades peruanas no está medida.**

Por eso la evidencia externa se debe completar con la **evidencia propia** que ya contempla el plan del equipo (`plan-mejora-rubrica.md`, B1 a B3): la entrevista al jefe de seguridad (cuántas cámaras, cuántos operadores, qué incidentes son frecuentes), la encuesta y el experimento «¿quién lo ve primero?». La sección 6 indica qué medir.

---

## 3. Encaje legal en el Perú

| Norma | Qué exige | Implicancia para SafeCampus |
|---|---|---|
| **Ley 29733** de Protección de Datos Personales y su **nuevo reglamento (D.S. 016-2024-JUS)**, vigente desde el 30 de marzo de 2025 | La imagen de una persona es un dato personal; se debe informar, tener base legal, aplicar medidas de seguridad y regular las transferencias | Hace falta un responsable del tratamiento, un aviso y un registro de los flujos de datos |
| **Directiva de videovigilancia** (R.D. 02-2020-JUS/DGTAIPD) | Cartel visible; conservación limitada de las grabaciones (30 a 60 días según el resumen de IAPP) | Definir la retención de las fotos de evidencia y de `data/` **(verificar si el reglamento de 2024 cambió el plazo)** |
| **Cláusulas contractuales modelo** para transferencia internacional (R.D. 74-2022-JUS/DGTAIPD) | Mecanismo para enviar datos personales al extranjero con garantías | Aplica a **OpenAI** (EE. UU.) y también a **Telegram** |
| **D.L. 1218** y su reglamento (D.S. 007-2020-IN) | Obligación de cámaras en establecimientos comerciales con aforo de 50 personas o más; interconexión con el Centro Nacional de Videovigilancia | No está claro que aplique a universidades; consultar con el área legal |
| **Ley 31814** de IA y su reglamento (**D.S. 115-2025-PCM**, vigente desde el 22 de enero de 2026) | Enfoque basado en riesgos; todo sistema de IA debe cumplir la Ley 29733 | Documentar el nivel de riesgo, la supervisión humana y la transparencia. SafeCampus no identifica personas, lo que lo aleja de los usos más riesgosos **(verificar la clasificación en el texto del reglamento)** |

**Hallazgo importante sobre los flujos de imágenes al extranjero.** En el código actual:

- A **OpenAI** se envía la foto **con los rostros difuminados** (`ia.py`), reducida a 1024 px.
- A **Telegram** se envía la foto de evidencia **sin difuminar** (`detector.py` llama a `telegram.enviar_alerta(..., ruta)` con la foto original).

Por lo tanto, la API de OpenAI **no es el único ni el mayor riesgo de privacidad**: Telegram también es una transferencia internacional, y con la imagen completa. Las dos deben constar en el aviso de privacidad y en la evaluación de impacto. Si la universidad no autoriza transferencias, la alternativa es mantener solo el dashboard local y un modelo de visión local (sección 5.6).

**Política de datos de OpenAI**, según su documentación oficial:

- Lo que se envía a la API **no se usa para entrenar** modelos.
- Los registros de monitoreo de abuso se guardan **hasta 30 días**. La retención cero (*Zero Data Retention*) existe, pero requiere la aprobación de OpenAI.
- En la API de Responses, el parámetro `store` vale **`true` por defecto**: la respuesta se guarda al menos 30 días para recuperarla después. **`ia.py` no lo desactiva**, y debería enviar `"store": false` (sección 5.7).

---

## 4. ¿En qué contexto conviene usarlo?

### 4.1 Según el tipo de universidad

| Perfil | ¿Conviene? | Por qué |
|---|---|---|
| Universidad grande con central de monitoreo y **muchas cámaras por operador** (por ejemplo, las públicas con campus extensos en Lima y regiones) | **Sí: es el cliente ideal** | Es donde la atención humana se satura (sección 2.4) |
| Universidad privada con **varias sedes** y monitoreo centralizado | **Sí** | Un operador vigila sedes que no conoce; las alertas con foto y la configuración por espacio le ayudan |
| Universidad regional con **presupuesto limitado** | **Sí, con cuidado** | La analítica comercial es cara y se cotiza solo por integradores; SafeCampus reutiliza las cámaras existentes. Hay que verificar que estén operativas |
| Instituto o sede pequeña con 1 o 2 vigilantes que **ven todo el espacio directamente** | **No es prioridad** | El problema de atención casi no existe |
| Universidad **sin protocolo** de quién atiende una alerta | **No todavía** | Una alerta que nadie atiende no reduce ningún tiempo; primero hay que definir el protocolo |
| Universidad que quiere **identificar personas** (listas negras, reconocimiento facial) | **No** | SafeCampus está diseñado para no hacerlo; para eso existen otros productos, con otro riesgo legal |

### 4.2 Según el espacio y el horario

| Espacio y momento | Regla | Por qué conviene | Evidencia |
|---|---|---|---|
| **Laboratorios, bibliotecas y aulas fuera de horario** (noches, fines de semana, vacaciones) | Zona restringida o de estancia con horario | Es cuando hay menos personal y los robos de equipos ocurren en espacios desatendidos | UTEC, La Cantuta, Científica del Sur (2.3) |
| **Pasillos, accesos, escaleras y patios** | Persona en el suelo; objeto desatendido en tránsito | Las emergencias médicas se detectan antes si no dependen de la ronda | USMP, PUCP, UPN (2.3) |
| **Exámenes de admisión, matrículas, eventos y comedor** | Aglomeración | Decenas de miles de personas en pocas horas | UNMSM: unos 29,000 postulantes por proceso (2.3) |
| **Turno nocturno con un solo operador** | Todas | Es cuando la proporción de cámaras por operador es peor | Tickner y Poulton; Contraloría de Chile (2.4) |
| **Cámaras con buen ángulo y operativas** | Todas | Las reglas dependen de ver los pies, el cuerpo completo o el objeto | Propuesta v2, sección 4 |

### 4.3 Cuándo activar la descripción con OpenAI y cuándo no

| Conviene activarla | No conviene activarla |
|---|---|
| Alertas que llegan al **celular del guardia en ronda** por Telegram: una frase se lee más rápido que una foto en una pantalla pequeña | Campus o espacios **sin internet estable**: la descripción no llega y el sistema debe funcionar igual |
| Reglas con **muchas falsas alarmas**, como persona en el suelo: el «Coincide: no o incierto» ayuda a priorizar. En el ensayo del 5 de noviembre, 3 de las 4 alertas de persona en el suelo fueron falsas | Sin la **aprobación legal** de la transferencia internacional (sección 3) |
| Turnos con **un solo operador** y muchas alertas, por ejemplo en exámenes de admisión | Para **decidir** o **descartar** alertas: los modelos de visión no son confiables como detectores (sección 5.6) |
| Para **reportes**: el texto queda en SQLite y permite buscar y resumir incidentes | Reglas con evidencia muy clara (zona restringida): la descripción agrega poco |
| Universidades **sin GPU** que no pueden correr un modelo de visión local | Durante la **validación principal** del piloto: la propuesta v2 ya lo indica, para medir su aporte por separado |

---

## 5. Relación costo-utilidad de la API de OpenAI

### 5.1 Cuánto consume una alerta

Para cada alerta, `ia.py` envía una foto reducida a 1024 px de ancho y una instrucción de unas 100 palabras, y limita la respuesta a 400 tokens (`max_output_tokens`).

- **Tokens de la imagen:** con una cámara de 1280x720, la foto queda en 1024x576. Los modelos actuales de OpenAI dividen la imagen en parches de 32x32 px y multiplican la cantidad por un factor de cada modelo: 576 parches equivalen a **692 tokens** con un factor de 1.2, 864 con 1.5 y 934 con 1.62. Con el método de teselas de modelos anteriores serían 1,105. OpenAI no publica el factor de la familia GPT-6, así que se usa un supuesto conservador.
- **Supuesto de entrada:** **1,300 tokens** (hasta unos 1,100 de imagen y unos 200 de texto).
- **Supuesto de salida:** **60 tokens** en el caso típico (la frase y el «Coincide») y **400** en el peor caso (el tope, si el modelo usa tokens de razonamiento).

### 5.2 Costo por alerta según el modelo

Precios de lista estándar de OpenAI en noviembre de 2026, en dólares por millón de tokens. Tipo de cambio de referencia: **S/ 3.46 por dólar** (3 de noviembre de 2026).

| Modelo | Entrada / salida (USD por 1M) | Costo típico por alerta | Peor caso por alerta |
|---|---|---|---|
| **GPT-6 Luna** (el más económico) | 0.10 / 0.50 | US$ 0.00016 (S/ 0.0006) | US$ 0.00033 (**S/ 0.0011**) |
| **GPT-6.1 Terra** (equilibrado) | 1.00 / 5.00 | US$ 0.0016 (S/ 0.0055) | US$ 0.0033 (**S/ 0.0114**) |
| GPT-5.6 Terra | 2.00 / 12.00 | US$ 0.0033 (S/ 0.0115) | US$ 0.0074 (S/ 0.0256) |
| GPT-6 Astra (insignia; **no recomendado**) | 10.00 / 50.00 **(verificar)** | US$ 0.016 (S/ 0.055) | US$ 0.033 (S/ 0.114) |

El modo *Batch* cuesta la mitad, pero no sirve aquí: devuelve resultados en horas, no en segundos.

### 5.3 Costo mensual según el escenario (peor caso)

| Escenario | Alertas al mes | GPT-6 Luna | GPT-6.1 Terra | GPT-5.6 Terra | GPT-6 Astra |
|---|---|---|---|---|---|
| **Piloto:** 4 cámaras, 20 alertas al día | 600 | S/ 0.69 | **S/ 6.85** | S/ 15.36 | S/ 68.51 |
| **Campus mediano:** 50 cámaras, 5 alertas por cámara al día | 7,500 | S/ 8.56 | **S/ 85.64** | S/ 192.03 | S/ 856.35 |
| **Campus grande:** 300 cámaras, 5 alertas por cámara al día | 45,000 | S/ 51.38 | **S/ 513.81** | S/ 1,152.18 | S/ 5,138.10 |

Cinco alertas por cámara al día es un supuesto **pesimista**: el presupuesto de carga de la propuesta v2 apunta a muchas menos. Aun así, el costo mensual es bajo.

### 5.4 Contra qué se compara

| Referencia | Monto | Fuente |
|---|---|---|
| Remuneración mínima vital | S/ 1,230 desde el 1 de octubre de 2026 (S/ 1,300 en el primer semestre de 2027) | D.S. 015-2026-TR |
| Sueldo de un operador de CCTV en Lima | S/ 1,900 a S/ 2,500 al mes, y hasta S/ 4,000 en algunos avisos | Computrabajo e Indeed **(fechas de los avisos sin confirmar)** |
| Costo para el empleador de un operador | Unos **S/ 2,940 a S/ 3,675** al mes (sueldo × 1.47 por EsSalud, gratificaciones, CTS y vacaciones; estimación propia del régimen general) | Cálculo propio |
| **Un puesto de monitoreo 24/7** (unas 4.2 personas) | Unos **S/ 12,300 a S/ 15,400** al mes | Cálculo propio |
| Analítica de video comercial | Sin precio público: Milestone, BriefCam y Avigilon venden licencias por canal a través de integradores | Páginas de los fabricantes |
| Centrales municipales con IA | Del orden de millones de soles (Callao: unos S/ 245 millones con obra y fibra) | Caretas |

**Comparación:** el escenario de campus grande con GPT-6.1 Terra (S/ 514 al mes) equivale a cerca del **3 a 4 % de un solo puesto de monitoreo 24/7**. Con GPT-6 Luna, al **0.3 a 0.4 %**. En una universidad pública, además, ese monto anual queda muy por debajo del umbral de 8 UIT (S/ 44,000 en 2026) que la Ley 32069 usa para las contrataciones menores **(verificar el procedimiento con logística: pagar una API extranjera con tarjeta puede requerir un trámite específico)**.

### 5.5 Punto de equilibrio: cuántos segundos debe ahorrar

El tiempo de un operador cuesta entre **US$ 0.0011 y US$ 0.0014 por segundo** (S/ 14 a S/ 18 por hora, con 208 horas al mes). La descripción se paga sola si le ahorra al operador al menos:

| Modelo | Segundos ahorrados por alerta para cubrir su costo (peor caso) |
|---|---|
| **GPT-6 Luna** | **0.2 a 0.3 s** |
| **GPT-6.1 Terra** | **2.3 a 2.9 s** |
| GPT-5.6 Terra | 5.2 a 6.5 s |
| GPT-6 Astra | 23 a 29 s |

Leer una frase en lugar de abrir y examinar una foto en el celular puede ahorrar varios segundos. **Pero es una hipótesis, no un dato:** hay que medirla (sección 6). Y el tiempo ahorrado se convierte en capacidad del operador, no en dinero, salvo que cambie la dotación de personal.

**El valor que más importa no es el tiempo del operador, sino el tiempo de respuesta ante un evento real.** Una persona desmayada atendida un minuto antes vale mucho más que cualquier costo de la API. Ese beneficio no se puede expresar en soles con rigor, pero es el argumento central del proyecto.

### 5.6 Utilidad: qué aporta y qué no la descripción

**Lo que aporta:**

1. **Contexto rápido** para el guardia en ronda que recibe la alerta en el celular.
2. **Segunda opinión** para priorizar las alertas dudosas, sin descartarlas nunca.
3. **Texto para buscar y para reportes** en el historial.
4. **Valor en la demo y en la rúbrica:** muestra IA generativa usada con responsabilidad.

**Lo que no aporta, según la evidencia:**

- **Los modelos de visión no son confiables como detectores.** En el benchmark CAVE (EMNLP 2025), el mejor modelo, GPT-4o, solo alcanzó un **F1 de 57 %** al describir anomalías en imágenes reales. Un estudio de 2026 («Are Multimodal LLMs Ready for Surveillance?») obtuvo como máximo un **F1 de 0.64** en detección de anomalías sin entrenamiento previo (ShanghaiTech) y observó un sesgo conservador. Por eso el diseño actual es correcto: **la IA describe, no decide.**
- **Las cifras comerciales** sobre cuánto reducen las falsas alarmas los modelos de visión (por ejemplo, 86 % en el caso de Calipsa con Prosegur) son **casos de venta**, no estudios independientes.
- **Riesgo de exceso de confianza.** En monitoreo clínico, la exposición a muchas falsas alarmas hizo más lenta la respuesta del personal (estudio del Children's Hospital of Philadelphia). Si el operador confía de más en un «Coincide: no», podría descuidar un evento real.

**Alternativa sin pago y sin transferencia internacional:** modelos de visión locales (Moondream, Florence-2, Qwen2.5-VL), ya mencionados en la propuesta v2. No cuestan por uso, pero necesitan una GPU y suelen describir peor. Convienen cuando la universidad no autoriza enviar imágenes al extranjero.

### 5.7 Riesgos del código actual que afectan el costo-utilidad, y cómo corregirlos

Revisión de `mvp/ia.py`. **No se modificó el código**; son recomendaciones para el equipo.

| # | Hallazgo | Efecto | Recomendación |
|---|---|---|---|
| 1 | `max_output_tokens: 400` sin controlar el razonamiento | En modelos con razonamiento, ese tope incluye los tokens de razonamiento; la respuesta puede volver con estado `incomplete` y **sin texto**, y aun así se cobran los tokens | Enviar `"reasoning": {"effort": "none"}`, o el nivel más bajo que admita el modelo; revisar `status` e `incomplete_details` y registrar cuándo falla |
| 2 | No envía `"store": false` | La respuesta queda guardada en OpenAI **al menos 30 días** | Agregar `"store": false` al cuerpo de la solicitud |
| 3 | `ia.modelo` vacío por defecto | Alguien podría elegir un modelo insignia y pagar unas 100 veces más | Recomendar **GPT-6 Luna** para empezar y **GPT-6.1 Terra** si Luna describe mal; anotar el modelo en cada alerta |
| 4 | No se registra el consumo | No se puede calcular el costo real por alerta | Guardar `usage.input_tokens` y `usage.output_tokens` de cada respuesta en SQLite |
| 5 | No hay límite de gasto | Un bucle de alertas falsas podría generar un gasto inesperado | Configurar un **límite y alertas de gasto** en el panel de OpenAI, y un tope diario de descripciones en `config.yaml` |
| 6 | El nivel de detalle de la imagen queda en `auto` | La guía de OpenAI advierte que `low` no siempre usa menos tokens en los modelos nuevos | Medir con `usage` antes de cambiarlo |
| 7 | La foto de Telegram va sin difuminar | Mayor riesgo de privacidad que la de OpenAI (sección 3) | Difuminar también la foto que se envía por Telegram, o enviar solo el texto |

### 5.8 Veredicto costo-utilidad

- **Costo:** **justificado.** Con GPT-6 Luna o GPT-6.1 Terra, el costo es marginal (céntimos al mes en el piloto y cientos de soles al mes en un campus grande con un supuesto pesimista), comparado con cualquier partida de seguridad.
- **Utilidad:** **plausible pero no demostrada.** Basta con que ahorre de 0.3 a 3 segundos por alerta. Debe medirse en el piloto.
- **Condiciones para que se justifique:** (1) que siga siendo **opcional y posterior a la alerta**; (2) usar un **modelo económico**, con `store: false`, razonamiento mínimo y un límite de gasto; (3) contar con la **aprobación legal** de la transferencia y difuminar también la foto de Telegram; (4) **medir** su aporte con los datos del piloto y apagarla si no ayuda.

---

## 6. Cómo demostrarlo con datos propios

Los datos ya se registran en SQLite; solo falta analizarlos.

| Qué medir | Cómo | Criterio para mantener la IA activa |
|---|---|---|
| **Concordancia** del «Coincide» con la decisión del operador | Comparar `descripcion_ia` con el estado final (confirmada o descartada) de cada alerta | El «Coincide: no» acierta en la mayoría de las alertas descartadas, **sin** marcar como «no» alertas confirmadas |
| **Tiempo de decisión** con y sin descripción | En el piloto, alternar alertas con y sin descripción (al azar) y comparar el tiempo de respuesta que ya calcula el dashboard | La diferencia supera el punto de equilibrio de la sección 5.5 (por ejemplo, más de 3 s con Terra) |
| **Costo real** por alerta | Sumar `usage` por alerta y multiplicar por el precio del modelo | Queda dentro del orden de magnitud de la tabla 5.2 |
| **Latencia** de la descripción | Diferencia entre la hora de la alerta y la de la descripción | Llega antes de que el operador decida; si llega después, no aporta |
| **Fallas** | Respuestas vacías, `incomplete` o errores HTTP | Menos del 5 % |

Y para la **relevancia del problema** (sección 2.6), completar en el pitch los valores entre corchetes de `pitch-y-negocio.md` con:

- La **entrevista al jefe de seguridad:** número de cámaras, operadores por turno, incidentes más frecuentes del último año y cuánto tardan hoy en enterarse.
- El **experimento «¿quién lo ve primero?»** (`experimento.py`): cuántas personas no notan el evento y en cuánto tiempo lo notan las que sí.
- La **encuesta** a estudiantes: victimización dentro del campus y aceptación de alertas revisadas por una persona.

---

## 7. Frases para el pitch, con su fuente

- «En el Perú, **8 de cada 10 personas** en zonas urbanas temen ser víctimas de un delito, y los jóvenes de 15 a 29 años son el grupo más victimizado» (INEI). **(Confirmar el semestre exacto antes de decirlo.)**
- «En universidades peruanas se han robado laptops de aulas, laboratorios y zonas de estudio sin personal, y se han reportado emergencias médicas en bibliotecas y estacionamientos» (casos de la sección 2.3).
- «Las cámaras ya existen: el Estado y las universidades invierten millones en ellas. Lo que falta es que alguien las mire a tiempo: la detección de una persona cae del 83 % al 64 % cuando vigila 16 pantallas en vez de 4» (Tickner y Poulton, citado en la literatura de CCTV).
- «La descripción con IA cuesta **menos de un céntimo de sol por alerta**, y se paga sola si le ahorra al guardia **unos pocos segundos**» (sección 5).
- «La IA no decide: describe. Los modelos de visión todavía fallan como detectores, por eso cada alerta la confirma una persona» (sección 5.6).

---

## 8. Fuentes

**Seguridad ciudadana (INEI y análisis)**

- INEI, boletín *Estadísticas de Seguridad Ciudadana*, julio a diciembre de 2025: https://www.inei.gob.pe/media/MenuRecursivo/boletines/seguridad_ciudadana_jul_dic_2025.pdf
- INEI, boletín noviembre de 2025 a abril de 2026: https://www.inei.gob.pe/media/MenuRecursivo/boletines/boletin_seguridad_nov25_abr26.pdf
- INEI, *Victimización en el Perú, 2025* (marzo de 2026): https://www.gob.pe/es/institucion/inei/informes-publicaciones/7938429-victimization-in-peru-2025
- El Peruano, «INEI: el 27,7 % de peruanos ha sido víctima de delincuencia…»: https://elperuano.pe/noticia/251200-inei-el-277-de-peruanos-ha-sido-victima-de-delincuencia-en-los-ultimos-6-meses-en-zonas-urbanas
- IEP, «La victimización en el Perú: ¿puede un indicador desviar el rumbo de la política de seguridad?»: https://criticaydebate.iep.org.pe/noticias/la-victimizacion-en-el-peru-puede-un-indicador-desviar-el-rumbo-de-la-politica-de-seguridad/
- DPL News, Osiptel: más de medio millón de celulares robados en 2024: https://dplnews.com/?p=237662
- REDI-CEDIA, *Social representations of citizen security in university students of Lima-Peru*: https://redi.cedia.edu.ec/document/462013

**Incidentes en campus**

- Panamericana, pareja burla la seguridad de UTEC y roba laptops: https://panamericana.pe/buenosdiasperu/locales/409428-pareja-burla-seguridad-utec-entra-robar-laptops-primera-vez-asaltan-zona
- Panamericana, alumnos de La Cantuta denuncian el robo de 31 laptops: https://panamericana.pe/buenosdiasperu/locales/411119-alumnos-cantuta-denuncian-extrano-robo-31-laptops-universidad
- América TV, ladrones fingen ser estudiantes para robar laptops (Villa El Salvador): https://www.americatv.com.pe/noticias/amp/actualidad/villa-salvador-ladrones-fingen-estudiantes-robar-laptops-universidad-n483580
- Trome, estudiante de Medicina de la USMP murió en la universidad: https://trome.com/actualidad/policiales/estudiante-de-la-facultad-de-medicina-de-la-usmp-murio-dentro-de-la-universidad-y-familiares-piden-explicaciones-noticia/
- La República, PUCP: la Fiscalía investiga la muerte de un alumno en el campus (marzo de 2025): https://larepublica.pe/sociedad/2025/03/13/pucp-fiscalia-investiga-muerte-de-alumno-en-campus-184847
- La República, estudiante fallece en el campus de la UPN Trujillo (mayo de 2025): https://larepublica.pe/sociedad/2025/05/22/estudiante-fallece-dentro-del-campus-de-la-upn-en-trujillo-evacuan-a-todos-los-alumnos-de-la-sede-2130986
- Andina, admisión 2025-I de San Marcos: https://andina.pe/agencia/noticia-san-marcos-claves-del-examen-admision-2025i-horarios-vacantes-postulantes-1002730.aspx
- Andina, admisión 2025-II de San Marcos: https://andina.pe/agencia/noticia-san-marcos-todo-sobre-su-examen-admision-2025ii-cuantas-preguntas-tendra-1020376.aspx
- Canal N, caos y aglomeración en un examen de admisión de San Marcos: https://canaln.pe/amp/actualidad/universidad-san-marcos-se-registro-caos-y-aglomeracion-examen-admision-n438766
- RPP, San Marcos denuncia robo de equipos y agresiones durante una toma: https://rpp.pe/lima/actualidad/san-marcos-denuncia-robo-de-equipos-y-agresiones-a-su-personal-de-seguridad-durante-toma-de-universidad-noticia-1461528
- Correo, ola de robos en la Av. Amézaga: https://diariocorreo.pe/edicion/lima/estudiantes-de-san-marcos-en-la-mira-de-delincuentes-ola-de-robos-azota-av-amezaga-peru-unmsm-pnp-noticia/
- Panamericana, inseguridad en los exteriores de San Marcos (2023): https://panamericana.pe/buenosdiasperu/locales/394145-inseguridad-exteriores-universidad-san-marcos-estudiantes-denuncian-constantes-robos
- América TV, asalto a estudiantes en la puerta de una universidad en Los Olivos: https://www.americatv.com.pe/noticias/actualidad/olivos-delincuentes-asaltan-estudiantes-puerta-su-universidad-n473772

**Inversión en videovigilancia y capacidad de monitoreo**

- El Peruano, cámaras inteligentes para más de 40,000 estudiantes de San Marcos: https://elperuano.pe/noticia/298658-camaras-inteligentes-reforzaran-la-seguridad-de-mas-de-40000-estudiantes-en-san-marcos
- Caretas, la ATU instala cámaras en San Marcos: https://caretas.pe/?p=816891
- UPAO, control de seguridad electrónica: https://upao.edu.pe/noticia/UPAO-aplicara-control-de-seguridad-electronica/
- Caretas, Miraflores activa más de 500 cámaras con IA: https://caretas.pe/?p=781182
- Caretas, Surco lanza su central de monitoreo: https://caretas.pe/?p=761881
- Caretas, central de seguridad del Callao de S/ 245 millones: https://caretas.pe/nacional/callao-inauguran-central-de-seguridad-de-s-245-millones-con-1-100-camaras-drones-lectores-de-placas-y-tecnologia-con-ia/
- El Peruano, la PNP presenta su sistema de videovigilancia con IA: https://www.elperuano.pe/noticia/278593-pnp-presentan-moderno-sistema-de-videovigilancia-con-ia-para-lucha-contra-la-delincuencia
- Gestión, cerca del 30 % de las cámaras de videovigilancia están inoperativas: https://gestion.pe/peru/cerca-del-30-de-camaras-de-videovigilancia-a-nivel-nacional-se-encuentran-inoperativas-noticia/
- Expreso, la Contraloría identifica 1,533 cámaras inoperativas en 248 gobiernos locales: https://www.expreso.com.pe/actualidad/contraloria-identifica-1533-camaras-y-1000-equipos-de-comunicacion-inoperativos-en-248-gobiernos-locales-de-24-regiones-noticia/1202945/ (el titular dice 1,533; otro resumen dice 1,553 de 6,144: **verificar**)
- Canal N, la Contraloría encuentra 729 cámaras inoperativas en Lima y el Callao: https://canaln.pe/actualidad/contraloria-729-camaras-y-537-vehiculos-inoperativos-n482709
- CNN Chile, deficiencias en los sistemas de televigilancia municipales: https://www.cnnchile.com/pais/contraloria-detecto-deficiencias-sistemas-televigilancia-municipios-region-metropolitana-biobio/
- Stainer, Scott-Brown y Tatler (2013), *Looking for trouble*, Frontiers in Human Neuroscience (cita a Tickner y Poulton): https://pmc.ncbi.nlm.nih.gov/articles/PMC3786256
- Tickner y Poulton (1973), *Monitoring up to 16 synthetic television pictures showing a great deal of movement*, Ergonomics 16(4): https://scilit.com/publications/10dd4acae10a659124cea921feffad72
- Tickner y Poulton (1972), *Monitoring 16 television screens showing little movement*, Ergonomics 15(3): https://scilit.com/publications/1cc3bca4c97a8d14c1d66af0fb19b20a
- Ventas de Seguridad, *How many monitors do we need in a CCTV system?*: https://www.ventasdeseguridad.com/en/more-in-depth/other-approaches/21894-how-many-monitors-do-we-need-in-a-cctv-system-i.html

**SUNEDU**

- Condición Básica de Calidad VII, servicios educacionales complementarios: https://cdn.www.gob.pe/uploads/document/file/7178547/6153783-condicion-basica-de-calidad-vii-servicios-educacionales-complementarios-basicos.pdf
- Exitosa, la SUNEDU deniega la licencia a la Universidad Santo Domingo de Guzmán: https://www.exitosanoticias.pe/politica/sunedu-deniega-licencia-institucional-universidad-santo-domingo-guzman-n27947
- SUNEDU, proyecto de reglamento con nuevas reglas de calidad: https://www.gob.pe/institucion/sunedu/noticias/1303488-sunedu-presenta-proyecto-de-reglamento-con-nuevas-reglas-de-calidad-para-la-educacion-semipresencial-y-a-distancia

**Marco legal**

- La Cámara, el nuevo reglamento refuerza la protección de datos personales: https://lacamara.pe/nuevo-reglamento-refuerza-la-proteccion-de-datos-personales/
- IAPP, directiva de videovigilancia en el Perú: https://iapp.org/news/a/se-aprueba-y-publica-la-directiva-para-el-tratamiento-de-datos-personales-mediante-sistemas-de-videovigilancia-en-peru
- Minjus, guía para la transferencia internacional de datos personales: https://www.gob.pe/institucion/minjus/noticias/663844-peru-aprueba-guia-de-implementacion-para-la-transferencia-internacional-de-datos-personales-en-linea-con-estandares-internacionales
- LP Derecho, D.S. 007-2020-IN, reglamento del D.L. 1218: https://img.lpderecho.pe/wp-content/uploads/2020/04/Decreto-Dupremo-07-2020-IN-LP.pdf
- PCM, D.S. 115-2025-PCM, reglamento de la Ley 31814: https://www.gob.pe/institucion/pcm/normas-legales/7133522-115-2025-pcm
- Cuatrecasas, ¿qué establece el reglamento de la Ley de Inteligencia Artificial?: https://www.cuatrecasas.com/es/latam/tecnologia-medios-digitales/art/que-establece-el-reglamento-de-la-ley-de-inteligencia-artificial
- Osterling, alerta legal del 26 de enero de 2026: https://osterlingfirm.com/wp-content/uploads/2026/01/Alerta-Legal-26.01.26.pdf

**Costos**

- OpenAI, GPT-6 Luna: https://developers.openai.com/api/docs/models/gpt-6-luna
- OpenAI, *Introducing GPT-6.1 Terra*: https://openai.com/index/introducing-gpt-6-1-terra/
- OpenAI, GPT-5.6 Terra: https://developers.openai.com/api/docs/models/gpt-5.6-terra
- OpenAI, precios: https://developers.openai.com/api/docs/pricing
- Puter, precios de la API de OpenAI a noviembre de 2026 (fuente de terceros para GPT-6 Astra): https://developer.puter.com/tutorials/openai-api-pricing/
- OpenAI, guía de imágenes y visión: https://developers.openai.com/api/docs/guides/images-vision
- OpenAI, calculadora de tokens de imagen: https://developers.openai.com/api/docs/guides/image-cost-calculator
- OpenAI, modelos de razonamiento (`max_output_tokens` y estado `incomplete`): https://developers.openai.com/api/docs/guides/reasoning
- OpenAI, controles de datos (retención, entrenamiento y ZDR): https://developers.openai.com/api/docs/guides/your-data
- OpenAI, estado de la conversación (`store`): https://developers.openai.com/api/docs/guides/conversation-state
- Revista Economía, remuneración mínima vital de S/ 1,230 desde octubre de 2026: https://www.revistaeconomia.com/sueldo-minimo-1230-octubre-2026/
- Computrabajo, operador CCTV a S/ 2,500 en Surco: https://pe.computrabajo.com/ofertas-de-trabajo/oferta-de-trabajo-de-operador-cctv-sueldo-s-2500-12-horas-rotativos-6x1santiago-de-surco-en-santiago-de-surco-F4C9A3488F73D00F61373E686DCF3405
- Indeed Perú, empleos de CCTV: https://pe.indeed.com/q-cctv-empleos.html
- TuCambista, tipo de cambio del 3 de noviembre de 2026: https://tucambista.pe/noticias/dolares-a-soles-3-noviembre-2026
- Correo, la UIT de 2026 es S/ 5,500: https://diariocorreo.pe/economia/mef-fija-la-uit-en-s-5500-para-el-2026-desde-el-1-de-enero-noticia/
- Milestone, precios de BriefCam (solo por integradores): https://www.milestonesys.com/pricing/briefcam/

**Utilidad de los modelos de visión**

- CAVE, benchmark de descripción de anomalías (EMNLP 2025): https://aclanthology.org/anthology-files/pdf/emnlp/2025.emnlp-main.1379.pdf
- *Are Multimodal LLMs Ready for Surveillance?* (2026): https://arxiv.org/pdf/2603.04727.pdf
- Evaluación sin entrenamiento previo de modelos de visión y lenguaje en video de vigilancia: https://www.emergentmind.com/papers/2510.23190
- Calipsa, caso Prosegur USA (material comercial): https://www.calipsa.io/hubfs/Downloads/Case%20Studies/Prosegur%20USA_Case%20Study_2020_Final.pdf
- CHOP, video para entender la fatiga por alarmas: https://research.chop.edu/cornerstone-blog/researchers-honored-using-video-better-understand-alarm-fatigue

**Documentos internos del proyecto**

- `docs/propuesta-safecampus-v2.md`, `docs/pitch-y-negocio.md`, `docs/plan-mejora-rubrica.md`, `docs/resultados-pruebas-2026-11-05.md`, `mvp/ia.py`, `mvp/detector.py` y `mvp/notificador.py`.
