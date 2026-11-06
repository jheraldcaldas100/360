# Desarrollo pendiente de Tres60 SafeCampus

Plan de trabajo para terminar el MVP antes de la demo: configurar la laptop nueva, validar Telegram e IA, cerrar los problemas del primer ensayo (`docs/resultados-pruebas-2026-11-05.md`) y conseguir los números del pitch. Está escrito para que Claude Code lo ejecute tarea por tarea con el equipo.

## Cómo empezar en la laptop nueva

En una terminal (PowerShell en Windows), en una carpeta **fuera de OneDrive**, abran Claude Code y péguenle esto:

> Clona `https://github.com/jheraldcaldas100/360.git` en `C:\dev\360` con `git clone --branch claude/festive-archimedes-gfntny`. Después lee `CLAUDE.md` y `DESARROLLO-PENDIENTE.md` completos, y empecemos por la fase 0. Trabaja una tarea a la vez y espera mi confirmación entre tareas.

Notas:

- La rama `claude/festive-archimedes-gfntny` es la del proyecto. La rama predeterminada de GitHub casi no tiene contenido, así que **siempre hay que clonar con `--branch`**. Se puede corregir en GitHub: Settings → General → Default branch.
- Si el repositorio es privado, Git pedirá iniciar sesión en GitHub la primera vez (en Windows se abre el navegador).
- Si Telegram o la IA se van a usar, las variables `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID` y `OPENAI_API_KEY` se definen en esa terminal **antes** de abrir Claude (ver `mvp/CONFIGURAR-LAPTOP.md`).

## Reglas de trabajo para Claude

1. Una tarea a la vez, en el orden de este documento, salvo que el equipo diga otra cosa.
2. Antes de cambiar código: `python -m pytest tests` dentro de `mvp/`. Después del cambio, otra vez. **Todas deben pasar.** Cada tarea de código agrega sus propias pruebas.
3. Cambios pequeños: no reescribir lo que ya funciona ni cambiar valores de `config.yaml` sin que lo pidan.
4. Al terminar cada tarea: mostrar qué cambió, cómo se probó, y hacer **un commit por tarea** con un mensaje claro. **Push solo cuando el equipo lo confirme.**
5. Si una tarea necesita una prueba con la cámara, pedir la acción a las personas y esperar su confirmación. No inventar resultados.
6. Nunca pedir ni guardar tokens o claves; nunca subir `mvp/data/`, fotos, videos ni archivos `.pt`.
7. Al terminar una tarea, marcarla en la lista de estado al final de este documento.

---

## Fase 0. Configurar la laptop

Seguir `mvp/CONFIGURAR-LAPTOP.md`, fases A a C: instalación, GPU NVIDIA si la hay, cámara y medición de fps.

**Hecha cuando:** pasan todas las pruebas, la cámara da imagen real en `verificar.py` y están anotados los fps con el dashboard cerrado y abierto.

## Fase 1. Validar Telegram e IA

Seguir `mvp/CONFIGURAR-LAPTOP.md`, fases D (pruebas T1 a T7) y E (pruebas I1 a I5).

**Hecha cuando:** T1 a T7 aprobadas. La IA es opcional: si no hay clave de API con saldo, se marca "no disponible" y se presenta sin ella.

---

## Fase 2. Desarrollo

Las tareas están ordenadas por impacto en la demo. Las primeras tres corrigen problemas que se vieron en el primer ensayo.

### D1. Aviso de "SIN SEÑAL" cuando se corta la cámara

**Problema.** Si el iPhone se desconecta, Iriun entrega una pantalla negra ("Looking for the phone") como si fuera video. El detector sigue analizándola sin avisar. Si el stream se corta del todo, el último fotograma queda congelado en el dashboard.

**Qué hacer:**

1. Crear `mvp/senal.py` con una clase `MonitorSenal`, sin dependencia de la cámara para poder probarla:
   - `actualizar_fotograma(frame, ahora)`: calcula el brillo medio (escala de grises, reducida a 64x36) y guarda la hora del último fotograma.
   - `estado(ahora)`: devuelve `"ok"`, `"oscura"` (brillo menor a `brillo_min` durante al menos `segundos_oscuro`) o `"sin_imagen"` (ningún fotograma nuevo durante `segundos_sin_imagen`), más la hora desde la que está así.
   - Usar `Temporizador` de `reglas.py` para los tiempos.
2. Agregar a `config.yaml` y `config_real.yaml`:
   ```yaml
   senal:
     brillo_min: 25
     segundos_oscuro: 5
     segundos_sin_imagen: 3
   ```
3. En `detector.py`:
   - En el bucle en vivo, consultar el monitor también cuando no llega fotograma (hoy hace `continue`).
   - Si el estado no es `"ok"`: **no evaluar las reglas**, dibujar una franja roja con `SIN SEÑAL: imagen oscura` o `SIN SEÑAL: no llegan imágenes` sobre el último fotograma, y seguir publicando `en_vivo.jpg` cada 0.3 s.
   - Escribir `data/estado_camara.json` con `{"estado", "desde", "actualizado"}` cada vez que se publica `en_vivo.jpg`, usando `reemplazar()`.
   - Si Telegram está activo, enviar **un** mensaje al pasar a "sin señal" y otro al recuperarse (`enviar_texto`), no uno por fotograma.
4. En `dashboard.py`, arriba de la pestaña Monitoreo: `st.error` con el motivo si el estado no es `"ok"`, o si `actualizado` tiene más de 5 s (el detector dejó de correr).

**Pruebas automáticas** (`tests/test_senal.py`): imagen negra durante 6 s → `"oscura"`; imagen normal → `"ok"`; sin fotogramas durante 4 s → `"sin_imagen"`; vuelve la imagen → `"ok"`.

**Prueba con cámara:** con la demo corriendo, cerrar la app de Iriun en el iPhone. **Aprobado:** en menos de 6 s aparecen la franja en el video y el aviso en el dashboard; al reabrir Iriun desaparecen solos.

### D2. Chequeo previo que no se engañe con la pantalla negra

**Problema.** `verificar.py` mira la cámara solo 3 s y aprueba aunque vea la pantalla negra de Iriun. Además, no usa la `resolucion` de `config.yaml`.

**Qué hacer:**

1. Sacar de `CamaraEnVivo._abrir()` una función `abrir_captura(fuente, resolucion)` en `detector.py` y usarla en los dos lugares.
2. En `verificar.py`, `revisar_camara()`:
   - Abrir con `abrir_captura(fuente, cfg.get("resolucion"))`.
   - Leer hasta 15 s y aprobar solo cuando haya **3 s seguidos** con brillo mayor o igual a `senal.brillo_min`. Mientras tanto, imprimir "Esperando imagen real de la cámara...".
   - Si en 15 s no lo logra: falla con "La cámara solo entrega imagen negra: revisa que la app del celular esté abierta y desbloqueada".
   - Mostrar la resolución realmente entregada.

**Pruebas automáticas:** separar la decisión en una función pura, por ejemplo `aprobar_brillos(lista_de_(t, brillo), brillo_min)`, y probarla con negro, con negro seguido de imagen normal y con imagen normal desde el inicio.

**Prueba con cámara:** correr `verificar.py` con Iriun cerrado en el iPhone (debe fallar) y abierto (debe aprobar, con 1280x720).

### D3. Menos falsas alarmas de persona en el suelo

**Problema.** En el ensayo hubo 3 falsas y 1 dudosa, ninguna correcta. Dos casos: una persona sentada detrás de una mesa (solo se ve su parte de arriba y la caja queda ancha) y un torso muy cerca de la cámara.

**Qué hacer:**

1. **Filtro de bordes.** En `ReglaPersonaEnSuelo`, reemplazar `ignorar_borde_inferior` por `ignorar_bordes` (por defecto `true`): ignorar la caja si toca **cualquier** borde del cuadro, con un margen del 2 %. Seguir aceptando `ignorar_borde_inferior` en la configuración para no romper archivos viejos.
2. **Script de calibración** `mvp/calibrar_suelo.py`:
   - Uso: `python calibrar_suelo.py --acostadas <carpeta> --otras <carpeta>`.
   - Corre YOLO sobre cada imagen y, por cada persona, imprime la proporción ancho/alto y si toca un borde.
   - Al final, imprime la proporción mínima del grupo "acostadas", la máxima del grupo "otras" (sin contar las que tocan bordes) y un umbral sugerido: el punto medio. Si los grupos se solapan, lo dice.
3. **Calibrar con datos reales (con el equipo):**
   - "otras": las fotos de las alertas falsas #4, #6, #7 y #10 del ensayo, si se copiaron por USB, o fotos nuevas de gente sentada detrás de mesas y muy cerca de la cámara.
   - "acostadas": 5 fotos de una persona en la colchoneta, de lado respecto a la cámara, en el lugar de la demo.
   - Poner el umbral sugerido en `persona_en_suelo.proporcion` de `config.yaml` **solo si el equipo lo aprueba**.

**Pruebas automáticas:** caja que toca el borde izquierdo, el derecho o el superior → no cuenta; caja horizontal sin tocar bordes → cuenta; un archivo con `ignorar_borde_inferior` sigue cargando.

**Prueba con cámara:** repetir la P4 de `PRUEBAS.md`. **Aprobado:** (a) agacharse y levantarse no alerta; (b) acostarse alerta entre 5 y 8 s, en al menos 4 de 5 intentos; 0 falsas alarmas con gente sentada al fondo durante 2 minutos.

### D4. Medir el rendimiento sin adivinar

**Problema.** En el ensayo el detector fue a 0.5–1.4 fps y no se sabe por qué.

**Qué hacer:**

1. En `detector.py`, cada 10 s, imprimir `[Rendimiento] X fps | YOLO Y ms | ciclo Z ms`, con los promedios de esos 10 s. Medir el tiempo de `analizador.detectar()` aparte del ciclo completo.
2. Opcional, en `config.yaml`: `dispositivo: ""` (vacío = automático). Si tiene valor (`cpu`, `0` para la primera GPU NVIDIA o `mps` en Mac con chip Apple), pasarlo como `device=` a `modelo.predict()` en `analizador.py`.
3. En `dashboard.py`, aligerar el panel de alertas: mostrar como máximo 15 tarjetas y abrir solo la evidencia de la alerta nueva más reciente; las demás quedan cerradas.

**Pruebas automáticas:** que `Analizador` pase `device` solo cuando está configurado (con un modelo falso que registre los argumentos).

**Prueba con cámara:** anotar los fps con el dashboard cerrado y abierto, antes y después del cambio 3.

### D5. Arranque más claro y dashboard solo en la laptop

**Qué hacer en `iniciar_demo.py`:**

1. Cuando un proceso termina, decir cuál fue (detector o dashboard) y su código de salida.
2. Arrancar Streamlit con `--server.address 127.0.0.1`, para que nadie más en la red pueda abrir el dashboard (no tiene contraseña). Agregar la opción `--red` para quien quiera abrirlo desde otro equipo, con una advertencia.

**Prueba:** cerrar la ventana del video y ver que el mensaje dice "El detector terminó (código N)". Abrir el dashboard desde otro equipo de la red: no debe abrir sin `--red`.

### D6. Prueba automática de `reemplazar()`

**Qué hacer:** en `tests/`, una prueba que simule `os.replace` fallando con `PermissionError` 3 veces y luego funcionando (debe devolver `True`), y otra que falle siempre (debe devolver `False` sin lanzar error). Usar `monkeypatch`.

### D7. Ajustes menores

1. Agregar `resolucion: [1280, 720]` a `config_real.yaml`.
2. Si D1 a D6 agregan opciones nuevas a `config.yaml`, agregarlas también a `config_real.yaml` y al `README.md`.

---

## Fase 3. Prueba formal

Con D1 a D3 hechas, seguir `mvp/PRUEBAS.md`, fases 4 a 8, con el celular **fijo** y `personas_min: 3`:

- P1, P2 (b) y P4 (b), 5 veces cada una.
- P2 (a), P3 y la fase 6 completa (Confirmar, Marcar atendida, Descartar y Estadísticas).
- Telegram durante toda la prueba.

**Hecha cuando:** el archivo `docs/resultados-pruebas-AAAA-MM-DD.md` tiene intentos, alertas correctas, falsas alarmas y tiempos de cada prueba.

## Fase 4. Evidencia para el pitch

1. **Clips y evaluación:** grabar unos 20 clips en el lugar de la demo (5 por situación y 5 sin situaciones), con el consentimiento de quienes aparecen, y seguir la sección 3c de `mvp/README.md` para correr `evaluar.py`.
2. **Experimento "¿quién lo ve primero?":** sección 3d de `mvp/README.md`, con unas 10 personas.
3. **Video de respaldo** de la demo completa, para el plan B.
4. **Completar los datos entre corchetes** de `docs/pitch-y-negocio.md` con los resultados reales de las fases 3 y 4. No inventar cifras.

---

## Estado

| Tarea | Estado | Notas |
|---|---|---|
| Fase 0. Configurar la laptop | Hecha | 7.2 fps con el dashboard abierto y 7.4 cerrado, en CPU. Ver `docs/resultados-pruebas-2026-11-06.md` |
| Fase 1. Telegram (T1 a T7) | Pendiente | |
| Fase 1. IA (I1 a I5) | Pendiente | Opcional |
| D1. Aviso de "SIN SEÑAL" | Pendiente | |
| D2. Chequeo previo | Pendiente | |
| D3. Persona en el suelo | Pendiente | |
| D4. Rendimiento | Pendiente | |
| D5. Arranque y dashboard local | Pendiente | |
| D6. Prueba de `reemplazar()` | Pendiente | |
| D7. Ajustes menores | Pendiente | |
| Fase 3. Prueba formal | Pendiente | |
| Fase 4. Evidencia para el pitch | Pendiente | |
