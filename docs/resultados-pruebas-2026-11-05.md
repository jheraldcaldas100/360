# Resultados de pruebas: 2026-11-05

**Estado: ensayo informal, todavía no es la prueba formal de `mvp/PRUEBAS.md`.** El celular estuvo en la mano, no fijo; el umbral de aglomeración se bajó a 2 personas; no hubo las 5 repeticiones; y se usó una banca en vez de una colchoneta.

La clasificación sale de revisar las 10 fotos de evidencia y los datos de `revisar_alertas.py`. No hay un registro de lo que se actuó en cada momento, así que los intentos no se pudieron contar. Las fotos no se suben al repositorio.

- Lugar: patio del campus, de noche
- Celular y app: iPhone con Iriun Webcam 2.9.9, conectado por el hotspot del iPhone
- Laptop (sistema, GPU sí o no): Windows 11, Intel Core i5-1235U, 7.7 GB de RAM, sin GPU dedicada
- fps del detector: 8.5 al arrancar, sin personas en el cuadro; **de 0.5 a 1.4 en las 10 fotos de evidencia** (la guía pide 3 o más)
- Ajustes usados: `fuente: 1` y `resolucion: [1280, 720]` en `config.yaml`. En vivo desde el dashboard: `personas_min: 2` y la zona restringida, activa durante parte del ensayo

| Prueba | Intentos | Alertas correctas | Falsas alarmas | Tiempo hasta la alerta | Notas |
|---|---|---|---|---|---|
| P1 Aglomeración | Sin registrar | 4, con umbral 2 | 0 | 5.3 a 6.6 s | La guía pide umbral 3, así que no cuenta como P1. La alerta #8 fue por gente que pasaba |
| P2 Objeto desatendido | Sin registrar | 1 | 0 | 20.2 s | Es el caso (b). El caso (a), con la persona junto a la mochila, no se pudo verificar |
| P3 Vuelve el dueño | Sin datos | | | | |
| P4 Persona en el suelo | Sin registrar | 0 confirmadas | 3, más 1 dudosa | 5.0 a 6.3 s | Ver "Pendientes", punto 2 |
| P5 Zona restringida | Sin registrar | 1 | 0 | 3.3 s | La guía espera 2 s |
| Flujo del guardia | Parcial | | | Descartada en 13.0 s | Se usó Descartar una vez. Confirmar y Marcar atendida no se usaron |
| Telegram | No realizada | | | | Sin configurar |

## Detalle de las alertas

| # | Hora | Tipo | Tiempo | fps en la foto | Lo que muestra la foto |
|---|---|---|---|---|---|
| 1 | 20:41:55 | Objeto desatendido | 20.2 s | 1.1 | Correcta: mochila sola en el piso |
| 2 | 20:43:37 | Aglomeración | 5.5 s | 0.8 | Correcta con umbral 2: dos personas de pie, muy cerca de la cámara |
| 3 | 20:44:25 | Aglomeración | 5.6 s | 1.0 | Correcta con umbral 2: una persona en la banca y otra sentada detrás |
| 4 | 20:44:25 | Persona en el suelo | 5.6 s | 1.0 | **Falsa:** persona sentada detrás de una mesa, visible solo de la cintura para arriba |
| 5 | 20:44:40 | Aglomeración | 5.3 s | 0.9 | Correcta con umbral 2: cuatro personas |
| 6 | 20:44:44 | Persona en el suelo | 5.3 s | 0.7 | **Falsa:** la misma situación de la #4. La persona recostada en la banca recién iba en 1/5 s |
| 7 | 20:44:48 | Persona en el suelo | 6.3 s | 1.4 | **Dudosa:** la foto muestra un torso muy cerca de la cámara. El tiempo podría venir de la persona recostada en la banca, pero la foto no lo confirma |
| 8 | 20:49:27 | Aglomeración | 6.6 s | 0.5 | Correcta con umbral 2: cuatro personas pasando al fondo |
| 9 | 20:50:10 | Zona restringida | 3.3 s | 0.7 | Correcta: los pies de una persona dentro de la zona |
| 10 | 20:50:50 | Persona en el suelo | 5.0 s | 0.8 | **Falsa:** torso muy cerca de la cámara. Se descartó en el dashboard en 13.0 s |

## Problemas encontrados y cómo se resolvieron

1. **En Windows, el detector se caía a los segundos con el dashboard abierto.** `os.replace` da `PermissionError` si otro proceso está leyendo `en_vivo.jpg`, y ese error detenía toda la demo.
   - Antes del cambio: se cayó a los 20.8 s. En una prueba aparte hubo 0 fallos de 395 escrituras sin lector y 12 de 395 con lector.
   - Solución: `detector.py` reintenta y, si el archivo sigue ocupado, se salta esa imagen.
   - Comprobación: pasan las 34 pruebas; una corrida de 326.5 s con video sintético tuvo 4 colisiones, todas recuperadas; y la demo real corrió unas 3 h 23 min sin ese error. No se sabe si el dashboard estuvo abierto todo ese tiempo.
2. **Iriun no encontraba el iPhone en el wifi de la universidad.** La causa probable es que esa red bloquea la conexión entre equipos, aunque no está confirmado. Con el hotspot del iPhone conectó.
3. **A 640x480, Iriun entrega la imagen con franjas negras de 60 píxeles arriba y abajo.** La imagen terminaba en y=420 y el filtro del borde inferior de `reglas.py` exige y≥470, así que nunca se activaba. Se agregó la opción `resolucion` en `config.yaml`. A 1280x720, 1920x1080 y 640x360 no hay franjas.
4. **`verificar.py` puede dar un verde falso con Iriun (sin resolver).** Iriun envía la pantalla "Looking for the phone" como si fuera video. El primer arranque tardó 8.2 s y el chequeo solo mira 3 s. Hay que confirmar que se ve imagen real.
5. **Si se pierde el iPhone, no hay ningún error (sin resolver).** El detector sigue analizando esa pantalla negra, así que no detecta nada. En el dashboard se ve negra, con un gato.
6. **La demo se detuvo sola a las 23:58 (causa sin confirmar).** El registro dice "Uno de los procesos terminó", sin errores de Python, y no indica cuál fue. Antes hubo 3 cortes de lectura de la cámara y el detector siguió funcionando.
7. **Proyecto dentro de OneDrive.** Se trabajó en `C:\dev\360`, fuera de OneDrive, para no sincronizar el entorno virtual ni las fotos de personas.

## Pendientes para la demo

1. **Subir los fps: es lo más urgente.** Con 1 fps las reglas tienen muy pocas imágenes para decidir, y la causa aún no se conoce.
   - Se midió el ciclo del detector con una foto real, sin cámara ni dashboard, con la laptop a batería y solo 0.7 GB de RAM libres de 7.7 GB. La misma configuración varió de 4.0 a 16.5 fps, así que la medición tiene mucho ruido.

   | Captura | Tamaño de imagen | fps (primera medición) | fps (repetición) |
   |---|---|---|---|
   | 640x480 con franjas | 640 | 3.5 | 5.1 |
   | 1280x720 | 640 | 4.0 | 16.5 |
   | 1280x720 | 480 | 22.9 | |
   | 1280x720 | 320 | 30.3 | |

   - 1280x720 no salió más lento que 640x480, pero esta medición no incluye el dashboard ni el navegador.
   - Siguiente paso: repetir con la demo completa, la laptop enchufada y los demás programas cerrados. Si sigue por debajo de 3 fps, usar `tamano_imagen: 480` y, si hace falta, 320.
2. **Falsas alarmas de persona en el suelo.** Hubo 3 falsas y ninguna alerta correcta confirmada. Aparecieron en dos casos: una persona sentada y tapada por los muebles (su caja queda más ancha que alta) y alguien muy cerca de la cámara mientras se movía el celular. Con el celular fijo debería desaparecer el segundo caso, y hay que encuadrar sin gente sentada al fondo. Falta repetir P4 con la colchoneta.
3. **Hacer la prueba formal.** Con el celular fijo a 1.5 o 2 m y `personas_min: 3`: repetir P1, P2 (b) y P4 (b) 5 veces cada una, y hacer P2 (a), P3, la fase 6 completa y Telegram.
4. **`fuente: 1` solo aplica a esta laptop.** Es el número que Windows le dio a Iriun. En otra computadora puede ser otro y, si no existe esa cámara, el detector no arranca.
5. **Sin probar.** La opción `resolucion` no se ha probado con IP Webcam, DroidCam ni otras cámaras, y estos cambios no se han probado en Mac ni en Linux.
