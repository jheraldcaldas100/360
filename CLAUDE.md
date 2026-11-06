# Tres60 SafeCampus

Proyecto de hackatón (frente S2: Ciudades Inteligentes, Seguridad y GovTech). Es un MVP que analiza en vivo la cámara de un celular con YOLO y reglas simples, y genera alertas que el personal de seguridad confirma o descarta. **Apoya al personal, no lo reemplaza.** Se comunica en español con el equipo.

## Estructura

- `mvp/`: el sistema. Todos los comandos se ejecutan dentro de esta carpeta.
  - `reglas.py`: las cuatro reglas (aglomeración, objeto desatendido, persona en el suelo, zona restringida), sin dependencia de la cámara.
  - `analizador.py`: YOLO más reglas; lo usan la demo y la evaluación.
  - `detector.py`: cámara → análisis → alertas (SQLite y foto), Telegram, IA opcional, `data/en_vivo.jpg` y ajustes en vivo desde `data/ajustes.yaml`.
  - `dashboard.py`: Streamlit (monitoreo, mapa, estadísticas, configuración).
  - `almacen.py`, `notificador.py`, `ia.py`, `mapa.py`: registro, Telegram, descripción con GPT y mapa.
  - `verificar.py` (chequeo previo), `iniciar_demo.py` (arranca todo), `revisar_alertas.py` (alertas en la terminal).
  - `evaluar.py` (métricas con videos etiquetados) y `experimento.py` (mosaico "¿quién lo ve primero?").
  - `config.yaml` (valores de la demo) y `config_real.yaml` (hipótesis real).
  - `PRUEBAS.md`: **guía de pruebas paso a paso**. `README.md`: guía de uso.
- `docs/`: propuesta, alcance del MVP, plan según la rúbrica, pitch y negocio.

## Comandos

Usar el intérprete del entorno virtual por su ruta: `.venv/bin/python` (Mac o Linux) o `.venv\Scripts\python.exe` (Windows). Detectar el sistema antes de elegir.

| Para | Comando (dentro de `mvp/`) |
|---|---|
| Instalar | `python -m venv .venv` y luego `python -m pip install -r requirements.txt` |
| Pruebas automáticas | `python -m pytest tests` (deben pasar las 34) |
| Chequeo previo | `python verificar.py --fuente <fuente>` |
| Iniciar la demo | `python iniciar_demo.py --limpiar` (**proceso largo: ejecutarlo en segundo plano**) |
| Ver alertas | `python revisar_alertas.py -n 5` o `--resumen` |
| Probar Telegram | `python notificador.py` |

## Cómo ayudar con las pruebas

Seguir `mvp/PRUEBAS.md` fase por fase. El comando `/probar-safecampus` arranca ese recorrido.

- **Las acciones físicas las hacen las personas:** conectar el celular, actuar frente a la cámara, tocar botones. Pedirles una acción a la vez, decir qué deberían ver y esperar a que confirmen.
- **Para ver lo que ve la cámara**, abrir `mvp/data/en_vivo.jpg` (se actualiza cada 0.3 s). Para verificar una alerta, usar `revisar_alertas.py` y abrir la foto de evidencia que indica.
- **Para ajustar sin reiniciar**, escribir solo lo que cambia en `mvp/data/ajustes.yaml` (se combina con `config.yaml`). El modelo, `tamano_imagen` y `fuente` requieren reiniciar la demo. Si un ajuste funciona, pasarlo a `config.yaml`.
- **Anotar resultados** en `docs/resultados-pruebas-AAAA-MM-DD.md` con la plantilla de `PRUEBAS.md`: intentos, alertas correctas, falsas alarmas y tiempos. No inventar resultados: solo lo observado o lo que digan las personas.
- Ante un fallo, seguir la columna "Si falla" de la prueba y cambiar **un parámetro a la vez**.

## Reglas

- **Nunca** pedir que peguen tokens o claves en el chat, ni escribirlos en archivos del repositorio. Telegram (`TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`) y OpenAI (`OPENAI_API_KEY`) se leen de variables de entorno definidas en la terminal antes de abrir Claude.
- No subir al repositorio `mvp/data/`, videos, fotos de personas ni archivos `.pt` (ya están en `.gitignore`).
- Privacidad: el sistema no identifica personas ni usa reconocimiento facial; no agregar nada que lo haga.
- Antes de cambiar código, correr `python -m pytest tests`, y otra vez después. Mantener los cambios pequeños: la demo es en pocos días.
- No hacer push ni commits sin que el equipo lo pida.
