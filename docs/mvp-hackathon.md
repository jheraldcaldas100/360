# Tres60 SafeCampus: alcance del MVP para el hackatón (3 días)

> Versión acotada para el hackatón interno. La propuesta completa (`propuesta-safecampus-v2.md`) queda como **hoja de ruta** para un piloto futuro; en este MVP **no** se aplican sus reglas estrictas ni su plan de validación formal.

## Objetivo de la demo

Demostrar en vivo, con la cámara de un celular, que la IA puede **analizar video en tiempo real y verificar, con parámetros objetivos y configurables, que se cumplen ciertos criterios**, y avisar al personal para que confirme o descarte. **No reemplaza al personal: lo ayuda a detectar antes.**

## Qué incluye

| Situación | Criterio simple | Parámetros | Valor en la demo | Hipótesis real |
|---|---|---|---|---|
| Aglomeración | Hay muchas personas a la vez durante cierto tiempo | Personas mínimas, segundos | 3 personas, 5 s | 15 personas, 60 s |
| Objeto desatendido | Mochila, bolso o maleta **sin nadie en su lugar**. El conteo empieza cuando no hay nadie y se alerta al superar el tiempo | Segundos, tamaño del "lugar", tiempo para reiniciar | 20 s | **10 min** |
| Persona en el suelo | Persona en posición horizontal durante cierto tiempo | Segundos, proporción ancho/alto | 5 s | 30 s |
| Zona restringida (opcional) | Persona dentro de un área marcada | Rectángulo, segundos | Desactivada | — |

Además incluye:

- **Video en vivo** desde el celular, con recuadros, contadores y tiempos visibles.
- **Alertas** con foto de evidencia, fecha, hora y cámara, guardadas en SQLite.
- **Dashboard** para confirmar o descartar cada alerta (validación humana).

## Qué queda fuera, a propósito

Varias cámaras, horarios y calendarios por zona, modelos de pose, VLM y LLM, notificaciones externas, roles de usuario, métricas formales y piloto con operadores. Todo eso está en la hoja de ruta (`propuesta-safecampus-v2.md`).

## Cómo funciona

```
Celular (cámara) ──wifi──► Laptop: YOLO detecta personas y mochilas
                                   │
                                   ▼
                     Reglas con parámetros (cantidad, tiempo, posición)
                                   │
                                   ▼
                     Alerta + foto ──► SQLite ──► Dashboard: confirmar / descartar
```

## Criterio de éxito de la demo

Cada una de las 3 situaciones, escenificada frente al celular, genera su alerta **en el tiempo configurado** y aparece en el dashboard con su foto. Una situación parecida, pero que **no** cumple el criterio (por ejemplo, el dueño vuelve por su mochila o alguien se agacha y se levanta), **no** genera alerta.

**Mini prueba recomendada (opcional, suma mucho en la presentación):** repetir cada situación 5 veces el día 3 y anotar cuántas veces se detectó y cuántas falsas alarmas hubo. Ejemplo: "detectó 5 de 5 aglomeraciones, 4 de 5 mochilas y hubo 1 falsa alarma en 10 minutos".

## Plan de 3 días

| Día | Tareas | Resultado al final del día |
|---|---|---|
| **1** | Instalar; conectar el celular (IP Webcam o DroidCam); correr el detector y el dashboard; ajustar la posición del celular y la `confianza` | Video en vivo con recuadros y la primera alerta de aglomeración |
| **2** | Ensayar mochila y persona en el suelo; ajustar `margen`, `proporcion` y tiempos; grabar videos de respaldo; preparar las diapositivas | Las 3 situaciones funcionan en el espacio real de la demo |
| **3** | Mini prueba de 5 repeticiones; ensayo completo del guion (ver `mvp/README.md`); plan B con video grabado | Demo ensayada y con números para mostrar |

## Mensajes clave para el jurado

1. **Apoyo, no reemplazo:** cada alerta la decide una persona.
2. **Parámetros objetivos y configurables:** cantidad de personas, tiempo y posición, no "intuición" del sistema.
3. **Privacidad:** detecta situaciones, no identifica personas; sin reconocimiento facial.
4. **Funciona con cámaras existentes:** hoy con un celular, mañana con las cámaras IP del campus.
5. **Hoja de ruta clara:** horarios por zona (por ejemplo, objetos en bibliotecas solo fuera de horario), más cámaras y validación con el personal de seguridad.
