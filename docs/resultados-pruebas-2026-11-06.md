# Resultados de pruebas: 2026-11-06

Fase 0 de `DESARROLLO-PENDIENTE.md`: instalación en la laptop nueva, cámara y medición de fps.

## Equipo

- Windows 11, proyecto en `C:\dev\360`, fuera de OneDrive
- Python 3.12.10 (la guía recomienda 3.13)
- PyTorch 2.15.0 solo CPU, ultralytics 8.4.203, OpenCV 5.0.0, Streamlit 1.67.0
- GPU NVIDIA GeForce GTX 1050 de 4 GB, driver 512.78 (CUDA 11.6): presente, pero **no usada**
- Cámara: iPhone por Iriun, número `1`, por el hotspot del iPhone

## Resultados de la fase 0

| Prueba | Resultado | Notas |
|---|---|---|
| Pruebas automáticas | Aprobado | 34 passed |
| Cámara con imagen real | Aprobado | Cámara 1, 1280x720, unos 30 fps, brillo de 101 a 129 |
| `verificar.py --fuente 1` | Aprobado | Muestra 640x480 porque aún no usa `resolucion` (tarea D2). Modelo: unos 9.7 fps en su prueba de velocidad |
| Laptop nueva: fps con el dashboard cerrado | Aprobado: mediana 7.4 | 10 lecturas en 30 s |
| Laptop nueva: fps con el dashboard abierto | Aprobado: mediana 7.2 | 10 lecturas en 30 s; mínimo pedido: 3 fps |
| GPU usada | No | Con estos fps no hizo falta instalarla |

## Lecturas de fps

Laptop enchufada, `tamano_imagen: 640`, CPU. Una lectura cada 3 s del valor impreso en `data/en_vivo.jpg`.

| Dashboard | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | Mediana | Promedio |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Abierto | 2.9 | 4.8 | 6.6 | 6.7 | 7.5 | 7.0 | 8.0 | 7.9 | 8.4 | 8.7 | 7.2 | 6.9 |
| Cerrado | 5.4 | 5.7 | 6.8 | 7.6 | 7.7 | 7.5 | 7.9 | 6.2 | 7.5 | 7.2 | 7.4 | 7.0 |

Límites de esta medición:

- Son muestras cortas y la escena no fue la misma: el celular se movía en al menos parte de las lecturas. Sirven para comprobar el mínimo, no para concluir cuánto pesa el dashboard.
- Con el dashboard abierto había 2 conexiones a Streamlit; no se confirmó si era una sola pestaña.
- La lectura 1 con el dashboard cerrado se ve con poco contraste y puede estar mal leída.
- No se comprobó el modo de energía: Windows muestra el plan "Equilibrado", pero el modo de Ajustes no siempre lo cambia.
- La laptop estuvo enchufada en las dos series de la tabla. La primera lectura de la sesión (7.3 fps, a batería) no se cuenta.

## Medición descartada

Una primera serie con el dashboard cerrado dio de 4.0 a 11.6 fps, pero **no vale**: la imagen era totalmente negra (brillo 0.3 de 255, `Personas: 0 / 3`), así que no había personas que procesar. La causa no se confirmó. La imagen volvió después de atender el iPhone.

El detector siguió analizando el negro sin ningún aviso, que es el problema que corrige la tarea D1. `verificar.py` tampoco lo detectaría de forma fiable (tarea D2).

## Alertas de la sesión

- #1 `objeto_desatendido`, 20 s sin persona cerca: en estado "nueva". **No se revisó** su foto, así que no se sabe si es correcta. No se cuenta como prueba.
- `persona_en_suelo`: una alerta en estado "nueva", tras verse a una persona acostada en el cuadro durante la medición. No se cuenta como prueba P4, que se hace en la fase 3.

## Pendientes

- Fase A: comprobar que la demo de la laptop vieja esté detenida antes de usar el mismo bot de Telegram.
- `mvp/.gitignore` no cubre `.venv/`: `git add .` lo subiría.
- Streamlit publica el dashboard en toda la red, sin contraseña (tarea D5).
- Telegram (T1 a T7) e IA (I1 a I5): sin probar, son la fase 1.
