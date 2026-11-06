# Pasar SafeCampus a la laptop nueva y validar Telegram e IA

Esta guía instala el proyecto en otra laptop y valida las dos funciones que todavía no se probaron: **las alertas por Telegram** y **la descripción con IA**. Está escrita para que la sigan personas o Claude Code en esa laptop.

**Para usarla con Claude:** abran Claude Code en la carpeta del proyecto (`360/`) y escriban:

> Lee `mvp/CONFIGURAR-LAPTOP.md` y guíame fase por fase. Ejecuta tú los comandos, pídeme las acciones físicas de a una y espera mi confirmación. Al final, anota los resultados en `docs/resultados-pruebas-AAAA-MM-DD.md`.

**Reglas que valen para todo:**

- Nunca pegar el token de Telegram ni la clave de OpenAI en el chat, ni guardarlos en archivos del repositorio. Se definen como variables de entorno en la terminal **antes** de abrir Claude.
- Los comandos van para **Windows (PowerShell)**. En Mac o Linux, el intérprete es `.venv/bin/python` en lugar de `.\.venv\Scripts\python.exe`, y las variables se definen con `export`.
- Todo se ejecuta dentro de la carpeta `mvp/`.

---

## Fase A. Antes de empezar, en la laptop vieja

1. Revisar que no quede nada sin subir:
   ```powershell
   git status
   ```
   Si hay cambios importantes (por ejemplo, resultados), subirlos antes con commit y push.
2. **Detener la demo en la laptop vieja.** Si dos computadoras usan el mismo bot de Telegram a la vez, se pisan al recibir los botones: Telegram responde con el error `409 Conflict`.
3. **No copiar** la carpeta `.venv` (no funciona en otra computadora) ni las fotos de `mvp/data/`, que muestran personas. Si de verdad se necesitan, se pasan por USB y no por la nube.

## Fase B. Instalar en la laptop nueva

1. **Instalar Git y Python 3.13** (la versión que funcionó). En Windows, marcar "Add python.exe to PATH" en el instalador.
2. **Ubicar el proyecto fuera de OneDrive**, por ejemplo en `C:\dev`. OneDrive intenta sincronizar miles de archivos del entorno y puede bloquear `en_vivo.jpg`.
3. Clonar la rama del proyecto:
   ```powershell
   mkdir C:\dev; cd C:\dev
   ```
   ```powershell
   git clone --branch claude/festive-archimedes-gfntny https://github.com/jheraldcaldas100/360.git
   ```
   ```powershell
   cd 360\mvp
   ```
4. Configurar su nombre y correo para los commits (en la laptop vieja no estaban configurados):
   ```powershell
   git config --global user.name "Su nombre"
   ```
   ```powershell
   git config --global user.email "su-usuario@users.noreply.github.com"
   ```
5. Crear el entorno e instalar:
   ```powershell
   python -m venv .venv
   ```
   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```
6. Comprobar:
   ```powershell
   .\.venv\Scripts\python.exe -m pytest tests
   ```
   **Aprobado:** `34 passed`.

### B.1 Si la laptop tiene tarjeta gráfica NVIDIA (recomendado revisarlo)

En Windows, `pip` instala PyTorch **solo para CPU**, aunque haya GPU. Con una GPU NVIDIA el detector puede ir mucho más rápido.

1. Revisar si hay GPU NVIDIA:
   ```powershell
   nvidia-smi
   ```
   Si el comando no existe, no hay GPU NVIDIA (o falta su driver): sigan a la fase C.
2. Si existe, entrar a https://pytorch.org/get-started/locally/, elegir Stable, Windows, Pip, Python y la versión de CUDA más reciente que muestre la página, y ejecutar **con el intérprete del entorno** el comando que da la página. Por ejemplo, si la página dice `pip3 install torch torchvision --index-url ...`, ejecutar:
   ```powershell
   .\.venv\Scripts\python.exe -m pip install --force-reinstall torch torchvision --index-url <la URL que da la página>
   ```
3. Comprobar:
   ```powershell
   .\.venv\Scripts\python.exe -c "import torch; print(torch.cuda.is_available())"
   ```
   **Aprobado:** `True`. YOLO usa la GPU automáticamente.

En una Mac con chip Apple, YOLO hoy corre en CPU, porque el código no le pide usar el chip gráfico.

## Fase C. Cámara y rendimiento

1. **Iriun con el iPhone**, igual que en la laptop vieja:
   1. Instalar Iriun Webcam en la laptop y abrirlo.
   2. Activar el hotspot del iPhone y conectar la laptop a esa red. El wifi de la universidad no sirvió.
   3. En Windows: Ajustes → Privacidad y seguridad → Red local → permitir Iriun.
   4. Abrir la app de Iriun en el iPhone, desbloqueado, y comprobar que la imagen aparece en la ventana de Iriun de la laptop.
2. **Saber qué número tiene cada cámara.** En esta laptop puede ser distinto que en la otra:
   ```powershell
   .\.venv\Scripts\python.exe -c "import cv2; [print(i, cv2.VideoCapture(i).read()[0]) for i in range(5)]"
   ```
   Las que dicen `True` abren. La webcam integrada suele ser la `0`. Para saber cuál es el iPhone, comparar con y sin Iriun abierto.
3. Poner ese número en `fuente:` de `config.yaml`. Dejar `resolucion: [1280, 720]`.
4. Chequeo previo:
   ```powershell
   .\.venv\Scripts\python.exe verificar.py --fuente 1
   ```
   **Vale solo si no aparece el aviso de imagen muy oscura.** Si aparece, es la pantalla de espera de Iriun ("Looking for the phone"): esperar unos segundos y repetir.
5. **Medir los fps reales**, que fue el problema de la laptop vieja:
   1. Laptop enchufada y en modo de máximo rendimiento.
   2. Iniciar la demo:
      ```powershell
      .\.venv\Scripts\python.exe iniciar_demo.py --limpiar
      ```
      (Claude debe ejecutarlo en segundo plano.)
   3. Con una persona en el cuadro, leer los fps en la esquina del video, primero **con el dashboard cerrado** y luego con **una sola pestaña** del dashboard abierta.
   4. **Aprobado:** 3 fps o más con el dashboard abierto. Si no llega, poner `tamano_imagen: 480` en `config.yaml`, reiniciar y medir otra vez.

## Fase D. Validar Telegram

### D.1 Crear el bot (unos 10 minutos, en el celular)

1. En Telegram, abrir **@BotFather**, escribir `/newbot`, elegir un nombre y un usuario que termine en `bot`, y **guardar el token** en un lugar privado.
2. Crear un grupo, por ejemplo "Seguridad SafeCampus", agregar al bot y escribir cualquier mensaje.
3. En el navegador, abrir `https://api.telegram.org/bot<TOKEN>/getUpdates` y copiar el número de `"chat":{"id": ...}`. En los grupos es negativo, por ejemplo `-1001234567890`. Si sale vacío, escribir otro mensaje en el grupo y recargar.

### D.2 Definir las variables

**Cerrar Claude**, definir las variables en la terminal y volver a abrir Claude **en esa misma terminal**:

```powershell
$env:TELEGRAM_TOKEN = "123456:ABC..."
```
```powershell
$env:TELEGRAM_CHAT_ID = "-1001234567890"
```
```powershell
claude
```

Estas variables duran mientras la terminal esté abierta. Para no repetirlas cada vez, se pueden guardar para el usuario de Windows con `setx TELEGRAM_TOKEN "..."` y `setx TELEGRAM_CHAT_ID "..."`. En ese caso quedan guardadas en la laptop y solo aplican a terminales que se abran después.

### D.3 Pruebas

| # | Prueba | Cómo | Aprobado si |
|---|---|---|---|
| T1 | Conexión | `.\.venv\Scripts\python.exe verificar.py --fuente 1` | Dice "Telegram listo: el bot puede escribir en «nombre del grupo»" |
| T2 | Mensaje de prueba | `.\.venv\Scripts\python.exe notificador.py` | Llega "Tres60 SafeCampus conectado" al grupo |
| T3 | Alerta con foto | Iniciar la demo y provocar una alerta (ver el truco de abajo) | La alerta llega al grupo **con foto y botones** en menos de 5 s |
| T4 | Confirmar desde Telegram | Tocar "Confirmar" en el mensaje | El mensaje dice "Confirmada por <nombre>" y aparece "Marcar atendida"; en el dashboard la alerta pasa a "Confirmada, por atender", con revisado por "Telegram: <nombre>" |
| T5 | Atender desde Telegram | Tocar "Marcar atendida" | El mensaje dice "Atendida por <nombre>" y el dashboard la muestra atendida, con su tiempo |
| T6 | Descartar desde Telegram | En otra alerta, tocar "Descartar" | Queda descartada en el dashboard |
| T7 | Conflicto | Confirmar una alerta en el **dashboard** y luego tocar un botón de esa alerta en Telegram | Telegram responde "La alerta ya está confirmada (revisada en otro lugar)" |

**Truco para provocar alertas sin un grupo de personas.** Con la demo corriendo, Claude puede crear `data/ajustes.yaml` con:

```yaml
reglas:
  aglomeracion:
    personas_min: 1
    segundos: 3
```

Así, una sola persona frente a la cámara genera una alerta en 3 s. Al reiniciar la demo se vuelve a los valores de `config.yaml`, o se puede borrar el archivo y aplicar desde el dashboard.

Para verificar desde la terminal:

```powershell
.\.venv\Scripts\python.exe revisar_alertas.py -n 3
```

Debe mostrar `revisada en X s por Telegram: <nombre>`.

**Si falla:**

| Síntoma | Causa probable |
|---|---|
| `verificar.py`: "Telegram rechazó el token" | Token mal copiado |
| "El bot no encuentra el chat" | Chat id equivocado, falta el signo menos, o el bot no está en el grupo |
| "Telegram sin configurar" | Las variables no llegaron a esa terminal: definirlas y reabrir Claude ahí |
| Las alertas llegan, pero los botones no hacen nada | Otra computadora corre la demo con el mismo bot (error `409 Conflict` en la consola) |
| "No hay conexión con Telegram" | La red bloquea `api.telegram.org`: usar el hotspot |

## Fase E. Validar la descripción con IA

### E.1 Requisitos

1. **Una clave de API de OpenAI con saldo.** Se crea en https://platform.openai.com/api-keys y el saldo se carga en https://platform.openai.com/settings/organization/billing. **ChatGPT Plus no incluye la API.** Conviene poner un límite de gasto en la misma página de facturación.
2. **Elegir un modelo con visión** (que acepte imágenes) en https://platform.openai.com/docs/models. Para esto conviene uno rápido y económico, porque se llama una vez por alerta.

### E.2 Configurar

1. Definir la clave en la terminal, igual que Telegram (cerrar Claude, definir y reabrir en esa terminal):
   ```powershell
   $env:OPENAI_API_KEY = "sk-..."
   ```
2. En `config.yaml`:
   ```yaml
   ia:
     activa: true
     modelo: "<nombre exacto del modelo elegido>"
   ```
   El nombre del modelo no es secreto: puede quedar en el archivo.
3. Comprobar con `verificar.py --fuente 1`. **Aprobado:** "Descripción con IA configurada (<modelo>)". Esto solo revisa la configuración: todavía no llama a la API.

### E.3 Pruebas

| # | Prueba | Cómo | Aprobado si |
|---|---|---|---|
| I1 | Llamada aislada | El comando de abajo, con una foto cualquiera en la que aparezcan personas que dieron su consentimiento | Imprime una frase que termina en "Coincide: sí", "Coincide: no" o "Coincide: incierto" |
| I2 | En la demo | Provocar una alerta con la demo corriendo | Unos segundos después la consola muestra `[IA] Alerta #N: ...` y la tarjeta del dashboard muestra el recuadro "IA" |
| I3 | En Telegram | Con Telegram activo, la misma alerta | Llega un segundo mensaje: "🤖 IA sobre la alerta #N: ..." |
| I4 | Privacidad | Leer 3 descripciones | No mencionan género, edad, etnia, ropa ni rasgos físicos |
| I5 | Si la IA falla (opcional) | Escribir mal el nombre del modelo en `config.yaml`, reiniciar la demo y provocar una alerta; después dejarlo como estaba. No quiten el wifi: con Iriun por hotspot también se corta la cámara | La alerta sale igual en el dashboard y en Telegram; solo falta la descripción y la consola muestra `[IA] No se pudo describir...` |

Comando para I1 (reemplazar `RUTA.jpg` por la foto):

```powershell
.\.venv\Scripts\python.exe -c "from analizador import cargar_yaml; from ia import configuracion_ia, DescriptorIA; from almacen import Almacen; k, m = configuracion_ia(cargar_yaml('config.yaml')); print('Modelo:', m); print(DescriptorIA(k, m, Almacen('data/prueba_ia.db')).describir('Prueba: persona en el suelo durante 5 s', 'RUTA.jpg'))"
```

**Si falla:**

| Síntoma | Causa probable |
|---|---|
| `HTTP 401` | Clave mal copiada o variable sin definir en esa terminal |
| `HTTP 429` | Sin saldo o se superó el límite de uso |
| `HTTP 400` que menciona el modelo | Nombre del modelo mal escrito, o el modelo no acepta imágenes |
| No da error pero no aparece ninguna descripción | El modelo gastó el límite de 400 tokens razonando y no devolvió texto. Probar otro modelo, o pedirle a Claude que suba `max_output_tokens` en `ia.py` (cambio de código: correr las pruebas antes y después) |
| Tarda más de 10 s | Elegir un modelo más rápido. La alerta no se retrasa, solo la descripción |

## Fase F. Registro

Agregar estas filas a la tabla del archivo de resultados del día (`docs/resultados-pruebas-AAAA-MM-DD.md`), con la plantilla de `PRUEBAS.md`:

| Prueba | Resultado | Tiempo | Notas |
|---|---|---|---|
| Laptop nueva: fps con el dashboard cerrado | | | |
| Laptop nueva: fps con el dashboard abierto | | | |
| GPU usada (sí o no) | | | |
| T1 a T7 Telegram | | | |
| I1 a I5 IA | | | |

Nunca anotar en el repositorio el token, la clave, el chat id ni nombres de personas.
