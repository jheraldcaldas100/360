# Guía de pruebas de Tres60 SafeCampus

Esta guía sirve para probar el MVP con la cámara de un celular, paso a paso, en el lugar donde se hará la demo. La pueden seguir personas o Claude Code en su computadora: con el comando `/probar-safecampus`, Claude la recorre con ustedes, ejecuta los comandos, revisa la imagen de la cámara y las alertas, y anota los resultados.

**Reparto de tareas:**

- **Claude:** instala, ejecuta comandos, revisa `data/en_vivo.jpg` (lo que ve la cámara) y las fotos de evidencia, consulta las alertas con `revisar_alertas.py`, ajusta parámetros y anota los resultados.
- **Las personas:** conectan el celular, actúan frente a la cámara (entrar, dejar la mochila, acostarse), tocan botones en el dashboard o en Telegram y cuentan lo que ven.

**Qué necesitan:** laptop con Python 3.10 a 3.13, celular en la misma red wifi (o el hotspot del celular), una mochila grande, una colchoneta, 2 o 3 personas y unos 60 a 90 minutos.

---

## Fase 0. Preparar

1. Tener la rama del proyecto actualizada:
   ```bash
   git checkout claude/festive-archimedes-gfntny
   ```
   ```bash
   git pull
   ```
2. Todos los comandos se ejecutan **dentro de la carpeta `mvp/`**.
3. Si van a usar Telegram, definan las variables **en la terminal antes de abrir Claude**, para que la herede (ver fase 7). Nunca peguen el token en el chat ni lo guarden en archivos del repositorio.

## Fase 1. Instalación y pruebas automáticas

```bash
python -m venv .venv
```

- Mac o Linux: el intérprete queda en `.venv/bin/python`.
- Windows: queda en `.venv\Scripts\python.exe`.

Para no depender de "activar" el entorno, usen siempre esa ruta. En esta guía, `python` significa ese intérprete.

```bash
python -m pip install -r requirements.txt
```

Tarda de 5 a 15 minutos la primera vez (descarga PyTorch).

```bash
python -m pytest tests
```

**Aprobado:** termina con `34 passed`. Si falla, la instalación quedó incompleta: repetir el `pip install`.

## Fase 2. Prueba rápida sin celular

Sirve para separar problemas de instalación de problemas de red. Usa la webcam de la laptop (`0`):

```bash
python verificar.py --fuente 0
```

**Aprobado:** marca en verde las librerías, la cámara, el modelo (con sus fps) y el disco. Telegram e IA pueden quedar en aviso: son opcionales. La primera vez descarga el modelo `yolo11n.pt` (unos 6 MB). Si los fps del modelo son menos de 5, anótenlo: habrá que bajar `tamano_imagen` (fase 4).

## Fase 3. Conectar el celular

| Opción | Pasos | Valor de `fuente` |
|---|---|---|
| Android con IP Webcam (la más fácil) | Instalar la app IP Webcam y tocar "Iniciar servidor"; anotar la IP que muestra | `http://192.168.X.X:8080/video` |
| Android o iPhone con DroidCam o Iriun | App en el celular y cliente en la laptop | `1` (o `2`) |
| iPhone con Mac (Continuity Camera) | El iPhone aparece como cámara de la Mac | `1` |

1. Con IP Webcam, abrir primero `http://192.168.X.X:8080` en el navegador de la laptop. Si ahí no se ve el video, el problema es la red: usar el hotspot del celular.
2. Ejecutar el chequeo con esa fuente:
   ```bash
   python verificar.py --fuente http://192.168.X.X:8080/video
   ```
3. **Aprobado:** la cámara sale en verde con su resolución y fps.
4. Guardar ese valor en `fuente:` dentro de `config.yaml`, para no repetirlo.

## Fase 4. Iniciar la demo y encuadrar

```bash
python iniciar_demo.py --limpiar
```

- Abre la ventana del video y el dashboard en `http://localhost:8501`. Es un proceso que sigue corriendo: **Claude debe ejecutarlo en segundo plano** y no esperar a que termine.
- `--limpiar` borra las alertas de pruebas anteriores. Úsenlo solo al empezar una sesión nueva.
- Para detener todo: Ctrl+C en esa terminal (o detener la tarea en segundo plano).

**Encuadre.** Coloquen el celular fijo, a 1.5 o 2 m de altura, mirando en diagonal un área de 3 a 5 m. Claude puede abrir `data/en_vivo.jpg` (se actualiza cada 0.3 s) para ver lo que ve la cámara y comprobar que:

- las personas se ven **de cuerpo entero** y con recuadro verde,
- hay buena luz, sin contraluz,
- el contador de fps (esquina superior derecha) marca 3 o más.

Si va lento, bajen `tamano_imagen` a 480 o 320 (ver "Ajustar parámetros").

## Fase 5. Pruebas por situación

Para cada prueba: preparar, actuar, verificar y anotar. Para verificar, Claude ejecuta:

```bash
python revisar_alertas.py -n 3
```

Muestra las últimas alertas con su hora, sus tiempos y la ruta de la foto de evidencia. Claude puede abrir esa foto para confirmar que corresponde a la situación.

### P1. Aglomeración (umbral de la demo: 3 personas, 5 s)

| | |
|---|---|
| **Actuar** | Entran 3 personas al cuadro y se quedan quietas 10 s. Después, solo 2 personas durante 30 s |
| **Esperado** | Arriba a la izquierda aparece `Personas: 3 / 3 (x/5 s)`; a los 5 s, alerta de aglomeración con sonido |
| **Aprobado** | 1 alerta entre 5 y 8 s después de que están las 3. Ninguna alerta con 2 personas |
| **Si falla** | Cuenta menos personas: alejarse para verse de cuerpo entero, más luz o `confianza: 0.3` |

### P2. Objeto desatendido (umbral de la demo: 20 s)

| | |
|---|---|
| **Actuar** | a) Una persona se sienta junto a la mochila 40 s. b) Deja la mochila a la vista y se aleja a más de 2 m o sale del cuadro |
| **Esperado** | Recuadro sobre la mochila: `Objeto #N acompañado` en (a); `Objeto #N solo 00:05/00:20` en (b) |
| **Aprobado** | (a) sin alerta. (b) 1 alerta entre 20 y 25 s después de alejarse |
| **Si falla** | Sin recuadro en la mochila: no la detecta; probar otra mochila más grande, `confianza: 0.3` o el modelo `yolo11s.pt`. El contador no arranca: alejarse más o bajar `margen` a 0.6 |

### P3. Objeto: vuelve el dueño

| | |
|---|---|
| **Actuar** | Dejar la mochila, alejarse 10 s, volver y quedarse junto a ella 5 s, y alejarse otra vez |
| **Esperado** | Al volver cambia a `acompañado`; al alejarse, el contador empieza de nuevo desde `00:00` |
| **Aprobado** | No hay alerta antes de 20 s contados desde la **segunda** vez que se aleja |
| **Si falla** | Quedarse más cerca de la mochila, o subir `segundos_para_reiniciar` si alguien que solo pasa la reinicia |

### P4. Persona en el suelo (umbral de la demo: 5 s)

| | |
|---|---|
| **Actuar** | a) Alguien se agacha 3 s y se levanta. b) Se acuesta en la colchoneta **de lado respecto a la cámara** (el cuerpo paralelo al borde inferior de la imagen), sin tocar ese borde, y se queda 10 s |
| **Esperado** | En (b), `En el suelo x/5 s` sobre la persona |
| **Aprobado** | (a) sin alerta. (b) 1 alerta entre 5 y 8 s después de acostarse |
| **Si falla** | No detecta a la persona acostada: cambiar a `yolo11s.pt` (requiere reiniciar la demo). La detecta pero no cuenta el tiempo: `proporcion: 1.1` |

### P5. Zona restringida (opcional)

| | |
|---|---|
| **Actuar** | Activarla en el dashboard (Configuración → Zona restringida → Activa → Aplicar) y entrar al rectángulo rojo |
| **Aprobado** | Alerta a los 2 s de tener los pies dentro de la zona |

## Fase 6. Flujo del guardia (dashboard)

1. En una alerta nueva: **Confirmar** → debe pasar a "Confirmada, por atender".
2. **Marcar atendida** → pasa a "Atendida".
3. En otra alerta: **Descartar** → pasa a "Descartada".
4. Pestaña **Estadísticas** → muestra tasa de confirmación, tiempo de respuesta y procesamiento.
5. Claude confirma con `python revisar_alertas.py -n 5` que los estados y los tiempos quedaron guardados.

**Aprobado:** los cuatro puntos funcionan y los tiempos aparecen.

## Fase 7. Telegram

1. En Telegram, abrir **@BotFather**, escribir `/newbot` y copiar el token.
2. Crear un grupo, agregar al bot y escribir un mensaje.
3. En el navegador, abrir `https://api.telegram.org/bot<TOKEN>/getUpdates` y copiar el número de `"chat":{"id": ...}` (en grupos es negativo).
4. **Cerrar Claude**, definir las variables en esa terminal y volver a abrir Claude allí:
   - Mac o Linux: `export TELEGRAM_TOKEN="..."` y `export TELEGRAM_CHAT_ID="..."`
   - Windows (PowerShell): `$env:TELEGRAM_TOKEN="..."` y `$env:TELEGRAM_CHAT_ID="..."`
5. Probar el envío:
   ```bash
   python notificador.py
   ```
6. Reiniciar la demo (sin `--limpiar` si quieren conservar las alertas) y repetir P1.

**Aprobado:** el mensaje de prueba llega al grupo; la alerta llega con foto en menos de 5 s; tocar Confirmar en Telegram cambia el estado en el dashboard.

## Fase 8. Repeticiones y registro

Repetir P1, P2 (b) y P4 (b) **5 veces cada una** y contar cuántas veces salió la alerta y cuántas alertas sobraron (falsas). Al final, Claude ejecuta `python revisar_alertas.py --resumen` y anota los resultados en un archivo nuevo `docs/resultados-pruebas-AAAA-MM-DD.md` con la plantilla de abajo.

## Fase 9 (opcional). Clips para la evaluación

Grabar con la cámara del celular unos 20 clips cortos en el mismo lugar (5 por situación y 5 normales), guardarlos en `mvp/clips/` y seguir la sección 3c de `README.md` para correr `evaluar.py`. Los clips no se suben al repositorio si muestran personas que no dieron su consentimiento.

## Cierre

1. Detener la demo.
2. Guardar el archivo de resultados.
3. Si se hace un commit: incluir solo los resultados y cambios de configuración. **No** subir `data/`, videos, fotos ni tokens.

---

## Ajustar parámetros

**En vivo, sin reiniciar.** La forma más simple es el dashboard: pestaña Configuración → Aplicar cambios.

Claude también puede crear o editar `data/ajustes.yaml`; el detector lo lee en un segundo y lo combina con `config.yaml`. Basta con escribir lo que cambia, por ejemplo:

```yaml
confianza: 0.3
reglas:
  objeto_desatendido:
    margen: 0.6
  persona_en_suelo:
    proporcion: 1.1
```

**Con reinicio.** El modelo (`modelo: yolo11s.pt`), `tamano_imagen` y `fuente` se cambian en `config.yaml` y se aplican al reiniciar la demo. Los ajustes de `data/ajustes.yaml` se borran al reiniciar, así que si un valor funcionó, hay que pasarlo a `config.yaml`.

## Plantilla de resultados

```markdown
# Resultados de pruebas: AAAA-MM-DD

- Lugar: 
- Celular y app: 
- Laptop (sistema, GPU sí o no): 
- fps del detector: 
- Ajustes usados (si cambiaron): 

| Prueba | Intentos | Alertas correctas | Falsas alarmas | Tiempo hasta la alerta | Notas |
|---|---|---|---|---|---|
| P1 Aglomeración | 5 | | | | |
| P2 Objeto desatendido | 5 | | | | |
| P3 Vuelve el dueño | 1 | | | | |
| P4 Persona en el suelo | 5 | | | | |
| P5 Zona restringida | | | | | |
| Flujo del guardia | 1 | | | | |
| Telegram | 1 | | | | |

## Problemas encontrados y cómo se resolvieron

## Pendientes para la demo
```

## Problemas comunes

| Síntoma | Solución |
|---|---|
| "No se pudo abrir la cámara" | Misma red wifi, URL con `/video` al final, probarla antes en el navegador, o usar el hotspot |
| Va lento (menos de 3 fps) | `tamano_imagen` a 480 o 320 en `config.yaml` y cerrar otros programas |
| El video se ve atrasado | Normal si la red es lenta; acercar el celular al router o usar el hotspot |
| El dashboard dice "Esperando video" | El detector no está corriendo: revisar los mensajes de la demo |
| No suena la alerta | Hacer clic en la página: el navegador bloquea el audio hasta entonces |
| Windows no reconoce `python` | Usar `py`, o reinstalar Python marcando "Add to PATH" |
| En Mac no abre la cámara `1` | Dar permiso de cámara a la Terminal en Ajustes del Sistema → Privacidad → Cámara |
| "Port 8501 is already in use" | Hay otra demo abierta: detenerla o usar `--puerto 8502` |
| Telegram no llega | `python verificar.py` dice el motivo; revisar que el bot esté en el grupo y el chat id negativo |
