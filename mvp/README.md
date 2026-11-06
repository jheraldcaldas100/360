# Tres60 SafeCampus: MVP para el hackatón

Demostración en vivo con la cámara de un celular. YOLO detecta personas y objetos, y unas **reglas simples con parámetros objetivos** deciden cuándo generar una alerta. El operador la confirma o la descarta en el dashboard.

| Situación | Criterio (parámetros en `config.yaml`) | Demo | Hipótesis real (`config_real.yaml`) |
|---|---|---|---|
| 👥 Aglomeración | Hay al menos `personas_min` personas durante `segundos` | 3 personas, 5 s | 15 personas, 60 s |
| 🎒 Objeto desatendido | Mochila, bolso o maleta **sin nadie en su lugar** (su caja agrandada) durante `segundos`. El conteo empieza cuando no hay nadie, y se reinicia si alguien se queda junto al objeto 3 s o si el objeto se mueve | 20 s | 600 s (10 min) |
| 🚑 Persona en el suelo | Persona horizontal (caja `proporcion` veces más ancha que alta) durante `segundos` | 5 s | 30 s |
| ⛔ Zona restringida (opcional) | Los pies de una persona dentro de un rectángulo durante `segundos` | Desactivada | — |

## 1. Instalar (una sola vez)

Necesitan Python 3.10 o superior. Funciona sin GPU, solo más lento.

```bash
cd mvp
```
```bash
python -m venv .venv
```
```bash
source .venv/bin/activate
```
En Windows, el último comando es `.venv\Scripts\activate`.
```bash
pip install -r requirements.txt
```

## 2. Conectar la cámara del celular

El celular y la laptop deben estar **en la misma red wifi**. En wifi de la universidad a veces se bloquea la conexión entre equipos; si pasa, usen el **hotspot del celular**.

| Opción | Pasos | Valor de `fuente` en `config.yaml` |
|---|---|---|
| **Android con IP Webcam** (la más fácil) | Instalar la app *IP Webcam*, abrir **Iniciar servidor** y anotar la IP que muestra | `"http://192.168.X.X:8080/video"` |
| **Android o iPhone con DroidCam o Iriun Webcam** | Instalar la app en el celular y el cliente en la laptop; el celular aparece como una webcam más | `1` (si no funciona, probar `2`) |
| **iPhone con Mac** (Continuity Camera) | El iPhone aparece como cámara de la Mac | `1` |
| **Webcam de la laptop** (respaldo) | — | `0` |

También pueden pasar la fuente sin editar el archivo: `python detector.py --fuente http://192.168.1.20:8080/video`.

## 3. Ejecutar

### Lo más fácil: dos comandos

Primero el chequeo previo, que revisa librerías, cámara, velocidad del modelo, Telegram, IA y disco, y dice qué falta:

```bash
python verificar.py
```

Después, el detector y el dashboard juntos (se abre el navegador; Ctrl+C detiene todo):

```bash
python iniciar_demo.py --limpiar
```

`--limpiar` borra las alertas de los ensayos. Para el plan B con un video grabado: `python iniciar_demo.py --fuente videos/respaldo.mp4`.

### O por separado

Terminal 1, el detector (abre una ventana con el video analizado; `q` para salir):

```bash
python detector.py
```

Terminal 2, el dashboard (se abre en el navegador, en http://localhost:8501):

```bash
streamlit run dashboard.py
```

La primera vez se descarga el modelo `yolo11n.pt` (unos 6 MB). Las alertas se guardan en `data/alertas.db` y las fotos de evidencia en `data/evidencias/`. Para empezar de cero, borren la carpeta `data/`.

### El dashboard

| Pestaña | Qué tiene |
|---|---|
| 📹 **Monitoreo** | Video en vivo, **mapa del campus** (cada cámara se pone roja con sus alertas pendientes) y alertas con **prioridad por color** (alta: persona en el suelo y zona restringida; media: objeto y aglomeración), **sonido** y aviso emergente. Flujo del guardia: **Confirmar o Descartar → Marcar atendida**. Cada alerta muestra cuánto tardó en generarse, en procesarse, en revisarse y en atenderse, y quién lo hizo |
| 📊 **Estadísticas** | Tasa de confirmación, tiempo de respuesta, tiempo de procesamiento, tabla por tipo, gráficos por tipo y por hora, historial y descarga en CSV |
| ⚙️ **Configuración** | **Deslizadores** para cambiar personas, segundos, confianza y la zona restringida. Se aplican **en vivo** en un segundo, sin reiniciar el detector. Ideal para mostrarle al jurado que los criterios son objetivos y configurables |

## 3b. Alertas al celular por Telegram (10 minutos)

1. En Telegram, abran **@BotFather**, escriban `/newbot`, elijan un nombre y copien el **token** que les da.
2. Creen un grupo, por ejemplo "Seguridad SafeCampus", y agreguen al bot. Escriban cualquier mensaje en el grupo.
3. Abran en el navegador `https://api.telegram.org/bot<TOKEN>/getUpdates` y copien el número de `"chat":{"id": ...}`. En los grupos es negativo, por ejemplo `-1001234567890`.
4. Definan las variables antes de correr el detector. En Linux o Mac:
   ```bash
   export TELEGRAM_TOKEN="123456:ABC..."
   ```
   ```bash
   export TELEGRAM_CHAT_ID="-1001234567890"
   ```
   En Windows (PowerShell): `$env:TELEGRAM_TOKEN="..."` y `$env:TELEGRAM_CHAT_ID="..."`.
5. Prueben la conexión: `python notificador.py` debe enviar un mensaje al grupo.

Cada alerta llega con **foto y botones** (✅ Confirmar / ❌ Descartar y luego 🚓 Marcar atendida). Lo que se toca en Telegram se ve en el dashboard, y al revés. Solo el chat configurado puede cambiar alertas. **No suban el token al repositorio.**

## 3b-bis. Mapa del campus

Por defecto se muestra un plano de ejemplo. Para usar el de su universidad, guarden una captura de Google Maps o un croquis como `mapa.png` en la carpeta `mvp/` y ubiquen cada cámara en `config.yaml`. La posición va en proporciones del plano: `[0.5, 0.5]` es el centro.

```yaml
mapa:
  imagen: "mapa.png"
  camaras:
    "Celular demo": [0.40, 0.62]
```

El nombre de la cámara debe ser igual a `nombre_camara`.

## 3b-ter. Descripción de la alerta con IA (opcional)

Un modelo de visión de OpenAI (GPT) mira la foto de cada alerta y responde en una frase qué se observa y si la imagen respalda la alerta, por ejemplo "Coincide: sí". La descripción aparece en el dashboard y en Telegram. Cómo se usa de forma responsable:

- La IA **no decide ni retrasa** la alerta: llega unos segundos después, como contexto.
- **Antes de enviar la foto se difuminan las caras** (la zona de la cabeza de cada persona detectada).
- Se le pide no identificar a nadie ni describir rasgos físicos.

Para activarla se necesita una clave de API con saldo en https://platform.openai.com/api-keys. **ChatGPT Plus no incluye la API.**

```bash
export OPENAI_API_KEY="sk-..."
```

En `config.yaml`, pongan `ia.activa: true` y en `ia.modelo` un modelo con visión de https://platform.openai.com/docs/models. Si no hay internet o falla, la demo sigue funcionando sin la descripción.

## 3c. Medir resultados con videos (para el pitch)

1. Graben clips cortos de cada situación con el celular, en el lugar de la demo. Por ejemplo, 5 de aglomeración, 5 de mochila, 5 de persona en el suelo y 5 normales, sin situaciones.
2. Anoten en un CSV en qué segundo empieza y termina cada situación:
   ```
   video,tipo,inicio_s,fin_s
   clips/aglo1.mp4,aglomeracion,3,15
   clips/mochila1.mp4,objeto_desatendido,5,40
   clips/caida1.mp4,persona_en_suelo,4,12
   clips/normal1.mp4,,,
   ```
   En `objeto_desatendido`, el inicio es cuando la persona se aleja de la mochila.
3. Corran la evaluación:
   ```bash
   python evaluar.py clips/etiquetas.csv
   ```
   Se genera `data/evaluacion/resumen.md`, con una tabla de detectados, omitidos, sensibilidad, falsas alarmas y tiempo hasta la alerta lista para las diapositivas, y `detalle.csv`, con cada situación y cada alerta.

## 3d. Experimento "¿quién lo ve primero?"

Simula una sala de monitoreo para comparar a personas con el sistema.

1. Creen el mosaico. El **primer video** es el que tiene la situación; los demás son videos normales:
   ```bash
   python experimento.py crear --videos clips/mochila1.mp4 clips/normal1.mp4 clips/normal2.mp4 clips/normal3.mp4 --duracion 90 --posicion-evento 3
   ```
2. Midan a cada participante, sin decirle qué va a pasar ni en qué cámara. En `--evento` va el segundo en que empieza la situación en el video del evento:
   ```bash
   python experimento.py medir --evento 5 --participante "Ana"
   ```
   El participante presiona ESPACIO cuando nota algo raro.
3. Calculen el resumen y compárenlo con el sistema. El tiempo del sistema sale de `evaluar.py` para ese mismo video:
   ```bash
   python experimento.py resumen --sistema 25
   ```

Con 10 participantes ya tienen un resultado fuerte para el pitch, del tipo "4 de 10 personas no notaron la mochila; SafeCampus alertó siempre".

Otros usos:

```bash
python detector.py --config config_real.yaml
```
```bash
python detector.py --fuente videos/prueba.mp4
```

Con un archivo de video se usa el tiempo del video, así que el resultado es igual en cada ejecución. Sirve para grabar la demo antes y tener un respaldo.

## 4. Guion sugerido para la demo en vivo (unos 3 minutos)

1. **Presentación (20 s):** el celular apunta a un espacio abierto y el dashboard está proyectado. "El sistema no reemplaza al personal: le avisa y él decide".
2. **Aglomeración (30 s):** entran 3 o más personas al cuadro y se quedan 5 s. El contador sube y aparece la alerta.
3. **Objeto desatendido (45 s):** alguien deja una mochila en una silla o en el piso y se aleja. Se ve el contador `00:05/00:20`. *Variante:* vuelve antes de los 20 s, se queda junto a la mochila y el conteo se reinicia. "En la hipótesis real son 10 minutos".
4. **Persona en el suelo (30 s):** un voluntario se acuesta **sobre una colchoneta** durante 5 s y aparece la alerta.
5. **Verificación humana (30 s):** en el dashboard se confirma una alerta y se descarta otra. "Cada decisión queda registrada".
6. **Cierre (20 s):** parámetros objetivos y configurables, privacidad (sin reconocimiento facial) y próximos pasos.

## 5. Consejos para que la demo salga bien

- **Ubicación del celular:** a 1.5 o 2 m de altura, fijo con un trípode o pegado a la pared, mirando en diagonal un área de 3 a 5 m. Las personas deben verse **de cuerpo entero.**
- **Buena luz**, sin contraluz (no apuntar a una ventana).
- **Para el objeto, una mochila grande y visible.** Ensayen antes que el modelo la detecte; si no, bajen `confianza` a 0.3.
- **Persona en el suelo:** que se acueste **de lado respecto a la cámara**, no apuntando hacia ella, para que la caja quede horizontal.
- **Si va lento** (menos de 3 fps en la esquina del video), bajen `tamano_imagen` a 480 o 320.
- **Si no detecta a la persona acostada o la mochila**, cambien `modelo: yolo11n.pt` por `modelo: yolo11s.pt` en `config.yaml`. Es más preciso, pero más lento. En nuestras pruebas detectó personas acostadas que el modelo nano no detectaba.
- **Plan B:** graben un video de cada situación el día anterior y córranlo con `--fuente`, por si fallan el wifi o el celular.

## 6. Limitaciones conocidas (para decirlas con honestidad)

- Es un **prototipo de demostración**, no está validado para operación real.
- Solo detecta mochilas, bolsos y maletas, no "cualquier objeto".
- El criterio de persona en el suelo es simple (caja horizontal). Un modelo de pose lo haría más robusto.
- Una persona sentada o agachada mucho tiempo, o un objeto que se parezca a una mochila, pueden generar falsas alarmas. Para eso está el botón **Descartar.**

## 7. Estructura

| Archivo | Qué hace |
|---|---|
| `reglas.py` | Las reglas y sus parámetros, ajustables en vivo (sin dependencia de la cámara) |
| `analizador.py` | YOLO más reglas; lo comparten la demo y la evaluación |
| `detector.py` | Cámara → análisis → alertas, foto de evidencia, Telegram, video en vivo y ajustes en vivo |
| `almacen.py` | Registro de alertas en SQLite, con el flujo nueva → confirmada o descartada → atendida, y los tiempos |
| `notificador.py` | Alertas por Telegram con botones |
| `dashboard.py` | Dashboard del operador (Streamlit) |
| `evaluar.py` | Evaluación con videos etiquetados |
| `experimento.py` | Experimento "¿quién lo ve primero?" |
| `ia.py` | Descripción opcional de la alerta con GPT (difumina las caras antes) |
| `mapa.py` | Mapa del campus con las cámaras y sus alertas pendientes |
| `verificar.py` | Chequeo previo a la demo |
| `iniciar_demo.py` | Arranca el detector y el dashboard juntos |
| `revisar_alertas.py` | Muestra las últimas alertas y sus tiempos en la terminal |
| `PRUEBAS.md` | Guía de pruebas paso a paso (también la usa Claude Code con `/probar-safecampus`) |
| `config.yaml` / `config_real.yaml` | Parámetros de la demo y de la hipótesis real |
| `tests/` | Pruebas de las reglas, el registro, Telegram e IA (simulados), el mapa, la evaluación y el experimento: `python -m pytest tests` |

Licencia del modelo: Ultralytics YOLO es AGPL-3.0. Para un hackatón no es un problema, pero hay que revisarlo si después se quiere comercializar (ver `docs/propuesta-safecampus-v2.md`, sección 8).
