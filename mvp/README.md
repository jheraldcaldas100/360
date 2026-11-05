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

Terminal 1, el detector (abre una ventana con el video analizado; `q` para salir):

```bash
python detector.py
```

Terminal 2, el dashboard (se abre en el navegador, en http://localhost:8501):

```bash
streamlit run dashboard.py
```

La primera vez se descarga el modelo `yolo11n.pt` (unos 6 MB). Las alertas se guardan en `data/alertas.db` y las fotos de evidencia en `data/evidencias/`. Para empezar de cero, borren la carpeta `data/`.

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
| `reglas.py` | Las reglas y sus parámetros (sin dependencia de la cámara) |
| `detector.py` | Cámara → YOLO → reglas → alertas, foto de evidencia y video en vivo |
| `almacen.py` | Registro de alertas en SQLite |
| `dashboard.py` | Dashboard del operador (Streamlit) |
| `config.yaml` / `config_real.yaml` | Parámetros de la demo y de la hipótesis real |
| `tests/test_reglas.py` | Pruebas de las reglas con detecciones simuladas: `python -m pytest tests` |

Licencia del modelo: Ultralytics YOLO es AGPL-3.0. Para un hackatón no es un problema, pero hay que revisarlo si después se quiere comercializar (ver `docs/propuesta-safecampus-v2.md`, sección 8).
