---
name: probar-safecampus
description: Guía interactiva para probar Tres60 SafeCampus con la cámara del celular, siguiendo mvp/PRUEBAS.md fase por fase y anotando los resultados.
user-invocable: true
argument-hint: "[fase o prueba, por ejemplo: fase 3, P2, telegram]"
---

# Probar Tres60 SafeCampus

Acompaña al equipo a probar el sistema siguiendo `mvp/PRUEBAS.md`. Habla en español, con frases cortas.

`$ARGUMENTS` puede indicar desde dónde empezar (por ejemplo, "fase 4", "P2" o "telegram"). Si está vacío, empieza por la fase 0.

## Cómo trabajar

1. Lee `mvp/PRUEBAS.md` y `CLAUDE.md` completos antes de empezar.
2. Detecta el sistema operativo y usa el intérprete del entorno virtual por su ruta: `mvp/.venv/bin/python` (Mac o Linux) o `mvp\.venv\Scripts\python.exe` (Windows). Ejecuta todo dentro de `mvp/`.
3. Avanza **una fase a la vez**. En cada fase:
   - Ejecuta tú los comandos.
   - Cuando se necesite una acción física (conectar el celular, actuar frente a la cámara, tocar un botón), pídela con instrucciones concretas, di qué deberían ver y **espera la confirmación** antes de seguir.
   - Al terminar la fase, di si quedó aprobada según el criterio de la guía y pasa a la siguiente.
4. `iniciar_demo.py` es un proceso largo: ejecútalo **en segundo plano** y nunca esperes a que termine.
5. Para comprobar el encuadre, abre `mvp/data/en_vivo.jpg` y describe lo que ves: si las personas están de cuerpo entero, si tienen recuadro y cuántos fps marca.
6. Después de cada prueba de la fase 5, ejecuta `python revisar_alertas.py -n 3`, abre la foto de evidencia de la alerta nueva y comprueba que corresponde a lo que se actuó. Mide el tiempo hasta la alerta con el campo "alerta X s tras el inicio".
7. Si una prueba falla, aplica la columna "Si falla" cambiando **un parámetro a la vez**, de preferencia en `mvp/data/ajustes.yaml` (se aplica en vivo), y repite la prueba.
8. Lleva la cuenta de intentos, alertas correctas y falsas alarmas. Al final (o cuando el equipo lo pida), crea `docs/resultados-pruebas-AAAA-MM-DD.md` con la plantilla de la guía, usando solo lo observado.

## Límites

- Nunca pidas tokens ni claves en el chat. Si hace falta Telegram, explica la fase 7: definir las variables en la terminal y reabrir Claude.
- No cambies el código sin preguntar. Si es necesario, corre `python -m pytest tests` antes y después.
- No hagas commits ni push salvo que el equipo lo pida, y nunca incluyas `mvp/data/`, videos, fotos ni tokens.
